
import os
import pytest

from metawards import Parameters, Network, Population, \
    OutputFiles
from metawards.extractors import extract_none

script_dir = os.path.dirname(__file__)
ncovparams_csv = os.path.join(script_dir, "data", "ncovparams.csv")


@pytest.mark.slow
def test_network_copy(prompt=None, nthreads=1):

    # user input parameters
    import random
    seed = random.randint(100000, 1000000)
    inputfile = ncovparams_csv
    line_num = 0
    UV = 0.0

    # load all of the parameters
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
    params.set_disease(os.path.join(script_dir, "data", "ncov.json"))
    params.set_input_files("2011Data")
    params.add_seeds("ExtraSeedsBrighton.dat")

    # extra parameters that are set
    params.UV = UV
    params.static_play_at_home = 0
    params.play_to_work = 0
    params.work_to_play = 0
    params.daily_imports = 0.0

    # the size of the starting population
    population = Population(initial=57104043)

    nsteps = 20

    print("Building the network...")
    network = Network.build(params=params)

    outdir = os.path.join(script_dir, "test_network_copy")

    print("Run 1")
    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        t1 = network.copy().run(population=population, seed=seed,
                                output_dir=output_dir,
                                nsteps=nsteps,
                                extractor=extract_none,
                                nthreads=nthreads)

    OutputFiles.remove(outdir, prompt=None)

    print("Run 2")
    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        t2 = network.copy().run(population=population, seed=seed,
                                output_dir=output_dir,
                                nsteps=nsteps,
                                extractor=extract_none,
                                nthreads=nthreads)

    print("Run 3")
    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        t3 = network.copy().run(population=population, seed=seed,
                                output_dir=output_dir,
                                nsteps=nsteps,
                                extractor=extract_none,
                                nthreads=nthreads)

    OutputFiles.remove(outdir, prompt=None)

    print(t1)
    print(t2)
    print(t3)
    assert t1 == t2
    assert t1 == t3


if __name__ == "__main__":
    test_network_copy(nthreads=2)
