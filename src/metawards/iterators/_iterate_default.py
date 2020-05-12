
from typing import List as _List
from ..utils._get_functions import MetaFunction

__all__ = ["iterate_default"]


def iterate_default(stage: str, **kwargs) -> _List[MetaFunction]:
    """This returns the default list of 'advance_XXX' functions that
       are called in sequence for each iteration of the model run.
       This is the default iterator. It models every day as though
       it is a working day.

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
        from ._setup_imports import setup_seed_wards
        from ._advance_additional import setup_additional_seeds

        return [setup_seed_wards, setup_additional_seeds]

    elif stage == "setup":
        from ._advance_additional import advance_additional
        return [advance_additional]

    elif stage == "foi":
        from ._advance_foi import advance_foi
        from ._advance_recovery import advance_recovery
        return [advance_foi, advance_recovery]

    elif stage == "infect":
        from ._iterate_weekday import iterate_weekday
        return iterate_weekday(**kwargs)

    else:
        # we don't do anything at the "analyse" or "finalise" stages
        return []
