#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython
from cython.parallel import parallel, prange

from .._network import Network
from ..utils._profiler import Profiler

from ..utils._ran_binomial cimport _ran_binomial, \
                                   _get_binomial_ptr, binomial_rng

from ..utils._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["advance_fixed", "advance_fixed_omp",
           "advance_fixed_serial"]


def advance_fixed_omp(network: Network, infections, rngs,
                      nthreads: int, profiler: Profiler, **kwargs):
    """Advance the model by triggering infections related to fixed
       'work' movements (parallel version of the function)

       Parameters
       ----------
       network: Network
         The network being modelled
       infections:
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

    links = network.to_links
    wards = network.nodes
    plinks = network.play
    params = network.params

    play_infections = infections.play
    infections = infections.work

    # Copy arguments from Python into C cdef variables
    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)
    cdef int * links_ito = get_int_array_ptr(links.ito)

    cdef double * links_distance = get_double_array_ptr(links.distance)
    cdef double * links_suscept = get_double_array_ptr(links.suscept)

    cdef double * wards_day_foi = get_double_array_ptr(wards.day_foi)
    cdef double * wards_day_inf_prob = get_double_array_ptr(wards.day_inf_prob)
    cdef double * wards_night_inf_prob = get_double_array_ptr(
                                                        wards.night_inf_prob)

    cdef double cutoff = params.dyn_dist_cutoff

    # Pointer to the infections array - only need [0] as this loop
    # is creating new infections
    cdef int * infections_i = get_int_array_ptr(infections[0])

    # get the random number generator
    cdef unsigned long [::1] rngs_view = rngs
    cdef binomial_rng* rng   # pointer to parallel rng

    # create and initialise variables used in the loop
    cdef int num_threads = nthreads
    cdef int thread_id = 0
    cdef int j = 0
    cdef int l = 0
    cdef int ifrom = 0
    cdef int ito = 0
    cdef int nlinks_plus_one = network.nlinks + 1

    cdef double inf_prob = 0.0
    cdef double distance = 0.0

    ## Finally(!) we can now declare the actual loop.
    ## This loops in parallel over all links between
    ## wards to create new infections that appear in
    ## those wards at daytime and nighttime

    p = profiler.start("fixed")
    with nogil, parallel(num_threads=num_threads):
        thread_id = cython.parallel.threadid()
        rng = _get_binomial_ptr(rngs_view[thread_id])

        for j in prange(1, nlinks_plus_one, schedule="static"):
            # actual new infections for fixed movements
            inf_prob = 0

            ifrom = links_ifrom[j]
            ito = links_ito[j]
            distance = links_distance[j]

            if distance < cutoff:
                # distance is below cutoff (reasonable distance)
                # infect in work ward
                if wards_day_foi[ito] > 0:
                    # daytime infection of link j
                    inf_prob = wards_day_inf_prob[ito]

                # end of if wards.day_foi[ito] > 0
            # end of if distance < cutoff
            elif wards_day_foi[ifrom] > 0:
                # if distance is too large then infect in home ward with day FOI
                inf_prob = wards_day_inf_prob[ifrom]

            if inf_prob > 0.0:
                # daytime infection of workers
                l = _ran_binomial(rng, inf_prob, <int>(links_suscept[j]))

                if l > 0:
                    # actual infection
                    #print(f"InfProb {inf_prob}, susc {links.suscept[j]}, l {l}")
                    infections_i[j] += l
                    links_suscept[j] -= l

            # nighttime infection of workers
            inf_prob = wards_night_inf_prob[ifrom]

            if inf_prob > 0.0:
                l = _ran_binomial(rng, inf_prob, <int>(links_suscept[j]))

                #if l > links_suscept[j]:
                #    print(f"l > links[{j}].suscept {links_suscept[j]} nighttime")

                if l > 0:
                    # actual infection
                    # print(f"NIGHT InfProb {inf_prob}, susc {links.suscept[j]}, {l}")
                    infections_i[j] += l
                    links_suscept[j] -= l
            # end of wards.night_foi[ifrom] > 0  (nighttime infections)
        # end of loop over all network links
    # end of parallel section
    p = p.stop()


def advance_fixed_serial(network: Network, infections, rngs,
                         profiler: Profiler, **kwargs):
    """Advance the model by triggering infections related to fixed
       'work' movements (serial version of the function)

       Parameters
       ----------
       network: Network
         The network being modelled
       infections:
         The space that holds all of the "work" infections
       rngs:
         The list of thread-safe random number generators, one per thread
       profiler: Profiler
         The profiler used to profile this calculation
       kwargs:
         Extra arguments that may be used by other advancers, but which
         are not used by advance_play
    """
    kwargs["nthreads"] = 1
    advance_fixed_omp(network=network, infections=infections,
                      rngs=rngs, profiler=profiler, **kwargs)


def advance_fixed(nthreads: int, **kwargs):
    """Advance the model by triggering infections related to fixed
       'work' movements (parallel version of the function)

       Parameters
       ----------
       network: Network
         The network being modelled
       infections:
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
    if nthreads == 1:
        advance_fixed_serial(**kwargs)
    else:
        advance_fixed_omp(nthreads=nthreads, **kwargs)
