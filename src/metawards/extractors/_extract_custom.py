
from typing import Union as _Union
from typing import List as _List
from ..utils._get_functions import MetaFunction, accepts_stage

__all__ = ["extract_custom",
           "build_custom_extractor"]


def build_custom_extractor(custom_function: _Union[str, MetaFunction],
                           parent_name="__main__") -> MetaFunction:
    """Build and return a custom extractor from the passed
       function. This will wrap 'extract_custom' around
       the function to double-check that the custom
       function is doing everything correctly

       Parameters
       ----------
       custom_function: MetaFunction or str
         This can either be a function, which will be wrapped and
         returned, or it can be a string. If it is a string then
         we will attempt to locate or import the function associated
         with that string. The search order is;

         1. Is this 'metawards.extractors.custom_function'?
         2. Is this 'custom_function' that is already imported'?
         3. Is this a file name in the current path, if yes then
            find the function in that file (either the first function
            called 'extractXXX' or the specified function if
            custom_function is in the form module::function)

        parent_name: str
          This should be the __name__ of the calling function, e.g.
          call this function as build_custom_extractor(func, __name__)

        Returns
        -------
        extractor: MetaFunction
          The wrapped extractor that is suitable for using in the extract
          function.
    """
    from ..utils._console import Console
    Console.print(custom_function)

    if isinstance(custom_function, str):
        Console.print(f"Importing a custom extractor from {custom_function}")

        # we need to find the function
        import metawards.extractors

        # is it metawards.extractors.{custom_function}
        try:
            func = getattr(metawards.extractors, custom_function)
            return build_custom_extractor(func)
        except Exception:
            pass

        # do we have the function in the current namespace?
        import sys
        try:
            func = getattr(sys.modules[__name__], custom_function)
            return build_custom_extractor(func)
        except Exception:
            pass

        # how about the __name__ namespace of the caller
        try:
            func = getattr(sys.modules[parent_name], custom_function)
            return build_custom_extractor(func)
        except Exception:
            pass

        # how about the __main__ namespace (e.g. if this was loaded
        # in a script)
        try:
            func = getattr(sys.modules["__main__"], custom_function)
            return build_custom_extractor(func)
        except Exception:
            pass

        # can we import this function as a file - need to check that
        # the user hasn't written this as module::function
        if custom_function.find("::") != -1:
            parts = custom_function.split("::")
            func_name = parts[-1]
            func_module = "::".join(parts[0:-1])
        else:
            func_name = None
            func_module = custom_function

        from ..utils._import_module import import_module

        module = import_module(func_module)

        if module is None:
            # we cannot find the extractor
            Console.error(f"Cannot find the extractor '{custom_function}'."
                          f"Please make sure this is spelled correctly and "
                          f"any python modules/files needed are in the "
                          f"PYTHONPATH or current directory")
            raise ImportError(f"Could not import the extractor "
                              f"'{custom_function}'")

        if func_name is None:
            # find the last function that starts with 'extract'
            import inspect
            funcs = []
            for name, value in inspect.getmembers(module):
                if name.startswith("extract"):
                    if hasattr(value, "__call__"):
                        if value.__module__ == module.__name__:
                            # this is a function defined in this module
                            funcs.append(value)

            if len(funcs) > 0:
                func = funcs[0]

                if len(funcs) > 1:
                    Console.warning(
                        f"Multiple possible matching functions: {funcs}. "
                        f"Choosing {func}. Please use the module::function "
                        f"syntax if this is the wrong choice.")
            else:
                func = None

            if func is not None:
                return build_custom_extractor(func)

            Console.error(
                f"Could not find any function in the module "
                f"{custom_function} that has a name that starts "
                f"with 'extract'. Please manually specify the "
                f"name using the '{custom_function}::your_function syntax")

            raise ImportError(f"Could not import the extractor "
                              f"{custom_function}")

        else:
            if hasattr(module, func_name):
                return build_custom_extractor(getattr(module, func_name))

            Console.error(
                f"Could not find the function {func_name} in the "
                f"module {func_module}. Check that the spelling "
                f"is correct and that the right version of the module "
                f"is being loaded.")
            raise ImportError(f"Could not import the extractor "
                              f"{custom_function}")

    if not hasattr(custom_function, "__call__"):
        Console.error(
            f"Cannot build an extractor for {custom_function} "
            f"as it is missing a __call__ function, i.e. it is "
            f"not a function.")
        raise ValueError(f"You can only build custom extractors for "
                         f"actual functions... {custom_function}")

    Console.print(f"Building a custom extractor for {custom_function}",
                  style="magenta")

    return lambda **kwargs: extract_custom(custom_function=custom_function,
                                           **kwargs)


def extract_custom(custom_function: MetaFunction,
                   stage: str, **kwargs) -> _List[MetaFunction]:
    """This returns the default list of 'output_XXX' functions that
       are called in sequence for each iteration of the model run.
       This provides a custom extractor that uses
       'custom_function' passed from the user. This makes
       sure that if 'stage' is not handled by the custom function,
       then the "extract_default" functions for that stage
       are correctly called for all stages except "analyse"

       Parameters
       ----------
       custom_function: MetaFunction
         A custom user-supplied function that returns the
         functions that the user would like to be called for
         each step.
       stage: str
         The stage of the day/model

       Returns
       -------
       funcs: List[MetaFunction]
         The list of functions that will be called in sequence
    """

    kwargs["stage"] = stage

    if custom_function is None:
        from ._extract_default import extract_default
        return extract_default(**kwargs)

    elif stage == "analyse" or accepts_stage(custom_function):
        # most custom functions operate at the 'analyse' stage,
        # so extractors that don't specify a stage are assumed to
        # only operate here (every other stage is 'extract_default')
        return custom_function(**kwargs)

    else:
        from ._extract_default import extract_default
        return extract_default(**kwargs)
