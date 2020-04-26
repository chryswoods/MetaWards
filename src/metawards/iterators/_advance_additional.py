
from .._network import Network
from .._population import Population
from ..utils._profiler import Profiler
from .._infections import Infections

__all__ = ["setup_additional_seeds",
           "advance_additional",
           "advance_additional_serial",
           "advance_additional_omp"]


def _load_additional_seeds(filename: str):
    """Load additional seeds from the passed filename. This returns
       the added seeds
    """
    print(f"Loading additional seeds from {filename}...")

    with open(filename, "r") as FILE:
        line = FILE.readline()
        seeds = []

        while line:
            words = line.split()

            # yes, this is really the order of the seeds - "t num loc"
            # is in the file as "t loc num"
            seeds.append((int(words[0]), int(words[2]), int(words[1])))
            print(seeds[-1])
            line = FILE.readline()

    return seeds


# This is the global 'additional_seeds' that are loaded
# by 'setup_additional_seed' and used by 'advance_additional'
# This is a safe global as it is only used in this file scope
# and multiple runs are not performed in the same process in
# parallel
_additional_seeds = None


def setup_additional_seeds(network: Network,
                           profiler: Profiler,
                           **kwargs):
    """Setup function that reads in the additional seeds held
       in `params.additional_seeds` and puts them ready to
       be used by `advance_additional` to import additional
       infections at specified times in specified wards
       during the outbreak

       Parameters
       ----------
       network: Network
         The network to be seeded
       profiler: Profiler
         Profiler used to profile this function
       kwargs
         Arguments that are not used by this setup function
    """
    params = network.params

    p = profiler.start("load_additional_seeds")
    global _additional_seeds
    _additional_seeds = []

    if params.additional_seeds is not None:
        for additional in params.additional_seeds:
            _additional_seeds += _load_additional_seeds(additional)
    p = p.stop()


def advance_additional_serial(network: Network,
                              population: Population,
                              infections: Infections,
                              profiler: Profiler,
                              **kwargs):
    """Advance the infection by infecting additional wards based
       on a pre-determined pattern based on the additional seeds

       Parameters
       ----------
       network: Network
         The network being modelled
       population: Population
         The population experiencing the outbreak - also contains the day
         of the outbreak
       infections: Infections
         Space to hold the infections
       profiler: Profiler
         Used to profile this function
       kwargs
         Arguments that aren't used by this advancer
    """

    wards = network.nodes

    play_infections = infections.play
    infections = infections.work

    # The 'setup_additional_seeds' function should have loaded
    # all additional seeds into this global '_additional_seeds' variable
    global _additional_seeds

    p = profiler.start("additional_seeds")
    for seed in _additional_seeds:
        if seed[0] == population.day:
            if wards.play_suscept[seed[1]] < seed[2]:
                print(f"Not enough susceptibles in ward for seeding")
            else:
                wards.play_suscept[seed[1]] -= seed[2]
                print(f"seeding play_infections[0][{seed[1]}] += {seed[2]}")
                play_infections[0][seed[1]] += seed[2]
    p.stop()


def advance_additional_omp(**kwargs):
    """Advance the infection by infecting additional wards based
       on a pre-determined pattern based on the additional seeds
       (parallel version)

       Parameters
       ----------
       network: Network
         The network being modelled
       population: Population
         The population experiencing the outbreak - also contains the day
         of the outbreak
       infections: Infections
         Space to hold the infections
       profiler: Profiler
         Used to profile this function
       kwargs
         Arguments that aren't used by this advancer
    """
    kwargs["nthreads"] = 1
    advance_additional(**kwargs)


def advance_additional(nthreads, **kwargs):
    """Advance the infection by infecting additional wards based
       on a pre-determined pattern based on the additional seeds
       (parallel version)

       Parameters
       ----------
       network: Network
         The network being modelled
       population: Population
         The population experiencing the outbreak - also contains the day
         of the outbreak
       infections: Infections
         Space to hold the infections
       profiler: Profiler
         Used to profile this function
       kwargs
         Arguments that aren't used by this advancer
    """
    if nthreads == 1:
        advance_additional_serial(**kwargs)
    else:
        advance_additional_omp(nthreads=nthreads, **kwargs)
