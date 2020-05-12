#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython
from cython.parallel import parallel, prange
from libc.math cimport floor, ceil

from .._network import Network

from ._recalculate_denominators import recalculate_play_denominator_day, \
                                       recalculate_work_denominator_day
from ._profiler import Profiler
from ._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["move_population_from_work_to_play",
           "move_population_from_play_to_work"]


def move_population_from_work_to_play(network: Network,
                                      nthreads: int = 1,
                                      profiler: Profiler = None):
    """This function is not used or implemented, but is implied
       by the naming scheme...
    """
    raise AssertionError("Code has not been written")


def move_population_from_play_to_work(network: Network,
                                      nthreads: int = 1,
                                      profiler: Profiler = None):
    """And Vice Versa From Work to Play
       The relevant parameters are network.params.play_to_work and
                                   network.params.work_to_play

       When both are 0, don't do anything;
       When play_to_work > 0 move work_to_play proportion from play to work.
       When work_to_play > 0 move work_to_play proportion from work to play.
    """

    params = network.params

    if params is None:
        return

    links = network.links
    wards = network.nodes
    play = network.play

    cdef int i = 0
    cdef double * links_suscept = get_double_array_ptr(links.suscept)
    cdef double * wards_play_suscept = get_double_array_ptr(wards.play_suscept)
    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)
    cdef double to_move = 0.0
    cdef double work_to_play = params.work_to_play
    cdef double play_to_work = params.play_to_work
    cdef double suscept = 0.0

    cdef int num_threads = nthreads
    cdef int nlinks_plus_one = network.nlinks + 1

    if params.work_to_play > 0.0:
        with nogil:
            for i in range(1, nlinks_plus_one):
                suscept = links_suscept[i]
                to_move = ceil(suscept * work_to_play)
                links_suscept[i] -= to_move
                wards_play_suscept[links_ifrom[i]] += to_move

    cdef int ifrom = 0
    cdef int * play_ifrom = get_int_array_ptr(play.ifrom)
    cdef double * play_weight = get_double_array_ptr(play.weight)
    cdef double * wards_save_play_suscept = get_double_array_ptr(
                                                    wards.save_play_suscept)
    cdef double countrem = 0.0
    cdef double temp = 0.0
    cdef double p = 0.0
    nlinks_plus_one = network.nplay + 1

    if params.play_to_work > 0.0:
        with nogil:
            for i in range(1, nlinks_plus_one):
                ifrom = play_ifrom[i]

                temp = play_to_work * (play_weight[i] *
                                    wards_save_play_suscept[ifrom])

                to_move = floor(temp)
                p = temp - to_move

                countrem += p

                if countrem >= 1.0:
                    to_move += 1.0
                    countrem -= 1.0

                if wards_play_suscept[ifrom] < to_move:
                    to_move = wards_play_suscept[ifrom]

                wards_play_suscept[ifrom] -= to_move
                links_suscept[i] += to_move

    recalculate_work_denominator_day(network=network, nthreads=nthreads,
                                     profiler=profiler)
    recalculate_play_denominator_day(network=network, nthreads=nthreads,
                                     profiler=profiler)
