
from .._population import Population
from .._outputfiles import OutputFiles

from ..utils._workspace import Workspace

__all__ = ["output_prevalence"]


def output_prevalence(population: Population,
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

    pfile = output_dir.open("prevalence.dat")

    pfile.write(str(population.day) + " ")

    pfile.write(" ".join([str(x) for x in workspace.total_inf_ward[1:]])
                + "\n")
