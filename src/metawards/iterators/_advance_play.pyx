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

__all__ = ["advance_play", "advance_play_omp",
           "advance_play_serial"]


def advance_play_omp(network: Network, infections: Infections, rngs,
                     nthreads: int, profiler: Profiler, **kwargs):
    """Advance the model by triggering infections related to random
       'play' movements (parallel version of the function)

       Parameters
       ----------
       network: Network
         The network being modelled
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

    links = network.links
    wards = network.nodes
    play = network.play
    params = network.params

    play_infections = infections.play

    # Copy arguments from Python into C cdef variables
    cdef int * wards_begin_p = get_int_array_ptr(wards.begin_p)
    cdef int * wards_end_p = get_int_array_ptr(wards.end_p)

    cdef int * play_ito = get_int_array_ptr(play.ito)
    cdef double * play_weight = get_double_array_ptr(play.weight)

    cdef double * wards_day_foi = get_double_array_ptr(wards.day_foi)
    cdef double * wards_night_foi = get_double_array_ptr(wards.night_foi)

    cdef double * wards_play_suscept = get_double_array_ptr(wards.play_suscept)
    cdef double * play_distance = get_double_array_ptr(play.distance)

    cdef double * wards_day_inf_prob = get_double_array_ptr(
                                                    wards.day_inf_prob)
    cdef double * wards_night_inf_prob = get_double_array_ptr(
                                                    wards.night_inf_prob)

    cdef double dyn_play_at_home = params.dyn_play_at_home
    cdef double cutoff = params.dyn_dist_cutoff

    # Pointer to the play_infections array - only need [0] as this loop
    # is creating new infections
    cdef int * play_infections_i = get_int_array_ptr(play_infections[0])

    # get the random number generator
    cdef uintptr_t [::1] rngs_view = rngs
    cdef binomial_rng* rng   # pointer to parallel rng

    # create and initialise variables used in the loop
    cdef int num_threads = nthreads
    cdef int thread_id = 0

    cdef int j = 0
    cdef int k = 0
    cdef int l = 0
    cdef int ito = 0
    cdef int nnodes_plus_one = network.nnodes + 1

    cdef double weight = 0.0
    cdef double inf_prob = 0.0
    cdef double prob_scaled = 0.0
    cdef double cumulative_prob = 0.0

    cdef int suscept = 0
    cdef int staying = 0
    cdef int moving = 0

    cdef int play_move = 0

    ## Finally(!) we can now declare the actual loop.
    ## This loops in parallel over all wards to create
    ## new infections that appear in those wards at
    ## daytime and nighttime

    p = profiler.start("play")
    with nogil, parallel(num_threads=num_threads):
        thread_id = cython.parallel.threadid()
        rng = _get_binomial_ptr(rngs_view[thread_id])

        for j in prange(1, nnodes_plus_one, schedule="static"):
            inf_prob = 0.0
            suscept = <int>wards_play_suscept[j]
            staying = _ran_binomial(rng, dyn_play_at_home, suscept)

            moving = suscept - staying

            cumulative_prob = 0.0

            # daytime infection of play matrix moves
            for k in range(wards_begin_p[j], wards_end_p[j]):
                if play_distance[k] < cutoff:
                    ito = play_ito[k]

                    if wards_day_foi[ito] > 0.0:
                        weight = play_weight[k]
                        prob_scaled = weight / (1.0-cumulative_prob)
                        cumulative_prob = cumulative_prob + weight

                        play_move = _ran_binomial(rng, prob_scaled, moving)
                        inf_prob = wards_day_inf_prob[ito]

                        l = _ran_binomial(rng, inf_prob, play_move)

                        moving = moving - play_move

                        if l > 0:
                            # infection
                            play_infections_i[j] += l
                            wards_play_suscept[j] -= l
                    # end of DayFOI if statement
                # end of Dynamics Distance if statement
            # end of loop over links of wards[j]

            if (staying + moving) > 0:
                # infect people staying at home
                inf_prob = wards_day_inf_prob[j]
                l = _ran_binomial(rng, inf_prob, staying+moving)

                if l > 0:
                    # another infections, this time from home
                    #print(f"staying home play_infections[{i}][{j}] += {l}")
                    play_infections_i[j] += l
                    wards_play_suscept[j] -= l

            # nighttime infections of play movements
            inf_prob = wards_night_inf_prob[j]
            if inf_prob > 0.0:
                l = _ran_binomial(rng, inf_prob, <int>(wards_play_suscept[j]))

                if l > 0:
                    # another infection
                    play_infections_i[j] += l
                    wards_play_suscept[j] -= l
        # end of loop over wards (nodes)
    # end of parallel
    p.stop()


def advance_play_serial(network: Network, infections: Infections, rngs,
                        profiler: Profiler, **kwargs):
    """Advance the model by triggering infections related to random
       'play' movements (serial version of the function)

       Parameters
       ----------
       network: Network
         The network being modelled
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

    links = network.links
    wards = network.nodes
    play = network.play
    params = network.params

    play_infections = infections.play

    # Copy arguments from Python into C cdef variables
    cdef int * wards_begin_p = get_int_array_ptr(wards.begin_p)
    cdef int * wards_end_p = get_int_array_ptr(wards.end_p)

    cdef int * play_ito = get_int_array_ptr(play.ito)
    cdef double * play_weight = get_double_array_ptr(play.weight)

    cdef double * wards_day_foi = get_double_array_ptr(wards.day_foi)
    cdef double * wards_night_foi = get_double_array_ptr(wards.night_foi)

    cdef double * wards_play_suscept = get_double_array_ptr(wards.play_suscept)
    cdef double * play_distance = get_double_array_ptr(play.distance)

    cdef double * wards_day_inf_prob = get_double_array_ptr(
                                                    wards.day_inf_prob)
    cdef double * wards_night_inf_prob = get_double_array_ptr(
                                                    wards.night_inf_prob)

    cdef double dyn_play_at_home = params.dyn_play_at_home
    cdef double cutoff = params.dyn_dist_cutoff

    # Pointer to the play_infections array - only need [0] as this loop
    # is creating new infections
    cdef int * play_infections_i = get_int_array_ptr(play_infections[0])

    # get the random number generator
    cdef binomial_rng* rng = _get_binomial_ptr(rngs[0])

    cdef int j = 0
    cdef int k = 0
    cdef int l = 0
    cdef int ito = 0
    cdef int nnodes_plus_one = network.nnodes + 1

    cdef double weight = 0.0
    cdef double inf_prob = 0.0
    cdef double prob_scaled = 0.0
    cdef double cumulative_prob = 0.0

    cdef int suscept = 0
    cdef int staying = 0
    cdef int moving = 0

    cdef int play_move = 0

    ## Finally(!) we can now declare the actual loop.
    ## This loops in parallel over all wards to create
    ## new infections that appear in those wards at
    ## daytime and nighttime

    p = profiler.start("play")
    with nogil:
        for j in range(1, nnodes_plus_one):
            inf_prob = 0.0
            suscept = <int>wards_play_suscept[j]
            staying = _ran_binomial(rng, dyn_play_at_home, suscept)

            moving = suscept - staying

            cumulative_prob = 0.0

            # daytime infection of play matrix moves
            for k in range(wards_begin_p[j], wards_end_p[j]):
                if play_distance[k] < cutoff:
                    ito = play_ito[k]

                    if wards_day_foi[ito] > 0.0:
                        weight = play_weight[k]
                        prob_scaled = weight / (1.0-cumulative_prob)
                        cumulative_prob = cumulative_prob + weight

                        play_move = _ran_binomial(rng, prob_scaled, moving)
                        inf_prob = wards_day_inf_prob[ito]

                        l = _ran_binomial(rng, inf_prob, play_move)

                        moving = moving - play_move

                        if l > 0:
                            # infection
                            play_infections_i[j] += l
                            wards_play_suscept[j] -= l
                    # end of DayFOI if statement
                # end of Dynamics Distance if statement
            # end of loop over links of wards[j]

            if (staying + moving) > 0:
                # infect people staying at home
                inf_prob = wards_day_inf_prob[j]
                l = _ran_binomial(rng, inf_prob, staying+moving)

                if l > 0:
                    # another infections, this time from home
                    #print(f"staying home play_infections[{i}][{j}] += {l}")
                    play_infections_i[j] += l
                    wards_play_suscept[j] -= l

            # nighttime infections of play movements
            inf_prob = wards_night_inf_prob[j]
            if inf_prob > 0.0:
                l = _ran_binomial(rng, inf_prob, <int>(wards_play_suscept[j]))

                if l > 0:
                    # another infection
                    play_infections_i[j] += l
                    wards_play_suscept[j] -= l
        # end of loop over wards (nodes)
    # end of nogil
    p.stop()

def advance_play(nthreads: int, **kwargs):
    """Advance the model by triggering infections related to random
       'play' movements (parallel version of the function)

       Parameters
       ----------
       network: Network
         The network being modelled
       infections: Infections
         The space that holds all of the "play" infections
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
                             func=advance_play_serial,
                             parallel=advance_play_omp,
                             **kwargs)
