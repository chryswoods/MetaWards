
from .._network import Network
from .._population import Population
from .._outputfiles import OutputFiles
from ..utils import Workspace

__all__ = ["output_basic"]


def output_basic(network: Network, population: Population,
                 output_dir: OutputFiles,
                 workspace: Workspace,
                 **kwargs):
    """This will write basic trajectory data to the output
       files. This will be the number of infected wards,
       total infections, play infections and work infections
       for each disease stage for each timestep

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

    # get the file handles - this will open the files if
    # they have not already been created
    n_inf_wards_file = output_dir.open("NumberWardsInfected.dat")
    total_file = output_dir.open("TotalInfections.dat")
    work_file = output_dir.open("WorkInfections.dat")
    play_file = output_dir.open("PlayInfections.dat")

    ts = f"{population.day} "

    def _join(array):
        return " ".join([str(x) for x in array])

    total_file.write(str(population.total) + "\n")

    n_inf_wards_file.write(ts + _join(workspace.n_inf_wards) + "\n")
    work_file.write(ts + _join(workspace.inf_tot) + "\n")
    play_file.write(ts + _join(workspace.pinf_tot) + "\n")
