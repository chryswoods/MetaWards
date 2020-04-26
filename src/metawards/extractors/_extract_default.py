
__all__ = ["extract_default", "extractor_needs_setup"]


def extractor_needs_setup(extractor):
    """Return whether or not the passed extractor function has
       a "setup" argument, and thus needs to be setup before
       it can be used
    """
    import inspect
    return "setup" in inspect.signature(extractor).parameters


def extract_default(setup=False, **kwargs):
    """This returns the default list of 'output_XXX' functions that
       are called in sequence for each iteration of the model run.
       These functions are used to output data to files for
       future processing

       Parameters
       ----------
       nthreads: int
         The number of threads that will be used for each function.
         If this is 1, then the serial versions of the functions will
         be returned, else the parallel (OpenMP) versions will be
         returned
       setup: bool
         Whether or not to return the functions used to setup the
         space and output files for the output_XXX functions returned by
         this iterator. This is called once at the start of a run
         to return the functions that must be called to setup the
         model

       Returns
       -------
       funcs: List[function]
         The list of functions that ```extract_data``` will call in sequence
    """

    kwargs["setup"] = setup

    from ._extract_core import extract_core

    if setup:
        # Return the functions needed to initialise this extractor
        funcs = extract_core(**kwargs)

    else:
        funcs = extract_core(**kwargs)

        from ._output_basic import output_basic
        from ._output_dispersal import output_dispersal
        from ._output_prevalence import output_prevalence
        from ._output_incidence import output_incidence

        funcs.append(output_basic)
        funcs.append(output_dispersal)
        funcs.append(output_prevalence)
        funcs.append(output_incidence)

    return funcs
