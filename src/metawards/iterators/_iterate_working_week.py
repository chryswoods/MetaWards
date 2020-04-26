
__all__ = ["iterate_working_week"]

from ._iterate_weekday import iterate_weekday
from ._iterate_weekend import iterate_weekend

from .._population import Population


def iterate_working_week(population: Population, **kwargs):
    """This returns the default list of 'advance_XXX' functions that
       are called in sequence for each iteration of the model run.
       This iterator understands the concept of a traditional working week,
       namely Monday-Friday is a work day, while Saturday and
       Sunday are weekends

       Parameters
       ----------
       population: Population
         The population experiencing the outbreak. This includes
         information about the day and date of the outbreak

       Returns
       -------
       funcs: List[function]
         The list of functions that ```iterate``` will call in sequence
    """

    kwargs["population"] = population

    # is this a weekday or a weekend?
    if population.date is None:
        # have to guess from the day - assume day zero was a Monday
        day = population.day % 7
        # 0-4 is a weekday, 5 and 6 are weekend
        is_weekend = (day >= 5)
    else:
        day = population.date.weekday()
        # 0-4 is a weekday, 5 and 6 are weekend
        is_weekend = (day >= 5)

    if is_weekend:
        return iterate_weekend(**kwargs)
    else:
        return iterate_weekday(**kwargs)
