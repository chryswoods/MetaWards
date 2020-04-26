
__all__ = ["iterate_default", "iterator_needs_setup"]


def iterator_needs_setup(iterator):
    """Return whether or not the passed iterator function has
       a "setup" argument, and thus needs to be setup before
       it can be used
    """
    import inspect
    return "setup" in inspect.signature(iterator).parameters


def iterate_default(setup=False, **kwargs):
    """This returns the default list of 'advance_XXX' functions that
       are called in sequence for each iteration of the model run.
       This is the default iterator. It models every day as though
       it is a working day.

       Parameters
       ----------
       setup: bool
         Whether or not to return the functions used to setup the
         space and input for the advance_XXX functions returned by
         this iterator. This is called once at the start of a run
         to return the functions that must be called to setup the
         model

       Returns
       -------
       funcs: List[function]
         The list of functions that ```iterate``` will call in sequence
    """

    kwargs["setup"] = setup

    from ._iterate_core import iterate_core
    from ._iterate_weekday import iterate_weekday

    if setup:
        # Return the functions needed to initialise this iterator
        funcs = iterate_core(**kwargs)

        # Does 'iterate_weekday' need to be setup?
        if iterator_needs_setup(iterate_weekday):
            funcs += iterate_weekday(**kwargs)

    else:
        funcs = iterate_core(**kwargs) + iterate_weekday(**kwargs)

    return funcs
