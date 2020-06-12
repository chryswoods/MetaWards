
from dataclasses import dataclass as _dataclass
from typing import Union as _Union

from ._network import Network
from ._networks import Networks
from ._disease import Disease

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

    #: The mapping from disease state 'i' in this network to
    #: disease stage 'j' in the overall network. This is used if
    #: the disease states in this subnetwork are different to the
    #: overall network
    _stage_mapping = None

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
    def build(network: _Union[Network, Networks] = None,
              overall: Network = None):
        """Construct and return the Infections object that will track
           infections during a model run on the passed Network (or Networks)

           Parameters
           ----------
           network: Network or Networks
             The network or networks that will be run
           overall: Network
             The overall network to which this subnet belongs

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

            if overall is not None:
                inf._set_stage_mapping(network.params.disease_params,
                                       overall.params.disease_params)

            return inf

        elif isinstance(network, Networks):
            inf = Infections.build(network.overall)

            subinfs = []

            for subnet in network.subnets:
                subinf = Infections.build(subnet, overall=network)
                subinfs.append(subinf)

            inf.subinfs = subinfs

            return inf

    def _set_stage_mapping(self, disease_params: Disease,
                           overall_params: Disease):
        """Get the mapping from the disease stages for this sub-network
           (from disease_params) to the disease stages for the
           overall network (in overall_params)
        """
        if disease_params == overall_params:
            self._stage_mapping = None
            return
        else:
            self._stage_mapping = disease_params.get_mapping_to(overall_params)

    def has_different_stage_mapping(self):
        """Return whether or not the sub-network disease stages
           are different to that of the overall network, and must
           thus be mapped
        """
        return self._stage_mapping is not None

    def get_stage_mapping(self):
        """Return the mapping from disease stages in this sub-network
           to disease stages in the overall network. This returns a list
           where mapping[i] gives the index of stage i in the subnetwork
           to stage j in the overall network
        """
        if self.has_different_stage_mapping():
            return self._stage_mapping
        else:
            return range(0, self.N_INF_CLASSES)

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
