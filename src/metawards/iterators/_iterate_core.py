
__all__ = ["iterate_core"]


def iterate_core(nthreads: int = 1, setup=False,
                 auto_advance_additional=True,
                 auto_advance_foi=True,
                 auto_advance_recovery=True,
                 **kwargs):
    """This returns the default list of 'advance_XXX' functions that
       are called in sequence at the beginning of each iteration of
       the model run. These are the core functions, so must make sure
       that the foi parameters have been calculated correctly
       and that the recovery/movement through disease stages takes
       place

       Parameters
       ----------
       nthreads: int
         The number of threads that will be used for each function.
         If this is 1, then the serial versions of the functions will
         be returned, else the parallel (OpenMP) versions will be
         returned
       setup: bool
         Whether or not to return the functions used to setup the
         space and input for the advance_XXX functions returned by
         this iterator. This is called once at the start of a run
         to return the functions that must be called to setup the
         model.

       Returns
       -------
       funcs: List[function]
         The list of functions that ```iterate``` will call in sequence
    """

    if setup:
        # Return the functions needed to initialise this iterator
        from ._setup_imports import setup_seed_wards
        from ._advance_additional import setup_additional_seeds

        funcs = [setup_seed_wards]

        if auto_advance_additional:
            funcs.append(setup_additional_seeds)

    else:
        from ._advance_additional import advance_additional
        from ._advance_foi import advance_foi
        from ._advance_recovery import advance_recovery

        funcs = []

        if auto_advance_additional:
            funcs.append(advance_additional)

        if auto_advance_foi:
            funcs.append(advance_foi)

        if auto_advance_recovery:
            funcs.append(advance_recovery)

    return funcs
