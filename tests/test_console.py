
import os

from metawards import OutputFiles
from metawards.utils import Console

script_dir = os.path.dirname(__file__)


def test_spinner():
    with Console.spinner() as spinner:
        spinner.success()

    with Console.spinner() as spinner:
        spinner.failure()

    with Console.spinner("something") as spinner:
        spinner.success()

    with Console.spinner("else") as spinner:
        spinner.failure()


def test_console():
    Console.error("Something")
    Console.warning("Something else")
    Console.rule("ruler")
    Console.print("Some text")
    Console.debug("Debugging")
    Console.panel("Panel", style="alternate")
    Console.panel("Panel", style="alternate")
    Console.panel("Panel", style="header")

    outdir = os.path.join(script_dir, "test_console")

    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        FILE = output_dir.open("console.log", auto_bzip=True)
        Console.save(FILE)

        with Console.redirect_output(outdir):
            Console.debug("debug something")
            Console.warning("warning should be redirected")
            Console.rule("ruler")
            Console.panel("Panel one", style="alternate")
            Console.panel("Panel two", style="alternate")
            Console.panel("Panel three", style="header")
            with Console.spinner("spinner") as spinner:
                spinner.success()
            with Console.spinner("spinner") as spinner:
                spinner.failure()
            assert not Console.debugging_enabled()
            Console.set_debugging_enabled(True)
            assert Console.debugging_enabled()
            Console.debug("HERE I AM")

        assert not Console.debugging_enabled()
        Console.debug("THIS SHOULD NOT BE PRINTED")

        Console.set_debugging_enabled(True)
        assert Console.debugging_enabled()
        Console.debug("debug debug debug", variables=[output_dir, outdir])
        Console.save(FILE)
        FILE.close()

    import bz2

    with bz2.open(os.path.join(outdir,
                               "console.log.bz2"),
                  "t", encoding="utf-8") as FILE:
        lines = FILE.readlines()

    print("\nMain output")
    for line in lines:
        print(line.strip())

    with bz2.open(os.path.join(outdir,
                               "output.txt.bz2"),
                  "t", encoding="utf-8") as FILE:
        lines = FILE.readlines()

    print("\nRedirected output")
    for line in lines:
        print(line.strip())

    print("\nNOW REMOVING FILES")
    OutputFiles.remove(outdir, prompt=None)


if __name__ == "__main__":
    test_spinner()
    test_console()
