#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython
from cython.parallel import parallel, prange
cimport openmp

from libc.math cimport floor

from .._network import Network

from ._profiler import Profiler
from ._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["recalculate_work_denominator_day",
           "recalculate_play_denominator_day"]


def recalculate_work_denominator_day(network: Network, nthreads: int = 1,
                                     profiler: Profiler = None):
    """Recalculate the denominator_d for the wards (nodes) in
       the network for the normal links
    """
    params = network.params

    if params is None:
        return

    wards = network.nodes
    links = network.links

    cdef int i = 0

    cdef double * wards_denominator_d = get_double_array_ptr(
                                                wards.denominator_d)
    cdef double * wards_denominator_n = get_double_array_ptr(
                                                wards.denominator_n)

    cdef int nnodes_plus_one = network.nnodes + 1
    cdef int num_threads = nthreads

    with nogil, parallel(num_threads=num_threads):
        for i in prange(1, nnodes_plus_one, schedule="static"):
            wards_denominator_d[i] = 0.0
            wards_denominator_n[i] = 0.0

    cdef int j = 0
    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)
    cdef int * links_ito = get_int_array_ptr(links.ito)
    cdef double * links_suscept = get_double_array_ptr(links.suscept)
    cdef int ifrom = 0
    cdef int ito = 0
    cdef int nlinks_plus_one = network.nlinks + 1
    cdef double suscept = 0.0
    cdef double sum = 0

    # not easily parallelisable due to reduction
    for j in range(1, nlinks_plus_one):
        ifrom = links_ifrom[j]
        ito = links_ito[j]
        suscept = links_suscept[j]
        wards_denominator_d[ito] += suscept
        wards_denominator_n[ifrom] += suscept
        sum += suscept

    #print(f"recalculate_work_denominator_day sum = {sum}")


def recalculate_play_denominator_day(network: Network, nthreads: int = 1,
                                     profiler: Profiler = None):
    """Recalculate the denominator_d for the wards (nodes) in
       the network for the play links
    """
    params = network.params

    if params is None:
        return

    wards = network.nodes
    links = network.play

    cdef int i = 0
    cdef double * wards_denominator_pd = get_double_array_ptr(
                                                    wards.denominator_pd)
    cdef double * wards_denominator_p = get_double_array_ptr(
                                                    wards.denominator_p)

    cdef int num_threads = nthreads
    cdef int nnodes_plus_one = network.nnodes + 1

    with nogil, parallel(num_threads=num_threads):
        for i in prange(1, nnodes_plus_one, schedule="static"):
            wards_denominator_pd[i] = 0
            wards_denominator_p[i] = 0

    cdef double sum = 0.0
    cdef int j = 0
    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)
    cdef int * links_ito = get_int_array_ptr(links.ito)
    cdef int ifrom = 0
    cdef int ito = 0
    cdef double weight = 0.0
    cdef double * links_weight = get_double_array_ptr(links.weight)
    cdef double denom = 0.0
    cdef double * wards_play_suscept = get_double_array_ptr(wards.play_suscept)

    cdef int nlinks_plus_one = network.nplay + 1

    # not easily parallelisable due to the reduction
    with nogil:
        for j in range(1, nlinks_plus_one):
            ifrom = links_ifrom[j]
            ito = links_ito[j]
            weight = links_weight[j]
            denom = weight * wards_play_suscept[ifrom]
            wards_denominator_pd[ito] += denom

            sum += denom

    #print(f"recalculate_play_denominator_day sum 1 = {sum}")

    sum = 0.0
    cdef double play_suscept = 0
    cdef double pd = 0.0

    with nogil, parallel(num_threads=num_threads):
        for i in prange(1, nnodes_plus_one, schedule="static"):
            pd = wards_denominator_pd[i]
            play_suscept = wards_play_suscept[i]

            wards_denominator_pd[i] = floor(pd + 0.5)
            wards_denominator_p[i] = play_suscept

            sum += play_suscept

    #print(f"recalculate_play_denominator_day sum 2 = {sum}")
