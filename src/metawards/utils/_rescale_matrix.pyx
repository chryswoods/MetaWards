#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython
from cython.parallel import parallel, prange
cimport openmp

from .._network import Network

from ._profiler import Profiler
from ._recalculate_denominators import recalculate_play_denominator_day
from ._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["rescale_play_matrix"]


def rescale_play_matrix(network: Network, nthreads: int = 1,
                        profiler: Profiler = None):
    """ Static Play At Home rescaling.
	    for 1, everyone stays at home.
	    for 0 a lot of people move around.
    """

    params = network.params

    if params is None:
        return

    links = network.play

    cdef double static_play_at_home = params.static_play_at_home
    cdef double sclfac = 0.0
    cdef int j = 0
    cdef int ifrom = 0
    cdef int ito = 0
    cdef double suscept = 0.0
    cdef int * links_ito = get_int_array_ptr(links.ito)
    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)
    cdef double * links_weight = get_double_array_ptr(links.weight)
    cdef double * links_suscept = get_double_array_ptr(links.suscept)

    cdef int nlinks_plus_one = network.plinks + 1
    cdef int num_threads = nthreads

    if static_play_at_home > 0:
        # if we are making people stay at home, then do this loop through nodes
        # Rescale appropriately!
        sclfac = 1.0 - static_play_at_home

        with nogil, parallel(num_threads=num_threads):
            for j in prange(1, nlinks_plus_one, schedule="static"):
                ifrom = links_ifrom[j]
                ito = links_ito[j]

                if ifrom != ito:
                    # if it's not the home ward, then reduce the
                    # number of play movers
                    links_weight[j] = links_suscept[j] * sclfac
                else:
                    # if it is the home ward
                    suscept = links_suscept[j]
                    links_weight[j] = ((1.0 - suscept) *
                                        static_play_at_home) + suscept

    recalculate_play_denominator_day(network=network, nthreads=nthreads,
                                     profiler=profiler)
