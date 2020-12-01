
from typing import Union as _Union
from typing import List as _List

cimport cython
from cython.parallel import parallel, prange
from libc.stdint cimport uintptr_t

from libc.math cimport ceil

from .._network import Network, PersonType
from .._networks import Networks
from .._infections import Infections

from ..utils._ran_binomial cimport _ran_binomial, \
                                   _get_binomial_ptr, binomial_rng

from ..utils._console import Console

from ..utils._array import create_int_array
from ..utils._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

from ._movegenerator import MoveGenerator
from ._moverecord import MoveRecord

__all__ = ["go_ward"]


def go_ward(generator: MoveGenerator,
            network: _Union[Network, Networks],
            infections: Infections,
            rngs,
            nthreads: int = 1,
            record: MoveRecord = None,
            **kwargs) -> None:
    """This go function will move individuals according to the flexible
       move specification described by the passed 'generator'.

       If you want a record of all moves, then pass in 'record',
       which will be updated.

       Parameters
       ----------
       generator: MoveGenerator
         Fully describes all of the moves that should be performed
       network: Network or Networks
         The network(s) in which the individuals will be moved
       infections: Infections
         Current record of infections
       nthreads: int
         Number of threads over which to parallelise the move
       rngs:
         Thread-safe random number generators used to choose the fraction
         of individuals
       record: MoveRecord
         An optional record to which to record the moves that are performed
    """
    # get the demographic/stage moves, plus the ward-level moves
    stages = generator.generate(network)
    wards = generator.generate_wards(network)

    if isinstance(network, Network):
        subnets = [network]
        subinfs = [infections]
    else:
        subnets = network.subnets
        subinfs = infections.subinfs

    cdef int from_stage = 0
    cdef int to_stage = 0

    cdef int number = 0
    cdef double fraction = 0.0

    cdef int nnodes_plus_one = subnets[0].nnodes + 1
    cdef int nlinks_plus_one = subnets[0].nlinks + 1

    cdef int * to_work_infections
    cdef int * from_work_infections

    cdef int * to_play_infections
    cdef int * from_play_infections

    cdef double * from_links_weight
    cdef double * to_links_weight

    cdef double * from_links_suscept
    cdef double * to_links_suscept

    cdef double * from_play_suscept
    cdef double * to_play_suscept

    cdef double * from_save_play_suscept
    cdef double * to_save_play_suscept

    cdef int num_threads = nthreads
    cdef int thread_id = 0

    # get the random number generator
    cdef uintptr_t [::1] rngs_view = rngs
    cdef binomial_rng* rng   # pointer to parallel rng

    updated = create_int_array(nthreads, 0)
    cdef int * have_updated = get_int_array_ptr(updated)

    cdef int i = 0
    cdef int nmove = 0

    cdef int record_moves = 1

    if record is None:
        record_moves = 0

    affected_subnets = {}

    worker = PersonType.WORKER
    player = PersonType.PLAYER

    cdef int is_worker = 0
    cdef int is_player = 0
    cdef int ifrom = 0
    cdef int ifrom_begin = 0
    cdef int ifrom_end = 0
    cdef int ito = 0
    cdef int ito_begin = 0
    cdef int ito_end = 0
    cdef int ito_delta = 0
    cdef int move_ward_only = 0

    for stage in stages:
        fraction = generator.fraction()
        number = generator.number()

        if fraction == 0.0 or number == 0:
            continue

        from_net = subnets[stage[0]]
        from_infs = subinfs[stage[0]]
        from_stage = stage[1]
        to_net = subnets[stage[2]]
        to_infs = subinfs[stage[2]]
        to_stage = stage[3]

        from_links_weight = get_double_array_ptr(from_net.links.weight)
        to_links_weight = get_double_array_ptr(to_net.links.weight)

        from_save_play_suscept = get_double_array_ptr(
                                        from_net.nodes.save_play_suscept)
        to_save_play_suscept = get_double_array_ptr(
                                        to_net.nodes.save_play_suscept)

        if from_stage >= 0:
            from_work_infections = get_int_array_ptr(
                                            from_infs.work[from_stage])
            from_play_infections = get_int_array_ptr(
                                            from_infs.play[from_stage])
        else:
            from_links_suscept = get_double_array_ptr(
                                            from_net.links.suscept)
            from_play_suscept = get_double_array_ptr(
                                            from_net.nodes.play_suscept)

        if to_stage >= 0:
            to_work_infections = get_int_array_ptr(
                                            to_infs.work[to_stage])
            to_play_infections = get_int_array_ptr(
                                            to_infs.play[to_stage])
        else:
            to_links_suscept = get_double_array_ptr(
                                            to_net.links.suscept)
            to_play_suscept = get_double_array_ptr(
                                            to_net.nodes.play_suscept)

        if generator.should_move_all():
            if stage[0] == stage[2] and stage[1] == stage[3]:
                # nothing to move
                continue

            with nogil, parallel(num_threads=num_threads):
                thread_id = cython.parallel.threadid()
                rng = _get_binomial_ptr(rngs_view[thread_id])

                # loop over workers
                for i in prange(1, nlinks_plus_one, schedule="static"):
                    if from_stage >= 0:
                        nmove = min(number, from_work_infections[i])
                    else:
                        nmove = min(number, <int>from_links_suscept[i])

                    if fraction != 1.0:
                        nmove = _ran_binomial(rng, fraction, nmove)

                    if nmove > 0:
                        have_updated[thread_id] = 1

                        if record_moves:
                            with gil:
                                record.add(from_demographic=stage[0],
                                           to_demographic=stage[2],
                                           from_stage=from_stage,
                                           to_stage=to_stage,
                                           from_type=worker,
                                           to_type=worker,
                                           from_ward=i,
                                           to_ward=i,
                                           number=nmove
                                           )

                        if to_stage >= 0:
                            to_work_infections[i] = \
                                            to_work_infections[i] + nmove
                        else:
                            to_links_suscept[i] = \
                                                to_links_suscept[i] + nmove

                        if from_stage >= 0:
                            from_work_infections[i] = \
                                            from_work_infections[i] - nmove
                        else:
                            from_links_suscept[i] = \
                                            from_links_suscept[i] - nmove

                        to_links_weight[i] = to_links_weight[i] + nmove
                        from_links_weight[i] = from_links_weight[i] - nmove
                # end of loop over workers

                # loop over players
                for i in prange(1, nnodes_plus_one, schedule="static"):
                    if from_stage >= 0:
                        nmove = min(number, from_play_infections[i])
                    else:
                        nmove = min(number, <int>from_play_suscept[i])

                    if fraction != 1.0:
                        nmove = _ran_binomial(rng, fraction, nmove)

                    if nmove > 0:
                        have_updated[thread_id] = 1

                        if record_moves:
                            with gil:
                                record.add(from_demographic=stage[0],
                                           to_demographic=stage[2],
                                           from_stage=from_stage,
                                           to_stage=to_stage,
                                           from_type=player,
                                           to_type=player,
                                           from_ward=i,
                                           to_ward=i,
                                           number=nmove
                                           )

                        if to_stage >= 0:
                            to_play_infections[i] = \
                                        to_play_infections[i] + nmove
                        else:
                            to_play_suscept[i] = \
                                        to_play_suscept[i] + nmove

                        if from_stage >= 0:
                            from_play_infections[i] = \
                                    from_play_infections[i] - nmove
                        else:
                            from_play_suscept[i] = \
                                    from_play_suscept[i] - nmove

                        to_save_play_suscept[i] = \
                                    to_save_play_suscept[i] + nmove
                        from_save_play_suscept[i] = \
                                    from_save_play_suscept[i] - nmove
                # end of loop over players
            # end of parallel section
        # end of if should move all
        else:
            if stage[0] == stage[2] and stage[1] == stage[3]:
                move_ward_only = 1
            else:
                move_ward_only = 0

            if move_ward_only and len(wards) == 0:
                # nothing to move
                continue

            for ward in wards:
                if ward[0] is None:
                    # everyone will move to 'to_ward'
                    to_type = ward[1][0]
                    ito_begin = ward[1][1]
                    ito_end = ward[1][2]

                    if ito_end - ito_begin != 1:
                        # cannot move everyone to multiple ids!
                        raise ValueError(
                            "Cannot move all individuals to multiple links")

                    ito = ito_begin

                    if to_type == worker:
                        is_worker = 1
                        is_player = 0
                    elif to_type == player:
                        is_worker = 0
                        is_player = 1
                    else:
                        raise NotImplementedError(
                                f"Unknown PersonType: {from_type}")

                    with nogil:
                        thread_id = cython.parallel.threadid()
                        rng = _get_binomial_ptr(rngs_view[thread_id])

                        # loop over workers (cannot be parallel)
                        for i in range(1, nlinks_plus_one):
                            if move_ward_only and is_worker and i == ito:
                                continue

                            if from_stage >= 0:
                                nmove = min(number, from_work_infections[i])
                            else:
                                nmove = min(number, <int>from_links_suscept[i])

                            if fraction != 1.0:
                                nmove = _ran_binomial(rng, fraction, nmove)

                            if nmove > 0:
                                have_updated[thread_id] = 1

                                if record_moves:
                                    with gil:
                                        record.add(from_demographic=stage[0],
                                                   to_demographic=stage[2],
                                                   from_stage=from_stage,
                                                   to_stage=to_stage,
                                                   from_type=worker,
                                                   to_type=to_type,
                                                   from_ward=i,
                                                   to_ward=ito,
                                                   number=nmove
                                                  )

                                if is_worker:
                                    if to_stage >= 0:
                                        to_work_infections[ito] = \
                                            to_work_infections[ito] + nmove
                                    else:
                                        to_links_suscept[ito] = \
                                            to_links_suscept[ito] + nmove

                                    to_links_weight[ito] = \
                                            to_links_weight[ito] + nmove
                                elif is_player:
                                    if to_stage >= 0:
                                        to_play_infections[ito] = \
                                            to_play_infections[ito] + nmove
                                    else:
                                        to_play_suscept[ito] = \
                                            to_play_suscept[ito] + nmove

                                    to_save_play_suscept[ito] = \
                                            to_save_play_suscept[ito] + nmove

                                if from_stage >= 0:
                                    from_work_infections[i] = \
                                            from_work_infections[i] - nmove
                                else:
                                    from_links_suscept[i] = \
                                            from_links_suscept[i] - nmove

                                from_links_weight[i] = \
                                            from_links_weight[i] - nmove
                        # end of loop over workers

                        # loop over players - cannot be parallel
                        for i in range(1, nnodes_plus_one):
                            if move_ward_only and is_player and i == ito:
                                continue

                            if from_stage >= 0:
                                nmove = min(number, from_play_infections[i])
                            else:
                                nmove = min(number, <int>from_play_suscept[i])

                            if fraction != 1.0:
                                nmove = _ran_binomial(rng, fraction, nmove)

                            if nmove > 0:
                                have_updated[thread_id] = 1

                                if record_moves:
                                    with gil:
                                        record.add(from_demographic=stage[0],
                                                   to_demographic=stage[2],
                                                   from_stage=from_stage,
                                                   to_stage=to_stage,
                                                   from_type=player,
                                                   to_type=to_type,
                                                   from_ward=i,
                                                   to_ward=ito,
                                                   number=nmove
                                                  )

                                if is_worker:
                                    if to_stage >= 0:
                                        to_work_infections[ito] = \
                                            to_work_infections[ito] + nmove
                                    else:
                                        to_links_suscept[ito] = \
                                            to_links_suscept[ito] + nmove

                                    to_links_weight[ito] = \
                                            to_links_weight[ito] + nmove
                                elif is_player:
                                    if to_stage >= 0:
                                        to_play_infections[ito] = \
                                            to_play_infections[ito] + nmove
                                    else:
                                        to_play_suscept[ito] = \
                                            to_play_suscept[ito] + nmove
                                    to_save_play_suscept[ito] = \
                                            to_save_play_suscept[ito] + nmove

                                if from_stage >= 0:
                                    from_play_infections[i] = \
                                            from_play_infections[i] - nmove
                                else:
                                    from_play_suscept[i] = \
                                            from_play_suscept[i] - nmove

                                from_save_play_suscept[i] = \
                                            from_save_play_suscept[i] - nmove
                        # end of loop over players
                    # end of parallel section
                # end of from_type is None (move all wards)
                else:
                    # this cannot run in parallel
                    rng = _get_binomial_ptr(rngs_view[0])

                    from_type = ward[0][0]
                    ifrom_begin = ward[0][1]
                    ifrom_end = ward[0][2]
                    to_type = ward[1][0]
                    ito_begin = ward[1][1]
                    ito_end = ward[1][2]

                    if move_ward_only and from_type == to_type and \
                      ifrom_begin == ito_begin and ifrom_end == ito_end:
                        # nothing to move
                        continue

                    if ito_end - ito_begin == 0:
                        raise ValueError(
                            "Cannot move individuals to a non-existent "
                            "ward or ward-link")
                    elif ito_end - ito_begin == 1:
                        # this is a single to-ward (or link)
                        ito_delta = 0
                    elif ito_end - ito_begin != ifrom_end - ifrom_begin:
                        # different number of links
                        raise ValueError(
                            "Cannot move individuals as the number of from "
                            "and to links are not the same: "
                            f"{ifrom_begin}:{ifrom_end} versus "
                            f"{ito_begin}:{ito_end}")
                    else:
                        ito_delta = 1

                    # cannot be parallel
                    for i in range(0, ifrom_end-ifrom_begin):
                        ifrom = ifrom_begin + i
                        ito = ito_begin + (i * ito_delta)

                        if from_type == worker:
                            if from_stage >= 0:
                                nmove = min(number,
                                            from_work_infections[ifrom])
                            else:
                                nmove = min(number,
                                            <int>from_links_suscept[ifrom])
                        elif from_type == player:
                            if from_stage >= 0:
                                nmove = min(number,
                                            from_play_infections[ifrom])
                            else:
                                nmove = min(number,
                                            <int>from_play_suscept[ifrom])
                        else:
                            raise NotImplementedError(
                                    f"Unknown PersonType: {from_type}")

                        if fraction != 1.0:
                            nmove = _ran_binomial(rng, fraction, nmove)

                        if nmove > 0:
                            have_updated[0] = 1

                            if to_type == worker:
                                if to_stage >= 0:
                                    to_work_infections[ito] = \
                                            to_work_infections[ito] + nmove
                                else:
                                    to_links_suscept[ito] = \
                                            to_links_suscept[ito] + nmove

                                to_links_weight[ito] = \
                                        to_links_weight[ito] + nmove
                            elif to_type == player:
                                if to_stage >= 0:
                                    to_play_infections[ito] = \
                                        to_play_infections[ito] + nmove
                                else:
                                    to_play_suscept[ito] = \
                                       to_play_suscept[ito] + nmove

                                to_save_play_suscept[ito] = \
                                        to_save_play_suscept[ito] + nmove
                            else:
                                raise NotImplementedError(
                                        f"Unknown PersonType: {to_type}")

                            if from_type == worker:
                                if from_stage >= 0:
                                    from_work_infections[ifrom] = \
                                        from_work_infections[ifrom] - nmove
                                else:
                                    from_links_suscept[ifrom] = \
                                        from_links_suscept[ifrom] - nmove

                                from_links_weight[ifrom] = \
                                        from_links_weight[ifrom] - nmove
                            else:
                                if from_stage >= 0:
                                    from_play_infections[ifrom] = \
                                        from_play_infections[ifrom] - nmove
                                else:
                                    from_play_suscept[ifrom] = \
                                        from_play_suscept[ifrom] - nmove

                                from_save_play_suscept[ifrom] = \
                                        from_save_play_suscept[ifrom] - nmove

                            if record_moves:
                                record.add(from_demographic=stage[0],
                                           to_demographic=stage[2],
                                           from_stage=from_stage,
                                           to_stage=to_stage,
                                           from_type=from_type,
                                           to_type=to_type,
                                           from_ward=ifrom,
                                           to_ward=ito,
                                           number=nmove
                                          )
                        # end of from i in range(0, end-begin)
                    # end of if nmove > 0
                # end of if from_type is None (test move all wards)
            # end of loop over wards
        #end of else (if should move all)

        if sum(updated) > 0:
            # record any subnets that changed at this stage
            affected_subnets[stage[0]] = 1
            affected_subnets[stage[2]] = 1

            for i in range(0, len(updated)):
                updated[i] = 0

    # end of loop over stages

    # we need to recalculate the denominators for the subnets that
    # were changed by this move
    for i in affected_subnets.keys():
        subnets[i].recalculate_denominators()
