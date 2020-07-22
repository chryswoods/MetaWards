
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
        from IPython import start_ipython
        have_ipython = True
    except Exception:
        have_ipython = False

    if have_ipython:
        sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
        sys.exit(start_ipython())
    else:
        exe = sys.executable

        if exe is None or len(exe) == 0:
            print("Unable to find the Python executable!")
            sys.exit(-1)

        sys.argv[0] = exe

        import subprocess
        subprocess.run(sys.argv)
