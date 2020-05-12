
__all__ = ["iterate_weekend"]


def iterate_weekend(nthreads: int = 1, **kwargs):
    """This returns the default list of 'advance_XXX' functions that
       are called in sequence for each weekend iteration of the model run.

       Parameters
       ----------
       nthreads: int
         The number of threads that will be used for each function.
         If this is 1, then the serial versions of the functions will
         be returned, else the parallel (OpenMP) versions will be
         returned

       Returns
       -------
       funcs: List[function]
         The list of functions that ```iterate``` will call in sequence
    """

    from ._advance_infprob import advance_infprob
    from ._advance_play import advance_play

    return [advance_infprob, advance_play]
