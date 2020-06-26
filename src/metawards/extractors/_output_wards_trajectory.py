
from .._network import Network
from .._population import Population
from .._outputfiles import OutputFiles
from .._workspace import Workspace

from ..utils._get_functions import call_function_on_network

__all__ = ["output_wards_trajectory", "output_wards_trajectory_serial"]


def output_wards_trajectory_serial(network: Network,
                                   population: Population,
                                   output_dir: OutputFiles,
                                   workspace: Workspace,
                                   **kwargs):
    """This will output the complete trajectory for
       S, E, I and R for each of the wards in the model.
       This may take a lot of disk space (10's MBs).

       The files are written to name "wards_trajectory_X.dat",
       where "X" is one of S, E, I or R

       Parameters
       ----------
       population: Population
         Model population - used to get the day
       output_dir: OutputFiles
         Where to place the output files
       workspace: Workspace
         Workspace containing the raw data
       **kwargs:
         Other arguments not needed by this function
    """

    if network.name is None:
        name = ""
    else:
        name = "_" + network.name.replace(" ", "_")

    day = str(population.day) + " "

    if workspace.S_in_wards is not None:
        S_file = output_dir.open(f"wards_trajectory{name}_S.dat")
        S_file.write(day)
        S_file.write(" ".join([str(x) for x in workspace.S_in_wards[1:]]))
        S_file.write("\n")

    if workspace.E_in_wards is not None:
        E_file = output_dir.open(f"wards_trajectory{name}_E.dat")
        E_file.write(day)
        E_file.write(" ".join([str(x) for x in workspace.E_in_wards[1:]]))
        E_file.write("\n")

    if workspace.I_in_wards is not None:
        I_file = output_dir.open(f"wards_trajectory{name}_I.dat")
        I_file.write(day)
        I_file.write(" ".join([str(x) for x in workspace.I_in_wards[1:]]))
        I_file.write("\n")

    if workspace.R_in_wards is not None:
        R_file = output_dir.open(f"wards_trajectory{name}_R.dat")
        R_file.write(day)
        R_file.write(" ".join([str(x) for x in workspace.R_in_wards[1:]]))
        R_file.write("\n")

    if workspace.X_in_wards is not None:
        for key, value in workspace.X_in_wards.items():
            X_file = output_dir.open(
                f"wards_trajectory{name}_{key.replace(' ','-')}.dat")
            X_file.write(day)
            X_file.write(" ".join([str(x) for x in value[1:]]))
            X_file.write("\n")


def output_wards_trajectory(nthreads: int = 1, **kwargs):
    """This will output the complete trajectory for
       S, E, I and R for each of the wards in the model.
       This may take a lot of disk space (10's MBs).

       The files are written to name "wards_trajectory_X.dat",
       where "X" is one of S, E, I or R

       Parameters
       ----------
       population: Population
         Model population - used to get the day
       output_dir: OutputFiles
         Where to place the output files
       workspace: Workspace
         Workspace containing the raw data
       **kwargs:
         Other arguments not needed by this function
    """
    call_function_on_network(nthreads=1,
                             func=output_wards_trajectory_serial,
                             call_on_overall=True,
                             **kwargs)
