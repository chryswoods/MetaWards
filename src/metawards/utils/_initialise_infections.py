

from .._network import Network
from ._array import create_int_array

__all__ = ["initialise_infections",
           "initialise_play_infections"]


def initialise_infections(network: Network):
    """Initialise the data structure used to store the infections"""

    params = network.params

    if params is None:
        return None

    disease = params.disease_params

    n = disease.N_INF_CLASSES()

    infections = []

    # 'infections' holds all of the infections recorded for every
    # single link in network.links. 1-indexing is used throughout
    # the code, hence why we size for n + 1
    for _ in range(0, n):
        infections.append(create_int_array(network.nlinks + 1))

    return infections


def initialise_play_infections(network: Network):
    """Initialise the space used to store the play infections"""

    params = network.params

    if params is None:
        return None

    disease = params.disease_params

    n = disease.N_INF_CLASSES()

    infections = []

    # the 'play_infections' holds the infections that occur in
    # each ward (node) according to the 'play' rules. 1-indexing
    # is used throughout the code, hence why we size for n + 1
    for _ in range(0, n):
        infections.append(create_int_array(network.nnodes+1))

    return infections
