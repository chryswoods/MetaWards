
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

    RESULTS.write(f"fingerprint,repeat,{varnames}"
                  f"day,{datestring}S,E,I,R,IW,UV\n")
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

            RESULTS.write(f"{start}{pop.day},{d}{pop.susceptibles},"
                          f"{pop.latent},{pop.total},"
                          f"{pop.recovereds},{pop.n_inf_wards},"
                          f"{pop.scale_uv}\n")
