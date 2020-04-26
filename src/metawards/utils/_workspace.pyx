
from ._array import create_int_array

from .._network import Network

from ._get_array_ptr cimport get_int_array_ptr

__all__ = ["Workspace"]


class Workspace:
    """This class provides a workspace for the running calculation.
       This pre-allocates all of the memory into arrays, which
       can then be used via cython memory views
    """
    def __init__(self, network: Network):
        """Create the workspace needed to run the model for the
           passed network
        """
        params = network.params

        n_inf_classes = params.disease_params.N_INF_CLASSES()

        #: number of disease stages
        self.n_inf_classes = params.disease_params.N_INF_CLASSES()

        #: number of wards (nodes)
        self.nnodes = network.nnodes

        size = self.nnodes + 1  # 1-indexed

        #: Size of population in each disease stage for work infections
        self.inf_tot = create_int_array(n_inf_classes, 0)
        #: Size of population in each disease stage for play infections
        self.pinf_tot = create_int_array(n_inf_classes, 0)
        #: Number of wards with at least one individual in this disease stage
        self.n_inf_wards = create_int_array(n_inf_classes, 0)

        #: Total number of infections in each ward over the last day
        #: This is also equal to the prevalence
        self.total_inf_ward = create_int_array(size, 0)

        #: Number of new infections in each ward over the last day
        self.total_new_inf_ward = create_int_array(size, 0)

        #: The incidence of the infection (sum of infections up to
        #: disease_class == 2)
        self.incidence = create_int_array(size, 0)

    def zero_all(self):
        """Reset the values of all of the arrays to zero"""
        cdef int i = 0

        cdef int * inf_tot = get_int_array_ptr(self.inf_tot)
        cdef int * pinf_tot = get_int_array_ptr(self.pinf_tot)
        cdef int * n_inf_wards = get_int_array_ptr(self.n_inf_wards)

        cdef int * total_inf_ward = get_int_array_ptr(self.total_inf_ward)
        cdef int * total_new_inf_ward = get_int_array_ptr(
                                                self.total_new_inf_ward)

        cdef int * incidence = get_int_array_ptr(self.incidence)

        cdef int nclasses = self.n_inf_classes
        cdef int nnodes_plus_one = self.nnodes + 1

        with nogil:
            for i in range(0, nclasses):
                inf_tot[i] = 0
                pinf_tot[i] = 0
                n_inf_wards[i] = 0

            for i in range(0, nnodes_plus_one):
                total_inf_ward[i] = 0
                total_new_inf_ward[i] = 0
                incidence[i] = 0
