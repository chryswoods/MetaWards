
from dataclasses import dataclass as _dataclass

from ._variableset import VariableSet
from ._network import Network
from ._disease import Disease

__all__ = ["Demographic"]


@_dataclass
class Demographic:
    """This class represents a single demographic"""

    #: The name of this demographic. This will be used as a label,
    #: and should be unique within the Demographics
    name: str = None

    #: The proportion of "work" (fixed movement) members in this
    #: demographic out of the entire population. This can either
    #: be a single number, or a list with a value for every ward.
    #: Whichever way is used, the sum of "work_ratio" for each demographic
    #: must equal 1.0 in each ward (every member of the work population
    #: must be represented)
    work_ratio: float = 0.0

    #: The proportion of "play" (random movement) members in this
    #: demographic out of the entire population. This can also either
    #: be a single number, or a list with a value for every ward.
    #: Whichever way is used, the sum of "play_ratio" for each demographic
    #: must equal 1.0 in each ward (every member of the play population
    #: must be represented)
    play_ratio: float = 0.0

    #: How the parameters for this demographic should be changed compared
    #: to the parameters used for the whole population. This is currently
    #: changed to fixed values, but future developments in VariableSet
    #: will support rules for varying relative to the whole population.
    #: If this is None then this demographic will have the same
    #: parameters as the whole population
    adjustment: VariableSet = None

    #: The Disease that should be used for this demographic. Is this
    #: is None, then the global Disease is used. Otherwise
    #: this demographic will follow this Disease
    disease: Disease = None

    def specialise(self, network: Network, profiler=None,
                   nthreads: int = 1):
        """Return a copy of the passed network that has been specialised
           for this demographic. The returned network will
           contain only members of this demographic, with the
           parameters of the network adjusted according to the rules
           of this demographic

           Parameters
           ----------
           network: Network
             The network to be specialised

           Returns
           -------
           network: Network
             The specialised network
        """
        # Start by making a shallow copy of all elements - I really do
        # only want the immediate children of the network to be copied.
        # I will then change what is needed in deep copies - this should
        # save memory for things that don't change
        import copy
        subnet = copy.copy(network)

        # Now create safe copies of the nodes and links. This will
        # shallow copy what it can, and will deep copy variables
        # that will change during a model run
        subnet.nodes = network.nodes.copy()
        subnet.links = network.links.copy()
        subnet.play = network.play.copy()

        # Now we need to adjust the number of susceptibles in each
        # ward according to work_ratio and play_ratio
        subnet.scale_susceptibles(work_ratio=self.work_ratio,
                                  play_ratio=self.play_ratio)

        if self.name in network.params.specialised_demographics():
            subnet.params = network.params[self.name].copy()
        else:
            subnet.params = network.params.copy()

        # Does this demographic have a custom disease pathway?
        if self.disease is not None:
            subnet.params.disease_params = self.disease

        # Do we need to specialise the parameters for this demographic?
        if self.adjustment is not None:
            subnet.params = subnet.params.set_variables(self.adjustment)

        subnet.name = self.name

        subnet.reset_everything(nthreads=nthreads, profiler=profiler)
        subnet.rescale_play_matrix(nthreads=nthreads, profiler=profiler)
        subnet.move_from_play_to_work(nthreads=nthreads, profiler=profiler)

        return subnet
