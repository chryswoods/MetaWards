
import os

from metawards import Parameters, Network, Population

script_dir = os.path.dirname(__file__)
ncovparams_csv = os.path.join(script_dir, "data", "ncovparams.csv")


def test_integration():
    """This test repeats main_RepeatsNcov.c and validates that the
       various stages report the same results as the original C code
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
    params.set_disease("ncov")
    params.set_input_files("2011Data")

    # start from the parameters in the specified line number of the
    # provided input file
    params.read_file(inputfile, line_num)

    # extra parameters that are set
    params.UV = UV
    params.static_play_at_home = 0
    params.play_to_work = 0
    params.work_to_play = 0
    params.daily_imports = 0.0

    # the size of the starting population
    population = Population(initial=57104043)

    print("Building the network...")
    network = Network.build(params=params, calculate_distances=True,
                            profile=False)

    print("Run the model...")
    population = network.run(population=population, seed=seed,
                             s=-1, nsteps=28, profile=False)

    print("End of the run")

    print(f"Model output:  {population}")

    # The original C code has this expected population after 47 steps
    expected = Population(initial=57104043,
                          susceptibles=56081764,
                          latent=122,
                          total=43,
                          recovereds=148,
                          n_inf_wards=34)

    print(f"Expect output: {expected}")

    assert population == expected


if __name__ == "__main__":
    test_integration()
