
from dataclasses import dataclass as _dataclass

from ._network import Network

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

    @staticmethod
    def build(network: Network):
        """Construct and return the Infections object that will track
           infections during a model run on the passed Network
        """
        from .utils import initialise_infections, initialise_play_infections

        inf = Infections()
        inf.work = initialise_infections(network=network)
        inf.play = initialise_play_infections(network=network)

        return inf

    def clear(self, nthreads: int = 1):
        """Clear all of the infections (resets all to zero)

           Parameters
           ----------
           nthreads: int
             Optionally parallelise this reset by specifying the number
             of threads to use
        """
        from .utils import clear_all_infections
        clear_all_infections(infections=self, nthreads=nthreads)
