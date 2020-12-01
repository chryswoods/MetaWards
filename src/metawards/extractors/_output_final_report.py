
from .._outputfiles import OutputFiles

__all__ = ["output_final_report"]


def output_final_report(output_dir: OutputFiles,
                        results, **kwargs) -> None:
    """Call in the "finalise" stage to output the final
       report of the population trajectory to
       'results.csv'
    """

    RESULTS = output_dir.open("results.csv")

    from ..utils._console import Console

    Console.panel(f"""
Writing a summary of all results into the csv file
**{output_dir.get_filename('results.csv')}**. You can use this to quickly
look at statistics across all runs using e.g. R or pandas""",
                  markdown=True, style="alternate")

    varnames = results[0][0].variable_names()

    if varnames is None or len(varnames) == 0:
        varnames = ""
    else:
        varnames = ",".join(varnames) + ","

    has_date = results[0][1][0].date

    if has_date:
        datestring = "date,"
    else:
        datestring = ""

    # get the first Population in the trajectory, as this will give
    # us the list of extra disease stages to print out
    t0 = results[0][-1][0]

    totals = {} if t0.totals is None else t0.totals
    other_totals = {} if t0.other_totals is None else t0.other_totals

    extra_stages = list(totals.keys()) + list(other_totals.keys())

    if len(extra_stages) > 0:
        extra_str = ",".join(extra_stages) + ","
    else:
        extra_str = ""

    def _int(val):
        return val if val is not None else 0

    RESULTS.write(f"fingerprint,repeat,{varnames}"
                  f"day,{datestring}S,E,I,{extra_str}R,IW,SCALE_UV\n")
    for varset, trajectory in results:
        varvals = varset.variable_values()
        if varvals is None or len(varvals) == 0:
            varvals = ""
        else:
            varvals = ",".join(map(str, varvals)) + ","

        start = f"{varset.fingerprint()}," \
                f"{varset.repeat_index()},{varvals}"

        for i, pop in enumerate(trajectory):
            if pop.date:
                d = pop.date.isoformat() + ","
            else:
                d = ""

            totals = {} if pop.totals is None else pop.totals
            other_totals = {} if pop.other_totals is None else pop.other_totals

            if len(extra_stages) > 0:
                extra_vals = []

                for stage in extra_stages:
                    if stage in totals:
                        extra_vals.append(str(totals[stage]))
                    elif stage in other_totals:
                        extra_vals.append(str(other_totals[stage]))
                    else:
                        extra_vals.append("0")

                extra_str = ",".join(extra_vals) + ","
            else:
                extra_str = ""

            RESULTS.write(f"{start}{pop.day},{d}{_int(pop.susceptibles)},"
                          f"{_int(pop.latent)},{_int(pop.total)},{extra_str}"
                          f"{_int(pop.recovereds)},{_int(pop.n_inf_wards)},"
                          f"{_int(pop.scale_uv)}\n")
