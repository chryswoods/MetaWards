
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

from ..utils._array import create_int_array
from ..utils._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["go_isolate", "go_isolate_serial", "go_isolate_parallel"]


def go_isolate_parallel(go_from: _Union[DemographicID, DemographicIDs],
                        go_to: DemographicID,
                        network: Networks,
                        infections: Infections,
                        nthreads: int,
                        rngs,
                        profiler,
                        self_isolate_stage: _Union[_List[int], int] = 2,
                        fraction: _Union[_List[float], float] = 1.0,
                        **kwargs) -> None:
    """This go function will move individuals from the "from"
       demographic(s) to the "to" demographic if they show any
       signs of infection (the disease stage is greater or equal
       to 'self_isolate_stage' - by default this is level '2',
       which is one level above "latent"). This can move
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
       network: Networks
         The networks to be modelled. This must contain all of the
         demographics that are needed for this go function
       self_isolate_stage: int or List[int]
         The stage of infection an individual must be at before they
         are moved into this demographic. If a list is passed then
         this can be multiple stages, e.g. [2, 3] will move at
         stages 2 and 3. Multiple stages are needed if only
         a fraction of individuals move.
       fraction: float or List[float]
         The fraction (percentage) of individuals who are moved from
         this stage into isolation. If this is a single value then
         the same fraction applies to all self_isolation_stages. Otherwise,
         the fraction for self_isolate_stage[i] is fraction[i]
       rngs:
         Thread-safe random number generators used to choose the fraction
         of individuals
    """

    # make sure that all of the needed demographics exist, and
    # convert them into a canonical form (indexes, list[indexes])
    if not isinstance(go_from, list):
        go_from = [go_from]

    subnets = network.subnets
    demographics = network.demographics
    subinfs = infections.subinfs

    go_from = [demographics.get_index(x) for x in go_from]

    go_to = demographics.get_index(go_to)

    to_subnet = subnets[go_to]
    to_subinf = subinfs[go_to]

    if isinstance(self_isolate_stage, list):
        stages = [int(stage) for stage in self_isolate_stage]
    else:
        stages = [int(self_isolate_stage)]

    if isinstance(fraction, list):
        fractions = [float(frac) for frac in fraction]
    else:
        fractions = [float(fraction)] * len(stages)

    for fraction in fractions:
        if fraction < 0 or fraction > 1:
            raise ValueError(
                f"The move fractions {fractions} should all be 0 to 1")

    N_INF_CLASSES = infections.N_INF_CLASSES

    for stage in stages:
        if stage < 1 or stage >= N_INF_CLASSES:
            raise ValueError(
                f"The stage(s) of self-isolation {stages} "
                f"is invalid for a disease with {N_INF_CLASSES} stages")

    if len(stages) != len(fractions):
        raise ValueError(
            f"The number of self isolation stages {stages} must equal "
            f"the number of fractions {fractions}")

    cdef int nnodes_plus_one = 0
    cdef int nlinks_plus_one = 0

    cdef int to_move = 0

    cdef int * work_infections_i
    cdef int * play_infections_i

    cdef int * to_work_infections_i
    cdef int * to_play_infections_i

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

    cdef double fraction_i = 1.0

    for ii in go_from:
        subnet = subnets[ii]
        subinf = subinfs[ii]
        nnodes_plus_one = subinf.nnodes + 1
        nlinks_plus_one = subinf.nlinks + 1

        links_weight = get_double_array_ptr(subnet.links.weight)
        nodes_save_play_suscept = get_double_array_ptr(
                                        subnet.nodes.save_play_suscept)

        for i, fraction in zip(stages, fractions):
            fraction_i = fraction

            work_infections_i = get_int_array_ptr(subinf.work[i])
            play_infections_i = get_int_array_ptr(subinf.play[i])

            to_work_infections_i = get_int_array_ptr(to_subinf.work[i])
            to_play_infections_i = get_int_array_ptr(to_subinf.play[i])

            with nogil, parallel(num_threads=num_threads):
                thread_id = cython.parallel.threadid()

                if fraction_i == 1.0:
                    for j in prange(1, nlinks_plus_one, schedule="static"):
                        if work_infections_i[j] > 0:
                            have_updated[thread_id] = 1
                            to_work_infections_i[j] = \
                                                to_work_infections_i[j] + \
                                                work_infections_i[j]
                            to_links_weight[j] = to_links_weight[j] + \
                                                work_infections_i[j]
                            links_weight[j] = links_weight[j] - \
                                            work_infections_i[j]
                            work_infections_i[j] = 0

                    for j in prange(1, nnodes_plus_one, schedule="static"):
                        if play_infections_i[j] > 0:
                            have_updated[thread_id] = 1
                            to_play_infections_i[j] = \
                                                to_play_infections_i[j] + \
                                                play_infections_i[j]
                            to_nodes_save_play_suscept[j] = \
                                            to_nodes_save_play_suscept[j] + \
                                            play_infections_i[j]
                            nodes_save_play_suscept[j] = \
                                            nodes_save_play_suscept[j] - \
                                            play_infections_i[j]
                            play_infections_i[j] = 0
                else:
                    rng = _get_binomial_ptr(rngs_view[thread_id])

                    for j in prange(1, nlinks_plus_one, schedule="static"):
                        to_move = _ran_binomial(rng, fraction_i,
                                                <int>(work_infections_i[j]))

                        if to_move > 0:
                            have_updated[thread_id] = 1
                            to_work_infections_i[j] = \
                                                to_work_infections_i[j] + \
                                                to_move
                            work_infections_i[j] = \
                                                work_infections_i[j] - \
                                                to_move
                            to_links_weight[j] = to_links_weight[j] + to_move
                            links_weight[j] = links_weight[j] - to_move

                    for j in prange(1, nnodes_plus_one, schedule="static"):
                        to_move = _ran_binomial(rng, fraction_i,
                                                <int>(play_infections_i[j]))

                        if to_move > 0:
                            have_updated[thread_id] = 1
                            to_play_infections_i[j] = \
                                                to_play_infections_i[j] + \
                                                to_move
                            play_infections_i[j] = \
                                                play_infections_i[j] - \
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


def go_isolate_serial(go_from: _Union[DemographicID, DemographicIDs],
                      go_to: DemographicID,
                      network: Networks,
                      infections: Infections,
                      rngs,
                      profiler,
                      self_isolate_stage: _Union[_List[int], int] = 2,
                      fraction: _Union[_List[float], float] = 1.0,
                      **kwargs) -> None:
    """This go function will move individuals from the "from"
       demographic(s) to the "to" demographic if they show any
       signs of infection (the disease stage is greater or equal
       to 'self_isolate_stage' - by default this is level '2',
       which is one level above "latent"). This can move
       a subset of individuals if 'fraction' is less than 1, e.g.
       0.5 would move 50% of individuals (chosen using
       a random binomial distribution)

       Parameters
       ----------
       from: DemographicID or DemographicIDs
         ID (name or index) or IDs of the demographics to scan for
         infected individuals
       to: DemographicID
         ID (name or index) of the demographic to send infected
         individuals to
       network: Networks
         The networks to be modelled. This must contain all of the
         demographics that are needed for this go function
       self_isolate_stage: int or List[int]
         The stage of infection an individual must be at before they
         are moved into this demographic. If a list is passed then
         this can be multiple stages, e.g. [2, 3] will move at
         stages 2 and 3. Multiple stages are needed if only
         a fraction of individuals move.
       fraction: float or List[float]
         The fraction (percentage) of individuals who are moved from
         this stage into isolation. If this is a single value then
         the same fraction applies to all self_isolation_stages. Otherwise,
         the fraction for self_isolate_stage[i] is fraction[i]
       rngs:
         Thread-safe random number generators used to choose the fraction
         of individuals
    """

    # make sure that all of the needed demographics exist, and
    # convert them into a canonical form (indexes, list[indexes])
    if not isinstance(go_from, list):
        go_from = [go_from]

    subnets = network.subnets
    demographics = network.demographics
    subinfs = infections.subinfs

    go_from = [demographics.get_index(x) for x in go_from]

    go_to = demographics.get_index(go_to)

    to_subnet = subnets[go_to]
    to_subinf = subinfs[go_to]

    if isinstance(self_isolate_stage, list):
        stages = [int(stage) for stage in self_isolate_stage]
    else:
        stages = [int(self_isolate_stage)]

    if isinstance(fraction, list):
        fractions = [float(frac) for frac in fraction]
    else:
        fractions = [float(fraction)] * len(stages)

    for fraction in fractions:
        if fraction < 0 or fraction > 1:
            raise ValueError(
                f"The move fractions {fractions} should all be 0 to 1")

    N_INF_CLASSES = infections.N_INF_CLASSES

    for stage in stages:
        if stage < 1 or stage >= N_INF_CLASSES:
            raise ValueError(
                f"The stage(s) of self-isolation {stages} "
                f"is invalid for a disease with {N_INF_CLASSES} stages")

    if len(stages) != len(fractions):
        raise ValueError(
            f"The number of self isolation stages {stages} must equal "
            f"the number of fractions {fractions}")

    cdef int nnodes_plus_one = 0
    cdef int nlinks_plus_one = 0

    cdef int to_move = 0

    cdef int * work_infections_i
    cdef int * play_infections_i

    cdef int * to_work_infections_i
    cdef int * to_play_infections_i

    cdef double * links_weight
    cdef double * nodes_save_play_suscept

    cdef double * to_links_weight = get_double_array_ptr(
                                            to_subnet.links.weight)
    cdef double * to_nodes_save_play_suscept = get_double_array_ptr(
                                            to_subnet.nodes.save_play_suscept)

    cdef int nsubnets = len(subnets)

    cdef int have_updated = 0

    cdef int ii = 0
    cdef int i = 0
    cdef int j = 0

    # get the random number generator
    cdef binomial_rng* rng = _get_binomial_ptr(rngs[0])

    cdef double fraction_i = 1.0

    for ii in go_from:
        subnet = subnets[ii]
        subinf = subinfs[ii]
        nnodes_plus_one = subinf.nnodes + 1
        nlinks_plus_one = subinf.nlinks + 1

        links_weight = get_double_array_ptr(subnet.links.weight)
        nodes_save_play_suscept = get_double_array_ptr(
                                        subnet.nodes.save_play_suscept)

        for i, fraction in zip(stages, fractions):
            fraction_i = fraction

            work_infections_i = get_int_array_ptr(subinf.work[i])
            play_infections_i = get_int_array_ptr(subinf.play[i])

            to_work_infections_i = get_int_array_ptr(to_subinf.work[i])
            to_play_infections_i = get_int_array_ptr(to_subinf.play[i])

            if fraction_i == 1.0:
                for j in range(1, nlinks_plus_one):
                    if work_infections_i[j] > 0:
                        have_updated = 1
                        to_work_infections_i[j] = to_work_infections_i[j] + \
                                                  work_infections_i[j]
                        to_links_weight[j] = to_links_weight[j] + \
                                             work_infections_i[j]
                        links_weight[j] = links_weight[j] - \
                                          work_infections_i[j]
                        work_infections_i[j] = 0

                for j in range(1, nnodes_plus_one):
                    if play_infections_i[j] > 0:
                        have_updated = 1
                        to_play_infections_i[j] = to_play_infections_i[j] + \
                                                  play_infections_i[j]
                        to_nodes_save_play_suscept[j] = \
                                        to_nodes_save_play_suscept[j] + \
                                        play_infections_i[j]
                        nodes_save_play_suscept[j] = \
                                        nodes_save_play_suscept[j] - \
                                        play_infections_i[j]
                        play_infections_i[j] = 0
            else:
                for j in range(1, nlinks_plus_one):
                    to_move = _ran_binomial(rng, fraction_i,
                                            <int>(work_infections_i[j]))
                    if to_move > 0:
                        have_updated = 1
                        to_work_infections_i[j] = to_work_infections_i[j] + \
                                                  to_move
                        work_infections_i[j] = work_infections_i[j] - \
                                               to_move
                        to_links_weight[j] = to_links_weight[j] + to_move
                        links_weight[j] = links_weight[j] - to_move

                for j in range(1, nnodes_plus_one):
                    to_move = _ran_binomial(rng, fraction_i,
                                            <int>(play_infections_i[j]))
                    if to_move > 0:
                        have_updated = 1
                        to_play_infections_i[j] = to_play_infections_i[j] + \
                                                  to_move
                        play_infections_i[j] = play_infections_i[j] - \
                                               to_move
                        to_nodes_save_play_suscept[j] = \
                                            to_nodes_save_play_suscept[j] + \
                                            to_move
                        nodes_save_play_suscept[j] = \
                                            nodes_save_play_suscept[j] - \
                                            to_move

    if have_updated > 0:
        # we need to recalculate the denominators for the subnets that
        # are involved in this move
        for ii in go_from:
            subnet.recalculate_denominators(profiler=profiler)

        to_subnet.recalculate_denominators(profiler=profiler)


def go_isolate(nthreads: int = 1, **kwargs) -> None:
    """This go function will move individuals from the "from"
       demographic(s) to the "to" demographic if they show any
       signs of infection (the disease stage is greater or equal
       to 'self_isolate_stage' - by default this is level '2',
       which is one level above "latent"). Individuals are held
       in the new demographic for "duration" days, before being
       returned either to their original demographic, or
       released to the "release_to" demographic

       Parameters
       ----------
       from: DemographicID or DemographicIDs
         ID (name or index) or IDs of the demographics to scan for
         infected individuals
       to: DemographicID
         ID (name or index) of the demographic to send infected
         individuals to
       network: Networks
         The networks to be modelled. This must contain all of the
         demographics that are needed for this go function
       self_isolate_stage: int
         The stage of infection an individual must be at before they
         are moved into this demographic
       duration: int
         The number of days an individual should isolate for
       release_to: DemographicID
         ID (name or index) that the individual should move to after
         existing isolation. If this is not set, then the individual
         will return to their original demographic
    """

    if nthreads > 1:
        go_isolate_parallel(nthreads=nthreads, **kwargs)
    else:
        go_isolate_serial(**kwargs)
