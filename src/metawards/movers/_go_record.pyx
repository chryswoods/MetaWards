
from typing import Union as _Union
from typing import List as _List

from .._network import Network, PersonType
from .._networks import Networks
from .._infections import Infections

from ..utils._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

from ._moverecord import MoveRecord

__all__ = ["go_record"]


def go_record(moves: MoveRecord,
              network: _Union[Network, Networks],
              infections: Infections,
              record: MoveRecord = None,
              **kwargs) -> None:
    """This go function will perform all (or as many possible) moves
       from the passed 'moves' MoveRecord. This will move specific
       individuals between specific demographics, stages and
       ward(s) / ward link(s).

       If you want a record of all moves, then pass in 'record',
       which will be updated.

       Parameters
       ----------
       moves: MoveRecord
         Fully describes all of the moves that should be performed
       network: Network or Networks
         The network(s) in which the individuals will be moved
       infections: Infections
         Current record of infections
       record: MoveRecord
         An optional record to which to record the moves that are performed
    """
    if isinstance(network, Network):
        subnets = [network]
        subinfs = [infections]
    else:
        subnets = network.subnets
        subinfs = infections.subinfs

    cdef int from_demo = 0
    cdef int to_demo = 0

    cdef int from_stage = 0
    cdef int to_stage = 0

    cdef int from_ward = 0
    cdef int to_ward = 0

    cdef int number = 0

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

    cdef int record_moves = 1

    if record is None:
        record_moves = 0

    affected_subnets = {}

    worker = PersonType.WORKER
    player = PersonType.PLAYER

    cdef int ifrom = 0
    cdef int ito = 0

    cdef int nmove = 0

    for move in moves:
        (from_demo, from_stage, from_type, from_ward,
         to_demo, to_stage, to_type, to_ward, number) = move

        if number <= 0:
            continue

        if from_demo < 0 or from_demo >= len(subnets):
            raise ValueError(f"Invalid from demographic: {from_demo}")
        elif to_demo < 0 or to_demo >= len(subnets):
            raise ValueError(f"Invaild to demographic: {to_demo}")

        from_net = subnets[from_demo]
        from_infs = subinfs[from_demo]
        to_net = subnets[to_demo]
        to_infs = subinfs[to_demo]

        if from_stage < -1 or \
          from_stage >= from_net.params.disease_params.N_INF_CLASSES():
            raise ValueError(f"Invalid from stage: {from_stage}")
        elif to_stage < -1 or \
          to_stage >= to_net.params.disease_params.N_INF_CLASSES():
            raise ValueError(f"Invalid to stage: {from_stage}")

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

        if from_demo == to_demo and from_stage == to_stage and \
          from_type == to_type and from_ward == to_ward:
            # nothing to do
            continue

        ifrom = from_ward
        ito = to_ward

        from_type = PersonType(from_type)
        to_type = PersonType(to_type)

        if from_type == worker:
            if from_stage >= 0:
                nmove = min(number, from_work_infections[ifrom])
            else:
                nmove = min(number, <int>from_links_suscept[ifrom])
        elif from_type == player:
            if from_stage >= 0:
                nmove = min(number, from_play_infections[ifrom])
            else:
                nmove = min(number, <int>from_play_suscept[ifrom])
        else:
            raise NotImplementedError(
                    f"Unknown PersonType: {from_type}")

        if nmove > 0:
            if to_type == worker:
                if to_stage >= 0:
                    to_work_infections[ito] = \
                            to_work_infections[ito] + nmove
                else:
                    to_links_suscept[ito] = \
                            to_links_suscept[ito] + nmove

                to_links_weight[ito] = to_links_weight[ito] + nmove
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

            affected_subnets[from_demo] = 1
            affected_subnets[to_demo] = 1

            if record_moves:
                record.add(from_demographic=from_demo,
                           to_demographic=to_demo,
                           from_stage=from_stage,
                           to_stage=to_stage,
                           from_type=from_type,
                           to_type=to_type,
                           from_ward=ifrom,
                           to_ward=ito,
                           number=nmove
                          )
            # end if record moves
        # end if nmove > 0
    # end of loop over stages

    # we need to recalculate the denominators for the subnets that
    # were changed by this move
    for i in affected_subnets.keys():
        subnets[i].recalculate_denominators()
