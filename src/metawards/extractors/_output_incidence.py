
from .._network import Network
from .._population import Population
from .._outputfiles import OutputFiles

from .._workspace import Workspace
from ..utils._get_functions import call_function_on_network

__all__ = ["output_incidence", "output_incidence_serial"]


def output_incidence_serial(network: Network,
                            population: Population,
                            output_dir: OutputFiles,
                            workspace: Workspace,
                            **kwargs):
    """This will incidence of infection for each ward for each timestep.
       This is the sum of infections from disease class 0 to 2 inclusive

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

    pfile = output_dir.open(f"incidence{name}.dat")

    pfile.write(str(population.day) + " ")

    pfile.write(" ".join([str(x) for x in workspace.incidence[1:]])
                + "\n")


def output_incidence(nthreads: int = 1, **kwargs):
    """This will incidence of infection for each ward for each timestep.
       This is the sum of infections from disease class 0 to 2 inclusive

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
                             func=output_incidence_serial,
                             call_on_overall=True,
                             **kwargs)
