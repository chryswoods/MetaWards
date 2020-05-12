#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython
from cython.parallel import parallel, prange
from libc.stdint cimport uintptr_t

from .._network import Network
from .._infections import Infections

from ..utils._profiler import Profiler
from ..utils._get_functions import call_function_on_network

from ..utils._ran_binomial cimport _ran_binomial, \
                                   _get_binomial_ptr, binomial_rng

from ..utils._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["advance_recovery", "advance_recovery_omp",
           "advance_recovery_serial"]


def advance_recovery_omp(network: Network, infections: Infections, rngs,
                         nthreads: int, profiler: Profiler, **kwargs):
    """Advance the model by processing recovery of individual through
       the different stages of the disease (parallel version of the
       function))

       Parameters
       ----------
       network: Network
         The network being modelled
       infections: Infections
         The space that holds all of the  infections
       rngs:
         The list of thread-safe random number generators, one per thread
       nthreads: int
         The number of threads over which to parallelise the calculation
       profiler: Profiler
         The profiler used to profile this calculation
       kwargs:
         Extra arguments that may be used by other advancers, but which
         are not used by advance_play
    """

    params = network.params

    play_infections = infections.play
    infections = infections.work

    # Copy arguments from Python into C cdef variables
    cdef int N_INF_CLASSES = len(infections)

    cdef int * infections_i
    cdef int * infections_i_plus_one
    cdef int * play_infections_i
    cdef int * play_infections_i_plus_one

    # get the random number generator
    cdef uintptr_t [::1] rngs_view = rngs
    cdef binomial_rng* rng   # pointer to parallel rng

    # create and initialise variables used in the loop
    cdef int num_threads = nthreads
    cdef int thread_id = 0

    cdef double disease_progress = 0.0

    cdef int nnodes_plus_one = network.nnodes + 1
    cdef int nlinks_plus_one = network.nlinks + 1

    cdef int i = 0
    cdef int j = 0
    cdef int l = 0
    cdef int inf_ij = 0

    ## Finally(!) we can now declare the actual loop.
    ## This loops in parallel over all infections in
    ## 'infections' and 'play_infections' and advances
    ## then through the various stages depending on
    ## the result of a random trial

    p = profiler.start("recovery")
    for i in range(N_INF_CLASSES-2, -1, -1):
        # recovery, move through classes backwards (loop down to 0)
        infections_i = get_int_array_ptr(infections[i])
        infections_i_plus_one = get_int_array_ptr(infections[i+1])
        play_infections_i = get_int_array_ptr(play_infections[i])
        play_infections_i_plus_one = get_int_array_ptr(play_infections[i+1])
        disease_progress = params.disease_params.progress[i]

        with nogil, parallel(num_threads=num_threads):
            thread_id = cython.parallel.threadid()
            rng = _get_binomial_ptr(rngs_view[thread_id])

            for j in prange(1, nlinks_plus_one, schedule="static"):
                inf_ij = infections_i[j]

                if inf_ij > 0:
                    l = _ran_binomial(rng, disease_progress, inf_ij)

                    if l > 0:
                        infections_i_plus_one[j] += l
                        infections_i[j] -= l

            for j in prange(1, nnodes_plus_one, schedule="static"):
                inf_ij = play_infections_i[j]

                if inf_ij > 0:
                    l = _ran_binomial(rng, disease_progress, inf_ij)

                    if l > 0:
                        play_infections_i_plus_one[j] += l
                        play_infections_i[j] -= l

        # end of parallel section
    # end of recovery loop
    p = p.stop()


def advance_recovery_serial(network: Network, infections: Infections,
                            rngs, profiler: Profiler, **kwargs):
    """Advance the model by processing recovery of individual through
       the different stages of the disease (serial version of the
       function))

       Parameters
       ----------
       network: Network
         The network being modelled
       infections: Infections
         The space that holds all of the infections
       rngs:
         The list of thread-safe random number generators, one per thread
       profiler: Profiler
         The profiler used to profile this calculation
       kwargs:
         Extra arguments that may be used by other advancers, but which
         are not used by advance_play
    """

    params = network.params

    play_infections = infections.play
    infections = infections.work

    # Copy arguments from Python into C cdef variables
    cdef int N_INF_CLASSES = len(infections)

    cdef int * infections_i
    cdef int * infections_i_plus_one
    cdef int * play_infections_i
    cdef int * play_infections_i_plus_one

    # get the random number generator
    cdef binomial_rng* rng = _get_binomial_ptr(rngs[0])

    cdef double disease_progress = 0.0

    cdef int nnodes_plus_one = network.nnodes + 1
    cdef int nlinks_plus_one = network.nlinks + 1

    cdef int i = 0
    cdef int j = 0
    cdef int l = 0
    cdef int inf_ij = 0

    ## Finally(!) we can now declare the actual loop.
    ## This loops in parallel over all infections in
    ## 'infections' and 'play_infections' and advances
    ## then through the various stages depending on
    ## the result of a random trial

    p = profiler.start("recovery")
    for i in range(N_INF_CLASSES-2, -1, -1):
        # recovery, move through classes backwards (loop down to 0)
        infections_i = get_int_array_ptr(infections[i])
        infections_i_plus_one = get_int_array_ptr(infections[i+1])
        play_infections_i = get_int_array_ptr(play_infections[i])
        play_infections_i_plus_one = get_int_array_ptr(play_infections[i+1])
        disease_progress = params.disease_params.progress[i]

        with nogil:
            for j in range(1, nlinks_plus_one):
                inf_ij = infections_i[j]

                if inf_ij > 0:
                    l = _ran_binomial(rng, disease_progress, inf_ij)

                    if l > 0:
                        infections_i_plus_one[j] += l
                        infections_i[j] -= l

            for j in range(1, nnodes_plus_one):
                inf_ij = play_infections_i[j]

                if inf_ij > 0:
                    l = _ran_binomial(rng, disease_progress, inf_ij)

                    if l > 0:
                        play_infections_i_plus_one[j] += l
                        play_infections_i[j] -= l

        # end of parallel section
    # end of recovery loop
    p = p.stop()

def advance_recovery(nthreads: int, **kwargs):
    """Advance the model by processing recovery of individual through
       the different stages of the disease (parallel version of the
       function))

       Parameters
       ----------
       network: Network or Networks
         The network being modelled
       infections: Infections
         The space that holds all of the "work" infections
       rngs:
         The list of thread-safe random number generators, one per thread
       nthreads: int
         The number of threads over which to parallelise the calculation
       profiler: Profiler
         The profiler used to profile this calculation
       kwargs:
         Extra arguments that may be used by other advancers, but which
         are not used by advance_play
    """
    call_function_on_network(nthreads=nthreads,
                             func=advance_recovery_serial,
                             parallel=advance_recovery_omp,
                             **kwargs)
