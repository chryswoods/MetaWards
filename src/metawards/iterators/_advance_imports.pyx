#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython
from cython.parallel import parallel, prange
from libc.stdint cimport uintptr_t

from .._network import Network
from .._population import Population
from .._infections import Infections

from ..utils._profiler import Profiler
from ..utils._get_functions import call_function_on_network

from ..utils._ran_binomial cimport _ran_binomial, \
                                   _get_binomial_ptr, binomial_rng

from ..utils._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["advance_imports", "advance_imports_omp",
           "advance_imports_serial"]


def advance_imports_omp(network: Network, population: Population,
                        infections: Infections, rngs,
                        nthreads: int, profiler: Profiler,
                        **kwargs):
    """Advance the model by importing additional infections
       depending on the additional seeds specified by the user
       and the day of the outbreak (serial version of the function)

       Parameters
       ----------
       network: Network
         The network being modelled
       population: Population
         The population experiencing the outbreak
       infections: Infections
         The space that holds all of the infections
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

    wards = network.nodes
    links = network.links
    params = network.params

    play_infections = infections.play
    infections = infections.work

    # Copy arguments from Python into C cdef variables
    cdef double * wards_play_suscept = get_double_array_ptr(wards.play_suscept)
    cdef double * links_suscept = get_double_array_ptr(links.suscept)

    cdef int * infections_0 = get_int_array_ptr(infections[0])
    cdef int * play_infections_0 = get_int_array_ptr(play_infections[0])

    cdef double frac = float(params.daily_imports) / float(population.initial)

    # get the random number generator
    cdef uintptr_t [::1] rngs_view = rngs
    cdef binomial_rng* rng   # pointer to parallel rng

    # create and initialise variables used in the loop
    cdef int num_threads = nthreads
    cdef int thread_id = 0
    cdef int i = 0
    cdef int to_seed = 0
    cdef int nnodes_plus_one = network.nnodes + 1
    cdef int nlinks_plus_one = network.nlinks + 1

    ## Finally(!) we can now declare the actual loop.
    ## This loops in parallel over all infections in
    ## 'infections' and 'play_infections' and advances
    ## then through the various stages depending on
    ## the result of a random trial

    p = profiler.start("imports")
    with nogil, parallel(num_threads=num_threads):
        thread_id = cython.parallel.threadid()
        rng = _get_binomial_ptr(rngs_view[thread_id])

        for i in prange(0, nnodes_plus_one):
            to_seed = _ran_binomial(rng, frac, <int>(wards_play_suscept[i]))

            if to_seed > 0:
                wards_play_suscept[i] -= to_seed
                play_infections_0[i] += to_seed

        for i in prange(0, nlinks_plus_one):
            # workers
            to_seed = _ran_binomial(rng, frac, <int>(links_suscept[i]))

            if to_seed > 0:
                links_suscept[i] -= to_seed
                infections_0[i] += to_seed

    p = p.stop()



def advance_imports_serial(network: Network, population: Population,
                           infections: Infections, rngs,
                           profiler: Profiler, **kwargs):
    """Advance the model by importing additional infections
       randomly

       Parameters
       ----------
       network: Network
         The network being modelled
       population: Population
         The population experiencing the outbreak
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

    wards = network.nodes
    links = network.links
    params = network.params

    play_infections = infections.play
    infections = infections.work

    # Copy arguments from Python into C cdef variables
    cdef double * wards_play_suscept = get_double_array_ptr(wards.play_suscept)
    cdef double * links_suscept = get_double_array_ptr(links.suscept)

    cdef int * infections_0 = get_int_array_ptr(infections[0])
    cdef int * play_infections_0 = get_int_array_ptr(play_infections[0])

    cdef double frac = float(params.daily_imports) / float(population.initial)

    cdef binomial_rng* rng = _get_binomial_ptr(rngs[0])

    # create and initialise variables used in the loop
    cdef int i = 0
    cdef int total = 0
    cdef int to_seed = 0
    cdef int nnodes_plus_one = network.nnodes + 1
    cdef int nlinks_plus_one = network.nlinks + 1

    ## Finally(!) we can now declare the actual loop.
    ## This loops in parallel over all infections in
    ## 'infections' and 'play_infections' and advances
    ## then through the various stages depending on
    ## the result of a random trial

    p = profiler.start("imports")
    with nogil:
        for i in range(0, nnodes_plus_one):
            to_seed = _ran_binomial(rng, frac, <int>(wards_play_suscept[i]))

            if to_seed > 0:
                wards_play_suscept[i] -= to_seed
                play_infections_0[i] += to_seed
                total += to_seed

        for i in range(0, nlinks_plus_one):
            # workers
            to_seed = _ran_binomial(rng, frac, <int>(links_suscept[i]))

            if to_seed > 0:
                links_suscept[i] -= to_seed
                infections_0[i] += to_seed
                total += to_seed

    p = p.stop()

    if params.daily_imports != total:
        print(f"Day: {population.day} Imports: "
              f"expected {params.daily_imports} "
              f"actual {total}")

        raise AssertionError(f"Incorrect number of daily imports on day "
                             f"{population.day}. {params.daily_imports} vs "
                             f"{total}")


def advance_imports(nthreads: int, **kwargs):
    """Advance the model by importing additional infections
       depending on the additional seeds specified by the user
       and the day of the outbreak (serial version of the function)

       Parameters
       ----------
       network: Network
         The network being modelled
       population: Population
         The population experiencing the outbreak
       infections: Infections
         The space that holds all of the infections
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
                             func=advance_imports_serial,
                             parallel=advance_imports_omp,
                             **kwargs)
