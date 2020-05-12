#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython
from cython.parallel import parallel, prange

from .._networks import Networks

from ..utils._profiler import Profiler
from ..utils._get_array_ptr cimport get_double_array_ptr

__all__ = ["merge_evenly"]


def merge_evenly(network: Networks, nthreads: int,
                 profiler: Profiler, **kwargs):
    """This merge_function merges the FOIs across all demographic
       sub-networks evenly. This should be equivalent to
       calculating the FOIs of the entire network without
       using demographics
    """

    subnets = network.subnets
    cdef int nsubnets = len(subnets)

    if nsubnets < 2:
        # nothing to merge
        return

    cdef int nnodes_plus_one = network.overall.nnodes + 1

    cdef int i = 0
    cdef int j = 0

    cdef int num_threads = nthreads

    wards = network.overall.nodes

    cdef double * wards_day_foi = get_double_array_ptr(wards.day_foi)
    cdef double * wards_night_foi = get_double_array_ptr(wards.night_foi)

    cdef double * sub_day_foi
    cdef double * sub_night_foi

    # accumulate the FOI for each ward into the overall network
    p = profiler.start("accumulate")
    with nogil, parallel(num_threads=num_threads):
        for j in prange(1, nnodes_plus_one, schedule="static"):
            wards_day_foi[j] = 0.0
            wards_night_foi[j] = 0.0

    for subnet in subnets:
        sub_wards = subnet.nodes
        sub_day_foi = get_double_array_ptr(sub_wards.day_foi)
        sub_night_foi = get_double_array_ptr(sub_wards.night_foi)

        with nogil, parallel(num_threads=num_threads):
            for j in prange(1, nnodes_plus_one, schedule="static"):
                wards_day_foi[j] = wards_day_foi[j] + \
                                   sub_day_foi[j]
                wards_night_foi[j] = wards_night_foi[j] + \
                                     sub_night_foi[j]

    p = p.stop()

    # now copy this total FOI back to all demographics
    p = p.start("distribute")

    for subnet in subnets:
        sub_wards = subnet.nodes
        sub_day_foi = get_double_array_ptr(sub_wards.day_foi)
        sub_night_foi = get_double_array_ptr(sub_wards.night_foi)

        with nogil, parallel(num_threads=num_threads):
            for j in prange(1, nnodes_plus_one, schedule="static"):
                sub_day_foi[j] = wards_day_foi[j]
                sub_night_foi[j] = wards_night_foi[j]

    p = p.stop()
