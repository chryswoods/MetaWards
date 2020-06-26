#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython
cimport openmp

from .._networks import Networks
from .._infections import Infections
from ._profiler import Profiler

from ._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["aggregate_networks", "aggregate_infections"]


def aggregate_infections(infections: Infections, profiler: Profiler,
                         nthreads: int=1) -> None:
    """Aggregate all of the demographic sub-network infections data
       together into the overall infections object

       Parameters
       ----------
       infections: Infections
         The complete set of infection data
       profiler: Profiler
         Profiler used to profile this work
       nthreads: int
         Number of threads to use to do this work

       Returns
       -------
       None
    """
    from cython.parallel import parallel, prange

    if profiler is None:
        from ._profiler import NullProfiler
        profiler = NullProfiler()

    p = profiler.start("aggregate_infections")

    cdef int i = 0
    cdef int j = 0
    cdef int idx = 0
    cdef int nnodes_plus_one = infections.nnodes + 1
    cdef int nlinks_plus_one = infections.nlinks + 1
    cdef int nsublinks_plus_one = 0
    cdef int num_threads = nthreads

    cdef int * infections_i
    cdef int * play_infections_i
    cdef int * sub_infections_i
    cdef int * sub_play_infections_i
    cdef int * idxs

    # zero the overal infections
    p = p.start("zero")
    for i in range(0, infections.N_INF_CLASSES):
        infections_i = get_int_array_ptr(infections.work[i])
        play_infections_i = get_int_array_ptr(infections.play[i])

        with nogil, parallel(num_threads=num_threads):
            for j in prange(1, nnodes_plus_one, schedule="static"):
                play_infections_i[j] = 0

            for j in prange(1, nlinks_plus_one, schedule="static"):
                infections_i[j] = 0
    p = p.stop()

    # aggregate from the sub-infections
    for ii, subinf in enumerate(infections.subinfs):
        p = p.start(f"aggregate_{ii}")
        mapping = subinf.get_stage_mapping()

        for i in range(0, len(mapping)):
            infections_i = get_int_array_ptr(infections.work[mapping[i]])
            play_infections_i = get_int_array_ptr(infections.play[mapping[i]])
            sub_infections_i = get_int_array_ptr(subinf.work[i])
            sub_play_infections_i = get_int_array_ptr(subinf.play[i])

            # aggregate the work infections
            if subinf.has_different_work_matrix():
                # the subnetwork has a different work matrix
                idxs = get_int_array_ptr(subinf.get_work_index())
                nsublinks_plus_one = subinf.nlinks + 1

                with nogil, parallel(num_threads=num_threads):
                    for j in prange(1, nsublinks_plus_one, schedule="static"):
                        idx = idxs[j]
                        infections_i[idx] = infections_i[idx] + \
                                            sub_infections_i[j]

            else:
                # the subnetwork has the same work matrix
                with nogil, parallel(num_threads=num_threads):
                    for j in prange(1, nlinks_plus_one, schedule="static"):
                        infections_i[j] = infections_i[j] + \
                                          sub_infections_i[j]

            # aggregate the play infections
            with nogil, parallel(num_threads=num_threads):
                for j in prange(1, nnodes_plus_one, schedule="static"):
                    play_infections_i[j] = play_infections_i[j] + \
                                           sub_play_infections_i[j]

        p = p.stop()

    p = p.stop()


def aggregate_networks(network: Networks, profiler: Profiler,
                       nthreads: int = 1) -> None:
    """Aggregate all of the Susceptibles data from the demographic
       sub-networks into an overall total set of data
       that is stored in the overall network

       Parameters
       ----------
       network: Networks
         The collection of networks to be aggregated
       profiler: Profiler
         Profiler used to profile the calculation
       nthreads: int
         The number of threads over which to parallelise this work
    """
    from cython.parallel import parallel, prange

    if profiler is None:
        from ._profiler import NullProfiler
        profiler = NullProfiler()

    p = profiler.start("aggregate_network")

    cdef int i = 0
    cdef int j = 0
    cdef int idx = 0
    cdef int num_threads = nthreads

    nodes = network.overall.nodes
    links = network.overall.links

    cdef int nnodes_plus_one = network.overall.nnodes + 1
    cdef int nlinks_plus_one = network.overall.nlinks + 1
    cdef int nsublinks_plus_one = 0

    cdef double * nodes_play_suscept = get_double_array_ptr(nodes.play_suscept)
    cdef double * sub_nodes_play_suscept

    cdef double * links_weight = get_double_array_ptr(links.weight)
    cdef double * links_suscept = get_double_array_ptr(links.suscept)
    cdef double * sub_links_weight
    cdef double * sub_links_suscept
    cdef int * idxs

    # zero the overall data
    p = p.start("zero")
    with nogil, parallel(num_threads=num_threads):
        for i in prange(1, nlinks_plus_one):
            links_weight[i] = 0
            links_suscept[i] = 0

        for i in prange(1, nnodes_plus_one):
            nodes_play_suscept[i] = 0
    p = p.stop()

    for ii, subnet in enumerate(network.subnets):
        p = p.start(f"aggregate_work_{ii}")
        sublinks = subnet.links
        sub_links_weight = get_double_array_ptr(sublinks.weight)
        sub_links_suscept = get_double_array_ptr(sublinks.suscept)

        if subnet.has_different_work_matrix():
            # different work matrix, so need to look up indicies
            idxs = get_int_array_ptr(subnet.get_work_index())
            nsublinks_plus_one = subnet.nlinks + 1

            with nogil, parallel(num_threads=num_threads):
                for i in prange(1, nsublinks_plus_one):
                    idx = idxs[i]
                    links_weight[idx] = links_weight[idx] + \
                                        sub_links_weight[i]
                    links_suscept[idx] = links_suscept[idx] + \
                                         sub_links_weight[i]
        else:
            # same work matrix, so simple accumulation
            with nogil, parallel(num_threads=num_threads):
                for i in prange(1, nlinks_plus_one):
                    links_weight[i] = links_weight[i] + sub_links_weight[i]
                    links_suscept[i] = links_suscept[i] + sub_links_suscept[i]

        p = p.stop()

        p = p.start(f"aggregate_play_{ii}")
        subnodes = subnet.nodes
        sub_nodes_play_suscept = get_double_array_ptr(subnodes.play_suscept)

        with nogil, parallel(num_threads=num_threads):
            for i in prange(1, nnodes_plus_one):
                nodes_play_suscept[i] = nodes_play_suscept[i] + \
                                        sub_nodes_play_suscept[i]

        p = p.stop()

    p = p.stop()

