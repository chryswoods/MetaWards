
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

    if nthreads is None or nthreads == 1:
        from ._advance_infprob import advance_infprob_serial
        from ._advance_play import advance_play_serial

        funcs = [advance_infprob_serial,
                 advance_play_serial]
    else:
        from ._advance_infprob import advance_infprob_omp
        from ._advance_play import advance_play_omp

        funcs = [advance_infprob_omp,
                 advance_play_omp]

    return funcs
