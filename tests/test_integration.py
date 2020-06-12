
import os
import pytest

from metawards import Parameters, Network, Population, OutputFiles
from metawards.utils import Profiler, Console

script_dir = os.path.dirname(__file__)
ncovparams_csv = os.path.join(script_dir, "data", "ncovparams.csv")


@pytest.mark.slow
def test_integration_ncov(prompt=None):
    """This test repeats main_RepeatsNcov.c and validates that the
       various stages report the same results as the original C code
       for ncov
    """

    # user input parameters
    seed = 15324
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

    print("Building the network...")
    network = Network.build(params=params,
                            profiler=profiler)

    params = params.set_variables(variables[0])
    network.update(params, profiler=profiler)

    print("Run the model...")
    outdir = os.path.join(script_dir, "test_integration_output")

    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        trajectory = network.run(population=population, seed=seed,
                                 output_dir=output_dir,
                                 nsteps=30, profiler=profiler,
                                 nthreads=1)

    OutputFiles.remove(outdir, prompt=None)

    print("End of the run")

    Console.print_profiler(profiler)

    Console.rule("Model output")
    Console.print_population(trajectory[-1])

    # The original C code has this expected population after 30 steps
    expected = Population(initial=57104043,
                          susceptibles=56081438,
                          latent=244,
                          total=81,
                          recovereds=314,
                          n_inf_wards=76,
                          day=30)

    Console.rule("Expected output")
    Console.print_population(expected)

    assert trajectory[-1] == expected


@pytest.mark.veryslow
def test_integration_pox(prompt=None):
    """This test repeats main_RepeatsNcov.c and validates that the
       various stages report the same results as the original C code
       for the POX
    """

    # user input parameters
    seed = 15324
    inputfile = ncovparams_csv
    line_num = 0
    UV = 1.0

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
    params.set_disease("pox")
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

    print("Building the network...")
    network = Network.build(params=params,
                            profiler=profiler)

    params = params.set_variables(variables[0])
    network.update(params, profiler=profiler)

    outdir = os.path.join(script_dir, "test_integration_output")

    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        print("Run the model...")
        trajectory = network.run(population=population, seed=seed,
                                 output_dir=output_dir,
                                 nsteps=31, profiler=profiler,
                                 nthreads=1)

    OutputFiles.remove(outdir, prompt=None)

    print("End of the run")

    Console.print_profiler(profiler)

    Console.rule("Model output")
    Console.print_population(trajectory[-1])

    # The original C code has this expected population after 47 steps
    expected = Population(initial=57104043,
                          susceptibles=56080960,
                          latent=317,
                          total=320,
                          recovereds=480,
                          n_inf_wards=229,
                          day=31)

    Console.rule("Expected output")
    Console.print_population(expected)

    assert trajectory[-1] == expected


if __name__ == "__main__":
    import sys

    try:
        n = str(sys.argv[1]).lower()
    except Exception:
        n = None

    if n is None or n == "all":
        test_integration_ncov(input)
        test_integration_pox(input)
    elif n == "pox":
        test_integration_pox(input)
    elif n == "ncov":
        test_integration_ncov(input)
    else:
        test_integration_ncov(input)
