
from metawards import InputFiles
import os
from pathlib import Path

script_dir = os.path.dirname(__file__)

simple_network = os.path.join(script_dir, "data", "simple_network.json.bz2")


def test_inputfiles():
    a = InputFiles.load("single")
    print(a)

    assert a.is_single

    a = InputFiles.load(model="2011Data")
    print(a)

    assert a.is_model_dir
    assert a.model_name() == "2011Data"
    assert a.work.endswith("EW1.dat")
    assert a.play.endswith("PlayMatrix.dat")

    a = InputFiles.load(model=simple_network)
    print(a)

    assert a.is_wards_data
    assert a.wards_data == str(Path(simple_network).expanduser().absolute())


if __name__ == "__main__":
    test_inputfiles()
