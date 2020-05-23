
from typing import Union as _Union

from .._network import Network
from .._networks import Networks
from .._population import Population
from .._infections import Infections

__all__ = ["setup_seed_specified_ward",
           "setup_seed_all_wards",
           "setup_seed_wards"]


def setup_seed_specified_ward(network: _Union[Network, Networks],
                              infections: Infections,
                              **kwargs):
    """Setup function that sets up the Network by seeding the infection
       at the ward specified by looking up the ward index
       from network.to_seed using index params.ward_seed_index

       Parameters
       ----------
       network: Network or Networks
         The network to be seeded
       infections: Infections
         Space to hold the 'work' infections
       kwargs
         Arguments that are not used by this setup function
    """
    if isinstance(network, Networks):
        # only seed the overall ward
        raise NotImplementedError(
            "Seeding a specific ward for a multi-demographic Network is "
            "not yet supported. If you need this please raise an issue "
            "at https://github.com/metawards/MetaWards/issues and we will "
            "work as quickly as we can to implement it.")

    wards = network.nodes
    links = network.links
    params = network.params

    play_infections = infections.play
    infections = infections.work

    seed_index = int(params.ward_seed_index)
    seed = network.to_seed[seed_index]

    from ._console import Console

    Console.print(f"Setup by seeding the ward at index {seed}")

    j = 0

    while (links.ito[j] != seed) or (links.ifrom[j] != seed):
        j += 1

    if links.suscept[j] < params.initial_inf:
        wards.play_suscept[seed] -= params.initial_inf
        play_infections[0][seed] += params.initial_inf

    infections[0][j] = params.initial_inf
    links.suscept[j] -= params.initial_inf


def setup_seed_all_wards(network: _Union[Network, Networks],
                         population: Population,
                         infections: Infections,
                         **kwargs):
    """Seed the wards with an initial set of infections, assuming
       an 'expected' number of infected people out of a population
       of 'population', based on the number of daily imports held
       in params.daily_imports
    """
    if isinstance(network, Networks):
        if network.overall.params.daily_imports == 0:
            return

        raise NotImplementedError(
            "Daily seeding of a multi-demographic network is not yet "
            "supported. If you need this, please raise an issue on "
            "https://github.com/metawards/MetaWards/issues and we will "
            "work as quickly as we can to implement it.")

    wards = network.nodes
    params = network.params

    if params.daily_imports == 0:
        return

    play_infections = infections.play
    infections = infections.work

    from ._console import Console
    Console.print(f"Setup by seeding all wards")

    frac = float(params.daily_imports) / float(population.initial)

    for i in range(0, network.nnodes+1):  # 1-index but also count at 0?
        temp = wards.denominator_n[i] + wards.denominator_p[i]
        to_seed = int(frac*temp + 0.5)
        wards.play_suscept[i] -= to_seed
        play_infections[0][i] += to_seed


def setup_seed_wards(network: Network,
                     **kwargs):
    """Seed the wards with an initial infection. If a specific ward
       has been highlighted via `params.ward_seed_index`, then this
       will be seeded using the function `setup_seed_specified_ward`.
       Otherwise, all wards will be seeded via `setup_seed_all_wards`.

       Parameters
       ----------
       network: Network
         The network over which the model will run
       kwargs
         Arguments not needed for this function
    """

    params = network.params

    try:
        seed_index = int(params.ward_seed_index)
    except Exception:
        seed_index = None

    if seed_index is None:
        setup_seed_all_wards(network=network,
                             **kwargs)
    else:
        setup_seed_specified_ward(network=network,
                                  **kwargs)
