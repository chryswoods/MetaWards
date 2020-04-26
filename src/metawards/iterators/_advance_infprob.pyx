#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython
from cython.parallel import parallel, prange

from .._network import Network
from ..utils._profiler import Profiler
from ..utils._rate_to_prob cimport rate_to_prob

from ..utils._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["advance_infprob", "advance_infprob_omp",
           "advance_infprob_serial"]


def advance_infprob_omp(network: Network, nthreads: int,
                        profiler: Profiler,
                        scale_rate: float = 1.0,
                        **kwargs):
    """Advance the calculation of the day and night infection probabilities
       for each ward. You need to call this function after you have
       changed them, and before you use them in, e.g. advance_fixed
       and advance_play. This is the parallel version of this function

       Parameters
       ----------
       network: Network
         The network being modelled
       nthreads: int
         The number of threads over which to parallelise the calculation
       profiler: Profiler
         The profiler used to profile this calculation
       scale_rate: float
         Optional parameter to scale the calculated infection rates.
         This can very bluntly model the impact of broad measures
         to reduce the infection rate
       kwargs:
         Extra arguments that may be used by other advancers, but which
         are not used by advance_infprob
    """
    wards = network.nodes
    params = network.params

    # Copy arguments from Python into C cdef variables
    cdef double length_day = params.length_day
    cdef double sclrate = scale_rate

    if sclrate < 0:
        sclrate = 0.0

    cdef double * wards_day_foi = get_double_array_ptr(wards.day_foi)
    cdef double * wards_night_foi = get_double_array_ptr(wards.night_foi)

    cdef double * wards_denominator_d = get_double_array_ptr(
                                                    wards.denominator_d)
    cdef double * wards_denominator_n = get_double_array_ptr(
                                                    wards.denominator_n)
    cdef double * wards_denominator_p = get_double_array_ptr(
                                                    wards.denominator_p)
    cdef double * wards_denominator_pd = get_double_array_ptr(
                                                    wards.denominator_pd)

    cdef double * wards_day_inf_prob = get_double_array_ptr(
                                                    wards.day_inf_prob)
    cdef double * wards_night_inf_prob = get_double_array_ptr(
                                                    wards.night_inf_prob)

    # create and initialise variables used in the loop
    cdef double rate = 0.0
    cdef double inf_prob = 0.0
    cdef double denom = 0.0

    cdef int num_threads = nthreads
    cdef int thread_id = 0
    cdef int j = 0
    cdef int nnodes_plus_one = network.nnodes + 1

    ## Finally(!) we can now declare the actual loop.
    ## This loops in parallel over all wards to calculate
    ## the day and night infection probabilities for
    ## all wards

    p = profiler.start("infprob")
    with nogil, parallel(num_threads=num_threads):
        for j in prange(1, nnodes_plus_one, schedule="static"):
            # pre-calculate the day and night infection probability
            # for each ward
            denom = wards_denominator_d[j] + wards_denominator_pd[j]

            if denom != 0.0:
                rate = (length_day * wards_day_foi[j]) / denom
                wards_day_inf_prob[j] = rate_to_prob(sclrate * rate)
            else:
                wards_day_inf_prob[j] = 0.0

            denom = wards_denominator_n[j] + wards_denominator_p[j]

            if denom != 0.0:
                rate = (1.0 - length_day) * (wards_night_foi[j]) / denom
                wards_night_inf_prob[j] = rate_to_prob(sclrate * rate)
            else:
                wards_night_inf_prob[j] = 0.0
        # end of loop over wards
    # end of parallel
    p = p.stop()


def advance_infprob_serial(**kwargs):
    """Advance the calculation of the day and night infection probabilities
       for each ward. You need to call this function after you have
       changed them, and before you use them in, e.g. advance_fixed
       and advance_play. This is the serial version of this function

       Parameters
       ----------
       network: Network
         The network being modelled
       profiler: Profiler
         The profiler used to profile this calculation
       kwargs:
         Extra arguments that may be used by other advancers, but which
         are not used by advance_infprob
    """
    kwargs["nthreads"] = 1
    advance_infprob_omp(**kwargs)


def advance_infprob(nthreads: int, **kwargs):
    """Advance the calculation of the day and night infection probabilities
       for each ward. You need to call this function after you have
       changed them, and before you use them in, e.g. advance_fixed
       and advance_play. This is the parallel version of this function

       Parameters
       ----------
       network: Network
         The network being modelled
       nthreads: int
         The number of threads over which to parallelise the calculation
       profiler: Profiler
         The profiler used to profile this calculation
       scale_rate: float
         Optional parameter to scale the calculated infection rates.
         This can very bluntly model the impact of broad measures
         to reduce the infection rate
       kwargs:
         Extra arguments that may be used by other advancers, but which
         are not used by advance_infprob
    """
    if nthreads == 1:
        advance_infprob_serial(**kwargs)
    else:
        advance_infprob_omp(nthreads=nthreads, **kwargs)
