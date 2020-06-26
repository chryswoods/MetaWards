#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

cimport cython

from ..utils._get_array_ptr cimport get_int_array_ptr

__all__ = ["zero_workspace"]


def zero_workspace(workspace):

    cdef int N_INF_CLASSES = workspace.n_inf_classes
    cdef int NNODES_PLUS_ONE = workspace.nnodes + 1

    cdef int * inf_tot = get_int_array_ptr(workspace.inf_tot)
    cdef int * pinf_tot = get_int_array_ptr(workspace.pinf_tot)
    cdef int * n_inf_wards = get_int_array_ptr(workspace.n_inf_wards)

    cdef int * ward_inf_tot_i

    cdef int * total_inf_ward = get_int_array_ptr(workspace.total_inf_ward)
    cdef int * total_new_inf_ward = get_int_array_ptr(
                                        workspace.total_new_inf_ward)
    cdef int * incidence = get_int_array_ptr(workspace.incidence)
    cdef int * S_in_wards = get_int_array_ptr(workspace.S_in_wards)
    cdef int * E_in_wards = get_int_array_ptr(workspace.E_in_wards)
    cdef int * I_in_wards = get_int_array_ptr(workspace.I_in_wards)
    cdef int * R_in_wards = get_int_array_ptr(workspace.R_in_wards)

    cdef int i = 0
    cdef int j = 0

    for i in range(0, N_INF_CLASSES):
        with nogil:
            inf_tot[i] = 0
            pinf_tot[i] = 0
            n_inf_wards[i] = 0

        ward_inf_tot_i = get_int_array_ptr(workspace.ward_inf_tot[i])

        with nogil:
            for j in range(0, NNODES_PLUS_ONE):
                ward_inf_tot_i[j] = 0

    with nogil:
        for j in range(0, NNODES_PLUS_ONE):
            total_inf_ward[j] = 0
            total_new_inf_ward[j] = 0
            incidence[j] = 0

            if S_in_wards:
                S_in_wards[j] = 0

            if E_in_wards:
                E_in_wards[j] = 0

            if I_in_wards:
                I_in_wards[j] = 0

            if R_in_wards:
                R_in_wards[j] = 0

    if workspace.X_in_wards is not None:
        for value in workspace.X_in_wards.values():
            X_in_wards = get_int_array_ptr(value)
            with nogil:
                for j in range(0, NNODES_PLUS_ONE):
                    X_in_wards[j] = 0
