
from .._network import Network
from .._population import Population
from .._outputfiles import OutputFiles

from .._workspace import Workspace

from ..utils._get_functions import call_function_on_network

__all__ = ["output_prevalence"]


def output_prevalence_serial(network: Network,
                             population: Population,
                             output_dir: OutputFiles,
                             workspace: Workspace,
                             **kwargs):
    """This will output the number of infections per ward per timestep
       as a (large) 2D matrix

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
         Extra argumentst that are ignored by this function
    """

    if network.name is None:
        name = ""
    else:
        name = "_" + network.name.replace(" ", "_")

    pfile = output_dir.open(f"prevalence{name}.dat")

    pfile.write(str(population.day) + " ")

    pfile.write(" ".join([str(x) for x in workspace.total_inf_ward[1:]])
                + "\n")


def output_prevalence(nthreads: int = 1, **kwargs):
    """This will output the number of infections per ward per timestep
       as a (large) 2D matrix

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
         Extra argumentst that are ignored by this function
    """
    call_function_on_network(nthreads=1,
                             func=output_prevalence_serial,
                             call_on_overall=True,
                             **kwargs)
