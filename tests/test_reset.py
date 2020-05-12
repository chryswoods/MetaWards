
import os
import pytest

from metawards import Parameters, Network, Population, \
    OutputFiles, VariableSets
from metawards.utils import Profiler, run_models

script_dir = os.path.dirname(__file__)
ncovparams_csv = os.path.join(script_dir, "data", "ncovparams.csv")


def can_run_multiprocessing(force_multi=False):
    import sys
    if sys.platform == "win32":
        # Cannot use multiprocessing in tests on windows
        return False

    elif sys.version_info >= (3, 8):
        # Cannot use multiprocessing in tests for Python 3.8 or above
        return False

    else:
        # if seems like nothing can run multiprocessing on github actions...
        return force_multi


@pytest.mark.slow
def test_reset(prompt=None, nthreads=1, force_multi=False):
    """This test runs several runs one after another with the expectation
       that they should all give the same result. This tests that the
       network is being correctly reset after each run
    """

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

    # start from the parameters in the specified line number of the
    # provided input file
    variables = params.read_variables(inputfile, line_num)

    # extra parameters that are set
    params.UV = UV
    params.static_play_at_home = 0
    params.play_to_work = 0
    params.work_to_play = 0
    params.daily_imports = 0.0

    # the size of the starting population
    population = Population(initial=57104043)

    profiler = Profiler()

    nsteps = 20

    print("Building the network...")
    network = Network.build(params=params,
                            profiler=profiler)

    outdir = os.path.join(script_dir, "test_integration_output")

    if can_run_multiprocessing(force_multi):
        print("Running in parallel...")
        variable = variables[0]
        variables = VariableSets()
        variables.append(variable)
        variables = variables.repeat(3)

        params = params.set_variables(variables[0])
        network.update(params, profiler=profiler)

        with OutputFiles(outdir, force_empty=True,
                         prompt=prompt) as output_dir:
            results = run_models(network=network,
                                 output_dir=output_dir, variables=variables,
                                 population=population, nsteps=nsteps,
                                 nthreads=nthreads, nprocs=2, seed=seed,
                                 debug_seeds=True)

        OutputFiles.remove(outdir, prompt=None)

        assert len(results) == 3

        print(f"Result 1\n{results[0][1][-1]}")
        print(f"Result 2\n{results[1][1][-1]}")
        print(f"Result 3\n{results[2][1][-1]}")

        assert results[0][1] == results[1][1]
        assert results[0][1] == results[2][1]

    print("Running model 1...")
    network.update(params, profiler=profiler)

    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        trajectory1 = network.run(population=population, seed=seed,
                                  output_dir=output_dir,
                                  nsteps=nsteps, profiler=None,
                                  nthreads=nthreads)

    OutputFiles.remove(outdir, prompt=None)

    # this should reset the network
    print("Running model 2...")
    network.update(params, profiler=profiler)

    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        trajectory2 = network.run(population=population, seed=seed,
                                  output_dir=output_dir,
                                  nsteps=nsteps, profiler=None,
                                  nthreads=nthreads)

    OutputFiles.remove(outdir, prompt=None)

    # this should reset the network
    print("Running model 3...")
    network.update(params, profiler=profiler)

    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        trajectory3 = network.run(population=population, seed=seed,
                                  output_dir=output_dir,
                                  nsteps=nsteps, profiler=None,
                                  nthreads=nthreads)

    OutputFiles.remove(outdir, prompt=None)

    print("End of the run")

    print(profiler)

    print(f"Model 1 output: {trajectory1}")
    print(f"Model 2 output: {trajectory2}")
    print(f"Model 3 output: {trajectory3}")

    assert trajectory1 == trajectory2
    assert trajectory1 == trajectory3

    if can_run_multiprocessing(force_multi):
        # this should also be the same result as the multiprocessing run
        assert trajectory1 == results[0][1]


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()  # needed to stop fork bombs
    test_reset(nthreads=2, force_multi=True)
