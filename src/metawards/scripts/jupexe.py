
try:
    import metawards
except ImportError:
    print("Unable to import metawards. Please make sure it is installed "
          "correctly. For more help see https://metawards.org or raise "
          "an issue at https://github.com/metawards/MetaWards/issues.")
    import sys
    sys.exit(-1)


def cli():
    import re
    import sys

    try:
        from jupyter_core.command import main
        have_jupyter = True
    except Exception:
        have_jupyter = False

    if have_jupyter:
        sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
        sys.exit(main())
    else:
        print("Cannot find jupyter. Install using, e.g. "
              "'pip install jupyter jupyterlab'")
        sys.exit(-1)
