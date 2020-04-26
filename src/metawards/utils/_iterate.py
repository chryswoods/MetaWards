
from .._network import Network
from .._population import Population
from .._infections import Infections

from ._profiler import Profiler, NullProfiler

__all__ = ["iterate"]


def iterate(network: Network, population: Population,
            infections: Infections,
            rngs, nthreads: int,
            get_advance_functions,
            profiler: Profiler = None):
    """Advance the infection by one day for the passed Network,
       acting on the passed Population.

       Parameters
       ----------
       network: Network
         The network in which the disease outbreak will be modelled
       population: Population
         The population experiencing the outbreak. This contains
         an overview of the current population, plus the day and
         date of the outbreak
       infections: Infections
         Space in which the infections are recorded
       rngs
         List of the thread-safe random number generators (one per thread)
       nthreads: int
         The number of threads over which to parallelise the calculation
       get_advance_functions: function
         This is a function that should return the set of "advance_XXX"
         functions that will be applied as part of this iteration
       profiler: Profiler
         The profiler to use to profile this calculation. Pass "None"
         if you want to disable profiling
    """
    if profiler is None:
        profiler = NullProfiler()

    p = profiler.start("iterate")

    advance_functions = get_advance_functions(network=network,
                                              population=population,
                                              infections=infections,
                                              rngs=rngs, nthreads=nthreads,
                                              profiler=p)

    for advance_function in advance_functions:
        p = p.start(str(advance_function))
        advance_function(network=network,
                         population=population,
                         infections=infections,
                         rngs=rngs, nthreads=nthreads,
                         profiler=p)
        p = p.stop()

    p.stop()
