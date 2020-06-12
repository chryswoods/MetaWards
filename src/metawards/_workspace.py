
from dataclasses import dataclass as _dataclass
from typing import List as _List
from typing import Union as _Union

from ._network import Network
from ._networks import Networks

__all__ = ["Workspace"]


@_dataclass
class Workspace:
    """This class provides a workspace for the running calculation.
       This pre-allocates all of the memory into arrays, which
       can then be used via cython memory views
    """
    #: Number of disease classes (stages)
    n_inf_classes: int = 0

    #: Number of wards (nodes)
    nnodes: int = 0

    #: Size of population in each disease stage for work infections
    inf_tot: _List[int] = None
    #: Size of population in each disease stage for play infections
    pinf_tot: _List[int] = None
    #: Number of wards with at least one individual in this disease stage
    n_inf_wards: _List[int] = None

    #: Size of population in each disease stage in each ward
    ward_inf_tot: _List[_List[int]] = None

    #: Total number of infections in each ward over the last day
    #: This is also equal to the prevalence
    total_inf_ward: _List[int] = None

    #: Number of new infections in each ward over the last day
    total_new_inf_ward: _List[int] = None

    #: The incidence of the infection (sum of infections up to
    #: disease_class == I_start)
    incidence: _List[int] = None

    #: The size of the S population in each ward
    S_in_wards: _List[int] = None

    #: The size of the E population in each ward
    E_in_wards: _List[int] = None

    #: The size of the I population in each ward
    I_in_wards: _List[int] = None

    #: The size of the R population in each ward
    R_in_wards: _List[int] = None

    #: The sub-workspaces used for the subnets of a
    #: multi-demographic Networks (list[Workspace])
    subspaces = None

    @staticmethod
    def build(network: _Union[Network, Networks]):
        """Create the workspace needed to run the model for the
           passed network
        """
        params = network.params

        workspace = Workspace()

        if isinstance(network, Network):
            n_inf_classes = params.disease_params.N_INF_CLASSES()

            workspace.n_inf_classes = params.disease_params.N_INF_CLASSES()
            workspace.nnodes = network.nnodes

            size = workspace.nnodes + 1  # 1-indexed

            from .utils._array import create_int_array

            workspace.inf_tot = create_int_array(n_inf_classes, 0)
            workspace.pinf_tot = create_int_array(n_inf_classes, 0)
            workspace.n_inf_wards = create_int_array(n_inf_classes, 0)

            workspace.total_inf_ward = create_int_array(size, 0)
            workspace.total_new_inf_ward = create_int_array(size, 0)
            workspace.incidence = create_int_array(size, 0)

            workspace.S_in_wards = create_int_array(size, 0)
            workspace.E_in_wards = create_int_array(size, 0)
            workspace.I_in_wards = create_int_array(size, 0)
            workspace.R_in_wards = create_int_array(size, 0)

            workspace.ward_inf_tot = []

            for i in range(0, n_inf_classes):
                workspace.ward_inf_tot.append(create_int_array(size, 0))

        elif isinstance(network, Networks):
            workspace = Workspace.build(network.overall)

            subspaces = []

            for subnet in network.subnets:
                subspaces.append(Workspace.build(subnet))

            workspace.subspaces = subspaces

        return workspace

    def zero_all(self, zero_subspaces=True):
        """Reset the values of all of the arrays to zero.
           By default we zero the subspace networks
           (change this by setting zero_subspaces to False)
        """
        from .utils._zero_workspace import zero_workspace
        zero_workspace(self)

        if zero_subspaces and self.subspaces is not None:
            for subspace in self.subspaces:
                subspace.zero_all()
