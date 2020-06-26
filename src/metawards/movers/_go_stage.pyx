
from typing import Union as _Union
from typing import List as _List

cimport cython
from cython.parallel import parallel, prange
from libc.stdint cimport uintptr_t

from libc.math cimport ceil

from .._networks import Networks
from .._infections import Infections
from .._demographics import DemographicID, DemographicIDs

from ..utils._ran_binomial cimport _ran_binomial, \
                                   _get_binomial_ptr, binomial_rng

from ..utils._console import Console

from ..utils._array import create_int_array
from ..utils._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["go_stage", "go_stage_serial", "go_stage_parallel"]

StageID = _Union[str, int]
StageIDs = _List[StageID]


def go_stage_parallel(go_from: _Union[DemographicID, DemographicIDs],
                      go_to: DemographicID,
                      from_stage: _Union[StageID, StageIDs],
                      to_stage: StageID,
                      network: Networks,
                      infections: Infections,
                      nthreads: int,
                      rngs,
                      profiler,
                      fraction: float = 1.0,
                      **kwargs) -> None:
    """This go function will move individuals from the "from_stage"
       stage(s) of the "from" demographic(s) to the "to_stage" stage
       of the "to" demographic. This can move
       a subset of individuals if 'fraction' is less than 1, e.g.
       0.5 would move 50% of individuals (chosen using
       a random binomial distribution)

       Parameters
       ----------
       from: DemographicID or DemographicIDs
         ID (name or index) or IDs of the demographics to scan for
         infected individuals
       to: DemographicID
         ID (name or index) of the isolation demographic to send infected
         individuals to
       from_stage: StageID or StageIDs
         The stage to move from (or list of stages if there are multiple
         from demographics - this is either a stage name or stage index
       to_stage: StageID
         The stage to move to (name or index)
       network: Networks
         The networks to be modelled. This must contain all of the
         demographics that are needed for this go function
       fraction: float or List[float]
         The fraction (percentage) of individuals who are moved.
       rngs:
         Thread-safe random number generators used to choose the fraction
         of individuals
    """

    # make sure that all of the needed demographics exist, and
    # convert them into a canonical form (indexes, list[indexes])
    if not isinstance(go_from, list):
        go_from = [go_from]

    if not isinstance(from_stage, list):
        from_stage = [from_stage] * len(go_from)

    elif len(go_from) != len(from_stage):
        raise ValueError(f"The 'go_from' {go_from} and 'from_stage' "
                         f"{from_stage} values must have the same length")

    if isinstance(go_to, list):
        if len(go_to) != 1:
            raise ValueError(f"The 'go_to' {go_to} must be a single value!")
        go_to = go_to[0]

    if isinstance(network, Networks):
        subnets = network.subnets
        demographics = network.demographics
        subinfs = infections.subinfs

        go_from = [demographics.get_index(x) for x in go_from]

        go_to = demographics.get_index(go_to)

        to_subnet = subnets[go_to]
        to_subinf = subinfs[go_to]
    else:
        if go_from != [0] or go_to != 0:
            raise AssertionError(
                "You cannot change demographics with a single Network")

        subnets = [network]
        subinfs = [infections]
        to_subnet = network
        to_subinf = infections

    fraction = float(fraction)

    if fraction < 0 or fraction > 1:
        raise ValueError(
            f"The move fraction {fraction} should all be 0 to 1")

    to_stage = to_subnet.params.disease_params.get_index(to_stage)

    if len(go_from) != len(from_stage):
        raise ValueError(
                f"Different number of from_stage {len(from_stage)} and "
                f"go_from {len(go_from)}")

    from_stage = [subnets[go_from[i]].params.disease_params.get_index(x)
                  for i, x in enumerate(from_stage)]

    cdef int nnodes_plus_one = 0
    cdef int nlinks_plus_one = 0

    cdef int to_move = 0

    cdef int * work_infections
    cdef int * play_infections

    cdef int * to_work_infections
    cdef int * to_play_infections

    cdef double * links_weight
    cdef double * nodes_save_play_suscept

    cdef double * to_links_weight = get_double_array_ptr(
                                            to_subnet.links.weight)
    cdef double * to_nodes_save_play_suscept = get_double_array_ptr(
                                            to_subnet.nodes.save_play_suscept)

    cdef int nsubnets = len(subnets)

    # get the random number generator
    cdef uintptr_t [::1] rngs_view = rngs
    cdef binomial_rng* rng   # pointer to parallel rng

    cdef int thread_id

    cdef int num_threads = nthreads

    updated = create_int_array(nthreads, 0)
    cdef int * have_updated = get_int_array_ptr(updated)

    cdef int ii = 0
    cdef int i = 0
    cdef int j = 0

    cdef int stage_from = 0
    cdef int stage_to = to_stage

    cdef double frac = fraction

    for ii, stage_from in zip(go_from, from_stage):
        subnet = subnets[ii]
        subinf = subinfs[ii]
        nnodes_plus_one = subinf.nnodes + 1
        nlinks_plus_one = subinf.nlinks + 1

        links_weight = get_double_array_ptr(subnet.links.weight)
        nodes_save_play_suscept = get_double_array_ptr(
                                        subnet.nodes.save_play_suscept)

        work_infections = get_int_array_ptr(subinf.work[stage_from])
        play_infections = get_int_array_ptr(subinf.play[stage_from])

        to_work_infections = get_int_array_ptr(to_subinf.work[stage_to])
        to_play_infections = get_int_array_ptr(to_subinf.play[stage_to])

        Console.debug(f"Move from {subnet.name}:{stage_from} to "
                      f"{to_subnet.name}:{stage_to} with fraction {frac}")

        with nogil, parallel(num_threads=num_threads):
            thread_id = cython.parallel.threadid()

            if frac == 1.0:
                for j in prange(1, nlinks_plus_one, schedule="static"):
                    if work_infections[j] > 0:
                        have_updated[thread_id] = 1
                        to_work_infections[j] = \
                                            to_work_infections[j] + \
                                            work_infections[j]
                        to_links_weight[j] = to_links_weight[j] + \
                                            work_infections[j]
                        links_weight[j] = links_weight[j] - \
                                        work_infections[j]
                        work_infections[j] = 0

                for j in prange(1, nnodes_plus_one, schedule="static"):
                    if play_infections[j] > 0:
                        have_updated[thread_id] = 1
                        to_play_infections[j] = \
                                            to_play_infections[j] + \
                                            play_infections[j]
                        to_nodes_save_play_suscept[j] = \
                                        to_nodes_save_play_suscept[j] + \
                                        play_infections[j]
                        nodes_save_play_suscept[j] = \
                                        nodes_save_play_suscept[j] - \
                                        play_infections[j]
                        play_infections[j] = 0
            else:
                rng = _get_binomial_ptr(rngs_view[thread_id])

                for j in prange(1, nlinks_plus_one, schedule="static"):
                    to_move = _ran_binomial(rng, frac,
                                            <int>(work_infections[j]))

                    if to_move > 0:
                        have_updated[thread_id] = 1
                        to_work_infections[j] = \
                                            to_work_infections[j] + \
                                            to_move
                        work_infections[j] = \
                                            work_infections[j] - \
                                            to_move
                        to_links_weight[j] = to_links_weight[j] + to_move
                        links_weight[j] = links_weight[j] - to_move

                for j in prange(1, nnodes_plus_one, schedule="static"):
                    to_move = _ran_binomial(rng, frac,
                                            <int>(play_infections[j]))

                    if to_move > 0:
                        have_updated[thread_id] = 1
                        to_play_infections[j] = \
                                            to_play_infections[j] + \
                                            to_move
                        play_infections[j] = \
                                            play_infections[j] - \
                                            to_move
                        to_nodes_save_play_suscept[j] = \
                                        to_nodes_save_play_suscept[j] + \
                                        to_move
                        nodes_save_play_suscept[j] = \
                                        nodes_save_play_suscept[j] - \
                                        to_move

    if sum(updated) > 0:
        # we need to recalculate the denominators for the subnets that
        # are involved in this move
        for ii in go_from:
            subnet.recalculate_denominators(profiler=profiler)

        to_subnet.recalculate_denominators(profiler=profiler)


def go_stage_serial(**kwargs) -> None:
    go_stage_parallel(nthreads=1, **kwargs)


def go_stage(nthreads: int = 1, **kwargs) -> None:
    """This go function will move individuals from the "from_stage"
       stage(s) of the "from" demographic(s) to the "to_stage" stage
       of the "to" demographic. This can move
       a subset of individuals if 'fraction' is less than 1, e.g.
       0.5 would move 50% of individuals (chosen using
       a random binomial distribution)

       Parameters
       ----------
       from: DemographicID or DemographicIDs
         ID (name or index) or IDs of the demographics to scan for
         infected individuals
       to: DemographicID
         ID (name or index) of the isolation demographic to send infected
         individuals to
       from_stage: int or list[int]
         The stage to move from (or list of stages if there are multiple
         from demographics)
       to_stage: int
         The stage to move to
       network: Networks
         The networks to be modelled. This must contain all of the
         demographics that are needed for this go function
       fraction: float or List[float]
         The fraction (percentage) of individuals who are moved.
       rngs:
         Thread-safe random number generators used to choose the fraction
         of individuals
    """
    if nthreads > 1:
        go_stage_parallel(nthreads=nthreads, **kwargs)
    else:
        go_stage_serial(**kwargs)
