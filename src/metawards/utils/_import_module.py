
__all__ = ["import_module"]


def _clean_cython(pyfile):
    """This function will clean up the passed cython file, making sure
       that required cython directives are added to the top of this file
    """

    from pathlib import Path as _Path

    p = _Path(pyfile)

    cleaned = f"_cython_{p.name}"

    import os as _os

    if _os.path.exists(cleaned):
        if _os.path.getmtime(cleaned) > _os.path.getmtime(pyfile):
            # cleaned exists, and is newer than pyfile - no need to rewrite
            return cleaned

    lines = open(pyfile).readlines()

    with open(cleaned, "w") as FILE:
        FILE.write(
            """# cython: binding=True
# cython: language_level=3
# cython: embedsignature=True
# cython: boundscheck=False
# cython: cdivision=True
# cython: initializedcheck=False
# cython: cdivision_warnings=False
# cython: wraparound=False
# cython: nonecheck=False
# cython: overflowcheck=False
""")
        for line in lines:
            FILE.write(line)

    return cleaned


def import_module(module):
    """This will try to import the passed module. This will return
       the module if it was imported, or will return 'None' if
       it should not be imported.

       Parameters
       ----------
       module: str
         The name of the module to import
    """

    from ._console import Console

    try:
        import importlib
        m = importlib.import_module(module)
    except SyntaxError as e:
        Console.error(
            f"\nSyntax error when importing {module}\n"
            f"{e.__class__.__name__}:{e}\n"
            f"Line {e.lineno}.{e.offset}:{(e.offset-1)*' '} |\n"
            f"Line {e.lineno}.{e.offset}:{(e.offset-1)*' '}\\|/\n"
            f"Line {e.lineno}.{e.offset}: {e.text}")
        m = None
    except ImportError:
        # this is ok and expected if the module is in a python file
        # that will be loaded below
        m = None
    except Exception:
        # something else went wrong
        m = None

    if m is None:
        try:
            import os

            if os.path.exists(module):
                pyfile = module
            elif os.path.exists(f"{module}.py"):
                pyfile = f"{module}.py"
            elif os.path.exists(f"{module}.pyx"):
                pyfile = f"{module}.pyx"
            else:
                pyfile = None

            if pyfile:
                from pathlib import Path as _Path
                module = _Path(pyfile).stem

                if pyfile.endswith(".pyx"):
                    try:
                        import pyximport
                        pyfile = _clean_cython(pyfile)
                        Console.print(f"Compiling cython plugin from {pyfile}")
                        pyximport.install(language_level=3)
                        m = pyximport.load_module(module, pyfile,
                                                  language_level=3)
                        Console.print(f"Loaded cython {module} from {pyfile}")
                    except Exception as e:
                        Console.error(
                            f"Cannot compile and load the cython plugin "
                            f"{pyfile}. Error is {e.__class__}: {e}")
                else:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        module,
                        pyfile)

                    if spec is None:
                        raise ImportError(
                            f"Cannot build a spec for the module from "
                            f"the file {pyfile}")

                    m = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(m)

                    Console.print(f"Loaded {module} from {pyfile}")

        except SyntaxError as e:
            Console.error(
                f"\nSyntax error when reading {pyfile}\n"
                f"{e.__class__.__name__}:{e}\n"
                f"Line {e.lineno}.{e.offset}:{(e.offset-1)*' '} |\n"
                f"Line {e.lineno}.{e.offset}:{(e.offset-1)*' '}\\|/\n"
                f"Line {e.lineno}.{e.offset}: {e.text}")
        except Exception as e:
            Console.error(
                f"\nError when importing {module}\n"
                f"{e.__class__.__name__}: {e}\n")
            m = None

    if m is not None:
        Console.print(f"IMPORT {m}")

    return m
