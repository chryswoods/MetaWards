
cimport cython

from ._network import Network
from ._parameters import Parameters

from ._ran_binomial cimport _ran_binomial, _get_binomial_ptr, binomial_rng

__all__ = ["import_infection"]


@cython.boundscheck(False)
@cython.wraparound(False)
def import_infection(network: Network, infections, play_infections,
                     params: Parameters, rng,
                     population: int):

    cdef binomial_rng* r = _get_binomial_ptr(rng)

    links = network.to_links
    wards = network.nodes

    frac = float(params.daily_imports) / float(population)

    total = 0

    for i in range(0, network.nnodes+1):
        to_seed = _ran_binomial(r, frac, int(wards.play_suscept[i]))

        if to_seed > 0:
            wards.play_suscept[i] -= to_seed
            play_infections[0][i] += to_seed
            total += to_seed

    for i in range(0, network.nlinks+1):
        # workers
        to_seed = _ran_binomial(r, frac, int(links.suscept[i]))

        if to_seed > 0:
            links.suscept[i] -= to_seed
            infections[0][i] += to_seed
            total += to_seed

    return total
