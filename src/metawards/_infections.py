
from dataclasses import dataclass as _dataclass
from typing import Union as _Union

from ._network import Network
from ._networks import Networks

__all__ = ["Infections"]


@_dataclass
class Infections:
    """This class holds the arrays that record the infections as they
       are occuring during the outbreak
    """

    #: The infections caused by fixed (work) movements. This is a list
    #: of int arrays, size work[N_INF_CLASSES][nlinks+1]
    work = None

    #: The infections caused by random (play) movements. This is a list
    #: of int arrays, size play[N_INF_CLASSES][nnodes+1]
    play = None

    #: The infections for the multi-demographic subnets
    subinfs = None

    #: The index in the overall network's work matrix of the ith
    #: index in this subnetworks work matrix. If this is None then
    #: both this subnetwork has the same work matrix as the overall
    #: network
    _work_index = None

    @property
    def N_INF_CLASSES(self) -> int:
        """The total number of stages in the disease"""
        if self.work is not None:
            return len(self.work)
        else:
            return 0

    @property
    def nnodes(self) -> int:
        """The total number of nodes (wards)"""
        if self.play is not None and len(self.play) > 0:
            return len(self.play[0]) - 1    # 1-indexed
        else:
            return 0

    @property
    def nlinks(self) -> int:
        """Return the number of work links"""
        if self.work is not None and len(self.work) > 0:
            return len(self.work[0]) - 1    # 1-indexed
        else:
            return 0

    @property
    def nsubnets(self) -> int:
        """Return the number of demographic subnetworks"""
        if self.subinfs is not None:
            return len(self.subinfs)
        else:
            return 0

    @staticmethod
    def build(network: _Union[Network, Networks] = None):
        """Construct and return the Infections object that will track
           infections during a model run on the passed Network (or Networks)

           Parameters
           ----------
           network: Network or Networks
             The network or networks that will be run

           Returns
           -------
           infections: Infections
             The space for the work and play infections for the network
             (including space for all of the demographics)
        """
        from .utils import initialise_infections, initialise_play_infections

        if isinstance(network, Network):
            inf = Infections()
            inf.work = initialise_infections(network=network)
            inf.play = initialise_play_infections(network=network)

            inf._ifrom = network.links.ifrom
            inf._ito = network.links.ito

            return inf

        elif isinstance(network, Networks):
            inf = Infections.build(network.overall)

            subinfs = []

            for subnet in network.subnets:
                subinfs.append(Infections.build(subnet))

            inf.subinfs = subinfs

            return inf

    def has_different_work_matrix(self):
        """Return whether or not the sub-network work matrix
           is different to that of the overall network
        """
        return self._work_index is not None

    def get_work_index(self):
        """Return the mapping from the index in this sub-networks work
           matrix to the mapping in the overall network's work matrix
        """
        if self.has_different_work_matrix():
            # remember this is 1-indexed, so work_index[1] is the first
            # value
            return self._work_index
        else:
            return range(1, self.nlinks + 1)

    def aggregate(self, profiler=None, nthreads: int = 1) -> None:
        """Aggregate all of the infection data from the demographic
           sub-networks

           Parameters
           ----------
           network: Network
               Network that was used to initialise these infections
           profiler : Profiler, optional
               Profiler used to profile the calculation, by default None
           nthreads : int, optional
               Number of threads to use, by default 1
        """
        from .utils._aggregate import aggregate_infections
        aggregate_infections(infections=self, profiler=profiler,
                             nthreads=nthreads)

    def clear(self, nthreads: int = 1):
        """Clear all of the infections (resets all to zero)

           Parameters
           ----------
           nthreads: int
             Optionally parallelise this reset by specifying the number
             of threads to use
        """
        from .utils import clear_all_infections
        clear_all_infections(infections=self.work,
                             play_infections=self.play,
                             nthreads=nthreads)

        if self.subinfs is not None:
            for subinf in self.subinfs:
                subinf.clear(nthreads=nthreads)
