#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython
from cython.parallel import parallel, prange

from .._networks import Networks

from ..utils._profiler import Profiler
from ..utils._get_array_ptr cimport get_double_array_ptr
from ..utils._array import create_double_array

__all__ = ["merge_using_matrix"]


def merge_using_matrix(network: Networks, nthreads: int,
                       profiler: Profiler, **kwargs):
    """This merge_function merges the FOIs across all demographic
       sub-networks according to the interaction matrix stored
       in networks.demographics.interaction_matrix.
    """

    matrix = network.demographics.interaction_matrix

    if matrix is None:
        # No matrix, so nothing should interact
        return

    subnets = network.subnets
    cdef int nsubnets = len(subnets)

    if nsubnets < 2:
        # nothing to merge
        return

    # the matrix should be sized for the number of subnets
    if len(matrix) != nsubnets:
        raise ValueError(
            f"The interaction matrix must be right-sized for the number "
            f"of demographics, e.g. it must be {nsubnets}x{nsubnets}")

    # it must also be square
    for row in matrix:
        if len(row) != nsubnets:
            raise ValueError(
                f"The interaction matrix must be square, e.g. "
                f"{nsubnets}x{nsubnets}.")

    # if all values are 1.0 then it is quicker to call merge_evenly

    # similarly if this is [[1,0], [0,1]] then it is quicker to
    # call merge_none. However, we won't do this now as this is a good
    # test if this merge function is correct

    cdef int nnodes_plus_one = network.overall.nnodes + 1

    cdef int i = 0
    cdef int j = 0
    cdef int k = 0

    cdef int num_threads = nthreads

    wards = network.overall.nodes

    cdef double scl = 0.0

    cdef double * wards_day_foi = get_double_array_ptr(wards.day_foi)
    cdef double * wards_night_foi = get_double_array_ptr(wards.night_foi)

    cdef double * day_foi
    cdef double * night_foi

    cdef double * sub_day_foi
    cdef double * sub_night_foi

    # create space to calculate all of the day and night fois
    day_fois = []
    night_fois = []

    p = profiler.start("allocate")
    for i in range(0, nsubnets):
        day_fois.append(create_double_array(nnodes_plus_one, 0.0))
        night_fois.append(create_double_array(nnodes_plus_one, 0.0))
    p = p.stop()

    # calculate the merged FOIs
    p = profiler.start("accumulate")
    for i in range(0, nsubnets):
        day_foi = get_double_array_ptr(day_fois[i])
        night_foi = get_double_array_ptr(night_fois[i])

        for j in range(0, nsubnets):
            sub_wards = subnets[j].nodes
            sub_day_foi = get_double_array_ptr(sub_wards.day_foi)
            sub_night_foi = get_double_array_ptr(sub_wards.night_foi)

            scl = matrix[i][j]

            with nogil, parallel(num_threads=num_threads):
                for k in prange(1, nnodes_plus_one, schedule="static"):
                    day_foi[k] = day_foi[k] + \
                                 scl * sub_day_foi[k]
                    night_foi[k] = night_foi[k] + \
                                   scl * sub_night_foi[k]
    p = p.stop()

    p = profiler.start("distribute")
    for j in range(0, nsubnets):
        day_foi = get_double_array_ptr(day_fois[j])
        night_foi = get_double_array_ptr(night_fois[j])

        sub_wards = subnets[j].nodes
        sub_day_foi = get_double_array_ptr(sub_wards.day_foi)
        sub_night_foi = get_double_array_ptr(sub_wards.night_foi)

        with nogil, parallel(num_threads=num_threads):
            for k in prange(1, nnodes_plus_one, schedule="static"):
                sub_day_foi[k] = day_foi[k]
                sub_night_foi[k] = night_foi[k]
    p = p.stop()
