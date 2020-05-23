#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

from .._network import Network
from .._population import Population
from .._outputfiles import OutputFiles
from .._infections import Infections

from .._workspace import Workspace

from ..utils._get_functions import call_function_on_network
from ..utils._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

from math import sqrt

__all__ = ["output_dispersal", "output_dispersal_serial"]


def output_dispersal_serial(network: Network, population: Population,
                            output_dir: OutputFiles,
                            workspace: Workspace,
                            **kwargs):
    """This will calculate and output the geographic dispersal
       of the outbreak

       Parameters
       ----------
       network: Network
         The network over which the outbreak is being modelled
       population: Population
         The population experiencing the outbreak
       output_dir: OutputFiles
         The directory in which to place all output files
       workspace: Workspace
         A workspace that can be used to extract data
       kwargs
         Extra arguments that are ignored by this function
    """

    wards = network.nodes

    # get data from the python objects
    cdef int * total_new_inf_ward = get_int_array_ptr(
                                        workspace.total_new_inf_ward)

    cdef double * wards_x = get_double_array_ptr(wards.x)
    cdef double * wards_y = get_double_array_ptr(wards.y)

    cdef int nnodes_plus_one = network.nnodes + 1

    # variables to accumulate data
    cdef double x = 0.0
    cdef double y = 0.0

    cdef double sum_x = 0.0
    cdef double sum_y = 0.0
    cdef double sum_x2 = 0.0
    cdef double sum_y2 = 0.0

    cdef int total_new = 0
    cdef int newinf = 0

    # now loop over all wards and accumulate the x/y position weighted
    # by new infections
    cdef int i = 0;

    with nogil:
        for i in range(1, nnodes_plus_one):
            newinf = total_new_inf_ward[i]

            if newinf > 0:
                x = wards_x[i]
                y = wards_y[i]

                sum_x += newinf * x
                sum_y += newinf * y

                sum_x2 += newinf * x * x
                sum_y2 += newinf * y * y

                total_new += newinf

    # get the file handles - this will open the files if
    # they have not already been created
    if network.name is not None:
        name = "_" + network.name.replace(" ", "_")
    else:
        name = ""

    mean_xy_file = output_dir.open(f"MeanXY{name}.dat")
    var_xy_file = output_dir.open(f"VarXY{name}.dat")
    dispersal_file = output_dir.open(f"Dispersal{name}.dat")

    timestep = population.day

    if total_new > 0:
        mean_x = sum_x / total_new
        mean_y = sum_y / total_new

        if total_new > 1:
            var_x = (sum_x2 - sum_x*mean_x) / (total_new - 1)
            var_y = (sum_y2 - sum_y*mean_y) / (total_new - 1)
        else:
            var_x = 0.0
            var_y = 0.0

        if var_x + var_y > 0:
            dispersal = sqrt(var_x + var_y)
        elif var_x + var_y > -0.1:
            # numeric rounding error
            dispersal = 0.0
        else:
            from ..utils._console import Console
            Console.warning(f"Negative var? {var_x+var_y}, {var_x} {var_y}")
            dispersal = 0.0
    else:
        mean_x = 0.0
        mean_y = 0.0

        var_x = 0.0
        var_y = 0.0

        dispersal = 0.0

    mean_xy_file.write("%d %f %f\n" % (timestep, mean_x, mean_y))
    var_xy_file.write("%d %f %f\n" % (timestep, var_x, var_y))
    dispersal_file.write("%d %f\n" % (timestep, dispersal))


def output_dispersal(nthreads: int, **kwargs):
    """This will calculate and output the geographic dispersal
       of the outbreak

       Parameters
       ----------
       network: Network
         The network over which the outbreak is being modelled
       population: Population
         The population experiencing the outbreak
       output_dir: OutputFiles
         The directory in which to place all output files
       workspace: Workspace
         A workspace that can be used to extract data
       kwargs
         Extra arguments that are ignored by this function
    """
    call_function_on_network(nthreads=1,
                             func=output_dispersal_serial,
                             call_on_overall=True,
                             **kwargs)
