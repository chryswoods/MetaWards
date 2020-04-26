
from .._network import Network
from .._parameters import Parameters
from ._profiler import Profiler
from .._infections import Infections

__all__ = ["iterate_weekend"]


def iterate_weekend(network: Network, infections: Infections,
                    params: Parameters, rngs, timestep: int,
                    population: int, nthreads: int = None,
                    profiler: Profiler = None,
                    is_dangerous=None, SELFISOLATE: bool = False,
                    ):
    """Iterate the model forward one timestep (day) using the supplied
       network and parameters, advancing the supplied infections,
       and using the supplied random number generator (rngs)
       (array, with one generator per thread)
       to generate random numbers. This iterates for a non-working
       (weekend) day (with only random movements)

       If SELFISOLATE is True then you need to pass in
       is_dangerous, which should be an array("i", network.nnodes)
    """
    raise AssertionError("Will write iterate_weekend later...")
