
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

    # get the first Population in the trajectory, as this will give
    # us the list of extra disease stages to print out
    t0 = trajectory[0]

    if t0.totals is None:
        extra_stages = []
        extra_str = ""
    else:
        extra_stages = list(t0.totals.keys())
        extra_str = ",".join(extra_stages) + ","

    RESULTS.write(f"day,{datestring}demographic,S,E,I,{extra_str}R,IW\n")

    for i, pop in enumerate(trajectory):
        if pop.date:
            d = pop.date.isoformat() + ","
        else:
            d = ""

        if len(extra_stages) > 0:
            extra_vals = []

            for stage in extra_stages:
                if pop.totals is None:
                    extra_vals.append("0")
                else:
                    extra_vals.append(str(pop.totals.get(stage, 0)))

            extra_str = ",".join(extra_vals) + ","
        else:
            extra_str = ""

        def _int(val):
            return val if val is not None else 0

        RESULTS.write(f"{pop.day},{d}overall,{_int(pop.susceptibles)},"
                      f"{_int(pop.latent)},{_int(pop.total)},{extra_str}"
                      f"{_int(pop.recovereds)},{_int(pop.n_inf_wards)}\n")

        if isinstance(network, Networks):
            for i, demographic in enumerate(network.demographics):
                subpop = pop.subpops[i]
                name = demographic.name

                if name is None or len(name) == 0:
                    name = str(i)

                if len(extra_stages) > 0:
                    extra_vals = []

                    for stage in extra_stages:
                        if subpop.totals is None:
                            extra_vals.append("0")
                        else:
                            extra_vals.append(str(subpop.totals.get(stage, 0)))

                    extra_str = ",".join(extra_vals) + ","
                else:
                    extra_str = ""

                RESULTS.write(f"{subpop.day},{d}{name},"
                              f"{_int(subpop.susceptibles)},"
                              f"{_int(subpop.latent)},"
                              f"{_int(subpop.total)},{extra_str}"
                              f"{_int(subpop.recovereds)},"
                              f"{_int(subpop.n_inf_wards)}\n")
