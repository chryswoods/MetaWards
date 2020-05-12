
from typing import List as _List
from ..utils._get_functions import MetaFunction

__all__ = ["extract_default"]


def extract_default(stage: str, **kwargs) -> _List[MetaFunction]:
    """This returns the default list of 'output_XXX' functions that
       are called in sequence for each iteration of the model run.
       These functions are used to output data to files for
       future processing

       Parameters
       ----------
       stage: str
         Which stage of the day is to be modelled

       Returns
       -------
       funcs: List[MetaFunction]
         The list of functions that will be called in sequence
    """

    if stage == "initialise":
        from ._output_core import setup_core, output_core
        return [setup_core, output_core]

    elif stage == "infect":
        # this must be called at the end of the 'infect' stage to
        # accumulate all of the new infections
        from ._output_core import output_core
        return [output_core]

    elif stage == "analyse":
        from ._output_basic import output_basic
        from ._output_dispersal import output_dispersal
        from ._output_incidence import output_incidence
        from ._output_prevalence import output_prevalence

        return [output_basic, output_dispersal,
                output_incidence, output_prevalence]

    elif stage == "finalise":
        from ._output_trajectory import output_trajectory
        return [output_trajectory]

    elif stage == "summary":
        # output the summary results.csv.bz2 file
        from ._output_final_report import output_final_report
        return [output_final_report]

    else:
        # we don't do anything at the "foi", "analyse" or "finalise" stages
        return []
