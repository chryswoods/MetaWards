
import os
import pytest

from metawards.utils import Console
from metawards import Parameters, Network, Population, OutputFiles

script_dir = os.path.dirname(__file__)


def iterate_debug(**kwargs):
    Console.debug("Something")
    return []


@pytest.mark.slow
def test_output():
    try:
        params = Parameters.load(parameters="march29")
    except Exception as e:
        print(f"Unable to load parameter files. Make sure that you have "
              f"cloned the MetaWardsData repository and have set the "
              f"environment variable METAWARDSDATA to point to the "
              f"local directory containing the repository, e.g. the "
              f"default is $HOME/GitHub/MetaWardsData")
        raise e

    # load the disease and starting-point input files
    params.set_disease("ncov")
    params.set_input_files("2011Data")
    params.add_seeds("ExtraSeedsBrighton.dat")

    # the size of the starting population
    population = Population(initial=57104043)

    print("Building the network...")
    network = Network.build(params=params)

    from metawards.iterators import build_custom_iterator

    iterator = build_custom_iterator(iterate_debug, __name__)

    print("Run the model...")
    outdir = os.path.join(script_dir, "test_output")

    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        with Console.redirect_output(outdir, auto_bzip=True):
            trajectory = network.run(population=population,
                                     output_dir=output_dir,
                                     iterator=iterator,
                                     nthreads=1)

    OutputFiles.remove(outdir, prompt=None)

    print(trajectory[-1])

    print("End of the run")


if __name__ == "__main__":
    test_output()
