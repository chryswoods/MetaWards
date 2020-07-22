
try:
    import metawards
except ImportError:
    print("Unable to import metawards. Please make sure it is installed "
          "correctly. For more help see https://metawards.org or raise "
          "an issue at https://github.com/metawards/MetaWards/issues.")
    import sys
    sys.exit(-1)


def cli():
    import sys
    from pathlib import Path

    exe = str(Path(sys.executable).expanduser().absolute())

    print("\nStart R or RStudio.\n")
    print("If you haven't installed 'reticulate' then type at the prompt:")
    print("> install.packages(\"reticulate\")\n")
    print("Once this has been installed you should now import reticulate via;")
    print("> library(\"reticulate\")\n")
    print("Next, tell R where this Python executable is located via;")
    print(f"> use_python(\"{exe}\", required = TRUE)\n")
    print("Finally, import the metawards module using;")
    print("> metawards <- import(\"metawards\")\n")
    print("You can now use metawards, e.g. via;")
    print("> metawards$run(model=\"single\", additional=5)\n")
