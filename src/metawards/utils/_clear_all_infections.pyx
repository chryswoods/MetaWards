#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython
from cython.parallel import parallel, prange

from .._infections import Infections

from ._get_array_ptr cimport get_int_array_ptr

__all__ = ["clear_all_infections"]


def clear_all_infections(infections, play_infections,
                         nthreads: int=1):
    """Clears all infections associated with a model run

       Parameters
       ----------
       infections
         Space that is used to hold all of the 'work' infections
       play_infections
         Space that is used to hold all of the 'play' infections
       nthreads: int
         Number of threads to use to clear the arrays
    """

    cdef int i = 0
    cdef int j = 0
    cdef int n = len(infections)

    if n <= 0:
        return

    cdef int ninf = len(infections[0])
    cdef int nplay = len(play_infections[0])

    cdef int * a
    cdef int * b
    cdef int num_threads = nthreads

    for i in range(0, n):
        a = get_int_array_ptr(infections[i])
        b = get_int_array_ptr(play_infections[i])

        with nogil, parallel(num_threads=num_threads):
            for j in prange(0, ninf, schedule="static"):
                a[j] = 0

            for j in prange(0, nplay, schedule="static"):
                b[j] = 0
