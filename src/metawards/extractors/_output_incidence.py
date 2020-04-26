
from .._population import Population
from .._outputfiles import OutputFiles

from ..utils._workspace import Workspace

__all__ = ["output_incidence"]


def output_incidence(population: Population,
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

    pfile = output_dir.open("incidence.dat")

    pfile.write(str(population.day) + " ")

    pfile.write(" ".join([str(x) for x in workspace.incidence[1:]])
                + "\n")
