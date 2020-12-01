
import os
import pytest

from metawards import Parameters, Disease, Network, Population, OutputFiles

script_dir = os.path.dirname(__file__)


def test_plugins():

    iterator = f"{script_dir}/plugins/_iterator.py"
    extractor = f"{script_dir}/plugins/_extractor.py"
    mover = f"{script_dir}/plugins/_mover.py"
    mixer = f"{script_dir}/plugins/_mixer.py"

    params = Parameters()
    params.set_disease("ncov")
    population = Population(initial=1000)

    print("Building the network...")
    network = Network.single(params=params, population=population)

    outdir = os.path.join(script_dir, "test_plugins")

    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        trajectory = network.copy().run(population=population,
                                        output_dir=output_dir,
                                        iterator=iterator,
                                        extractor=extractor,
                                        mixer=mixer,
                                        mover=mover,
                                        nthreads=1)

    OutputFiles.remove(outdir, prompt=None)

    p = trajectory[-1]

    assert p.advance_test == "advance_test_value"
    assert p.output_test == "output_test_value"
    assert p.merge_test == "merge_test_value"
    assert p.go_test == "go_test_value"


if __name__ == "__main__":
    test_plugins()
