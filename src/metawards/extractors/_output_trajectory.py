
from typing import Union as _Union

from .._network import Network
from .._networks import Networks
from .._population import Populations
from .._outputfiles import OutputFiles

__all__ = ["output_trajectory"]


def output_trajectory(network: _Union[Network, Networks],
                      output_dir: OutputFiles,
                      trajectory: Populations,
                      **kwargs) -> None:
    """Call in the "finalise" stage to output the
       population trajectory to the 'trajectory.csv' file
    """

    RESULTS = output_dir.open("trajectory.csv")

    has_date = trajectory[0].date

    if has_date:
        datestring = "date,"
    else:
        datestring = ""

    RESULTS.write(f"day,{datestring}demographic,S,E,I,R,IW\n")

    for i, pop in enumerate(trajectory):
        if pop.date:
            d = pop.date.isoformat() + ","
        else:
            d = ""

        RESULTS.write(f"{pop.day},{d}overall,{pop.susceptibles},"
                      f"{pop.latent},{pop.total},"
                      f"{pop.recovereds},{pop.n_inf_wards}\n")

        if isinstance(network, Networks):
            for i, demographic in enumerate(network.demographics):
                subpop = pop.subpops[i]
                name = demographic.name

                if name is None or len(name) == 0:
                    name = str(i)

                RESULTS.write(f"{subpop.day},{d}{name},{subpop.susceptibles},"
                              f"{subpop.latent},{subpop.total},"
                              f"{subpop.recovereds},{subpop.n_inf_wards}\n")
