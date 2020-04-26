
from array import array
import os

from .._network import Network
from .._infections import Infections

__all__ = ["allocate_vaccination",
           "how_many_vaccinated", "vaccinate_same_id"]


def allocate_vaccination(network: Network, output_dir: str):
    """Allocate memory and open files needed to track vaccination"""

    null_int = (network.nnodes+1) * [0]
    null_float = (network.nnodes+1) * [0.0]

    int_t = "i"
    float_t = "d"

    vac = array(int_t, null_int)
    wards_ra = array(int_t, null_int)
    risk_ra = array(float_t, null_float)
    sort_ra = array(int_t, null_int)
    VACF = open(os.path.join(output_dir, "Vaccinated.dat", "w"))

    trigger = 0

    return (vac, wards_ra, risk_ra, sort_ra, VACF, trigger)


def how_many_vaccinated(vac):
    raise AssertionError("how_many_vaccinated has not yet been written")


def vaccinate_same_id(network: Network, risk_ra, sort_ra,
                      infections: Infections,
                      vac, params):
    raise AssertionError("vaccinate_same_id has not yet been written")
