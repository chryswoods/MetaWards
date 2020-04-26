#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython
from cython.parallel import parallel, prange
cimport openmp

from .._network import Network
from .._node import Node
from ._profiler import Profiler

from ._get_array_ptr cimport get_double_array_ptr

__all__ = ["reset_work_matrix", "reset_play_matrix",
           "reset_play_susceptibles", "reset_everything"]


def reset_work_matrix(network: Network, nthreads=1):
    """Resets the work entries in the passed Network. You need
       to call this before performing a new model run

       Parameters
       ----------
       network: Network
         The network to be reset
       nthreads: int
         Number of threads to parallelise over
    """
    links = network.to_links

    cdef int i = 0
    cdef double * links_suscept = get_double_array_ptr(links.suscept)
    cdef double * links_weight = get_double_array_ptr(links.weight)

    cdef int nlinks_plus_one = network.nlinks + 1
    cdef int num_threads = nthreads

    with nogil, parallel(num_threads=num_threads):
        for i in prange(1, nlinks_plus_one, schedule="static"):
            links_suscept[i] = links_weight[i]


def reset_play_matrix(network: Network, nthreads: int=1):
    """Resets the play entries in the passed Network. You need
       to call this before performing a new model run

       Parameters
       ----------
       network: Network
         The network to be reset
       nthreads: int
         Number of threads to parallelise over
    """
    links = network.play

    cdef int i = 0
    cdef double * links_suscept = get_double_array_ptr(links.suscept)
    cdef double * links_weight = get_double_array_ptr(links.weight)

    cdef int nlinks_plus_one = network.plinks + 1
    cdef int num_threads = nthreads

    with nogil, parallel(num_threads=num_threads):
        for i in prange(1, nlinks_plus_one, schedule="static"):
            links_weight[i] = links_suscept[i]


def reset_play_susceptibles(network: Network, nthreads: int=1):
    """Resets the ward entries in the passed Network. You need
       to call this before performing a new model run

       Parameters
       ----------
       network: Network
         The network to be reset
       nthreads: int
         Number of threads to parallelise over
    """
    nodes = network.nodes

    cdef int i = 0
    cdef double * nodes_play_suscept = get_double_array_ptr(nodes.play_suscept)
    cdef double * nodes_save_play_suscept = get_double_array_ptr(
                                                    nodes.save_play_suscept)

    cdef int nnodes_plus_one = network.nnodes + 1
    cdef int num_threads = nthreads

    with nogil, parallel(num_threads=num_threads):
        for i in prange(1, nnodes_plus_one, schedule="static"):
            nodes_play_suscept[i] = nodes_save_play_suscept[i]


def reset_everything(network: Network, profiler: Profiler, nthreads: int = 1):
    """Reset everything in the passed network so that it can
       be used for a new model run

       Parameters
       ----------
       network: Network
         The network to be reset
       nthreads: int
         Number of threads to use during the reset
       profiler: Profiler
         Profiler used to profile the reset
    """
    p = profiler.start("reset_work")
    reset_work_matrix(network=network, nthreads=nthreads)
    p = p.stop()

    p = p.start("reset_play")
    reset_play_matrix(network=network, nthreads=nthreads)
    p = p.stop()

    p = p.start("reset_susceptibles")
    reset_play_susceptibles(network=network, nthreads=nthreads)
    p = p.stop()

    p = p.start("reset_params")
    params = network.params
    if params:
        N_INF_CLASSES = params.disease_params.N_INF_CLASSES()

        params.disease_params.contrib_foi = N_INF_CLASSES * [0]

        for i in range(0, N_INF_CLASSES-1):   # why -1?
            params.disease_params.contrib_foi[i] = 1

        network.params = params

    p = p.stop()
