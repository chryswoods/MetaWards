
from metawards import OutputFiles

import pytest
import os

script_dir = os.path.dirname(__file__)


def test_openfiles(prompt=None):
    outdir = os.path.join(script_dir, "test_openfiles_output")

    if os.path.exists(outdir):
        OutputFiles.remove(outdir, prompt=prompt)

    of = OutputFiles(outdir)

    assert of.is_open()
    assert not of.is_closed()

    with pytest.raises(ValueError):
        of.open("../test.txt")

    with pytest.raises(ValueError):
        of.open("/test.txt")

    FILE = of.open("test.txt")

    assert of.is_open()

    FILE.write("hello\n")

    of.close()

    assert of.is_closed()

    assert open(os.path.join(outdir, "test.txt")).readline() == "hello\n"

    with pytest.raises(FileExistsError):
        OutputFiles(outdir, prompt=None)

    with OutputFiles(outdir, force_empty=True, prompt=None) as of:
        FILE = of.open("test.txt")
        assert of.is_open()

        assert of.get_filename("test.txt").endswith("test.txt")

        FILE.write("goodbye\n")

        FILE = of.open("test2.txt", auto_bzip=True)
        FILE.write("hello ")

        assert of.get_filename("test2.txt").endswith("test2.txt.bz2")

        FILE = of.open("test2.txt")
        FILE.write("world\n")

    assert open(os.path.join(outdir, "test.txt")).readline() == "goodbye\n"

    import bz2
    line = bz2.open(os.path.join(outdir, "test2.txt.bz2"), "rt").readline()
    assert line == "hello world\n"

    OutputFiles.remove(outdir, prompt=None)


if __name__ == "__main__":
    test_openfiles(input)
