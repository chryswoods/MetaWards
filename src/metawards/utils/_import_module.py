
__all__ = ["import_module"]


def import_module(module):
    """This will try to import the passed module. This will return
       the module if it was imported, or will return 'None' if
       it should not be imported.

       Parameters
       ----------
       module: str
         The name of the module to import
    """

    try:
        import importlib
        m = importlib.import_module(module)
    except SyntaxError as e:
        print(f"\nSyntax error when importing {module}")
        print(f"{e.__class__.__name__}:{e}")
        print(f"Line {e.lineno}.{e.offset}:{(e.offset-1)*' '} |")
        print(f"Line {e.lineno}.{e.offset}:{(e.offset-1)*' '}\\|/")
        print(f"Line {e.lineno}.{e.offset}: {e.text}\n")
        m = None
    except Exception:
        m = None

    if m is None:
        try:
            import importlib.util
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
                spec = importlib.util.spec_from_file_location(
                                                module,
                                                pyfile)

                m = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(m)

                print(f"Loaded {module} from {pyfile}")

        except SyntaxError as e:
            print(f"\nSyntax error when reading {pyfile}")
            print(f"{e.__class__.__name__}:{e}")
            print(f"Line {e.lineno}.{e.offset}:{(e.offset-1)*' '} |")
            print(f"Line {e.lineno}.{e.offset}:{(e.offset-1)*' '}\\|/")
            print(f"Line {e.lineno}.{e.offset}: {e.text}\n")
        except Exception:
            pass

    return m
