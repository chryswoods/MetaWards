
from dataclasses import dataclass as _dataclass

from typing import Union as _Union

from ._variableset import VariableSet
from ._network import Network
from ._disease import Disease
from ._inputfiles import InputFiles

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

    #: The network that describes the workers and player that are part
    #: of this demographic. If this is None then the entire population
    #: network will be used (scaled by "work_ratio" and "play_ratio")
    network: InputFiles = None

    def __init__(self, name: str = None, work_ratio: float = None,
                 play_ratio: float = None, adjustment: VariableSet = None,
                 disease: _Union[str, Disease] = None,
                 network: _Union[str, InputFiles] = None):
        """Construct the Demographics"""
        if name is None:
            self.name = "default"
        else:
            self.name = name

        if disease is not None:
            if isinstance(disease, Disease):
                self.disease = disease
            else:
                self.disease = Disease.load(disease)

        if network is None:
            if work_ratio is None:
                self.work_ratio = 0.0
            else:
                self.work_ratio = float(work_ratio)

            if play_ratio is None:
                self.play_ratio = 0.0
            else:
                self.play_ratio = float(play_ratio)
        else:
            if work_ratio is None:
                self.work_ratio = 1.0
            else:
                self.work_ratio = float(work_ratio)

            if play_ratio is None:
                self.play_ratio = 1.0
            else:
                self.play_ratio = float(play_ratio)

            if isinstance(network, InputFiles):
                self.network = network
            else:
                self.network = InputFiles.load(network)

        self.adjustment = adjustment

    def __str__(self):
        parts = []

        if self.name is not None:
            parts.append(f"name='{self.name}'")

        if self.work_ratio != 1.0:
            parts.append(f"work_ratio={self.work_ratio}")

        if self.play_ratio != 1.0:
            parts.append(f"play_ratio={self.play_ratio}")

        if self.adjustment is not None:
            parts.append(f"adjustment={self.adjustment}")

        if self.disease is not None:
            parts.append(f"disease={self.disease.__repr__()}")

        if self.network is not None:
            parts.append(f"network='{self.network.__repr__()}'")

        return f"Demographic({', '.join(parts)})"

    def __repr__(self):
        return str(self)

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
