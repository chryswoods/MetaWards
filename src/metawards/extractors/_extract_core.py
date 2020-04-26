
__all__ = ["extract_core"]


def extract_core(nthreads: int = 1, setup=False,
                 auto_output_core=True,
                 **kwargs):
    """This returns the default list of 'output_XXX' functions that
       are called in sequence at the end of each iteration of
       the model run.

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
         this extractor. This is called once at the start of a run
         to return the functions that must be called to setup the
         output files.

       Returns
       -------
       funcs: List[function]
         The list of functions that ```extract_data``` will call in sequence
    """

    funcs = []

    if setup:
        if auto_output_core:
            from ._output_core import setup_core
            funcs.append(setup_core)

    else:
        if auto_output_core:
            from ._output_core import output_core
            funcs.append(output_core)

    return funcs
