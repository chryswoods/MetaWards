
import pickle
import os

from metawards import Parameters

script_dir = os.path.dirname(__file__)
ncovparams_csv = os.path.join(script_dir, "data", "ncovparams.csv")


def test_parameters():
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

    params.set_disease("ncov")
    params.set_input_files("2011Data")
    params.add_seeds("ExtraSeedsBrighton.dat")

    # extra parameters that are set
    params.UV = 1.0
    params.static_play_at_home = 0
    params.play_to_work = 0
    params.work_to_play = 0
    params.daily_imports = 0.0

    variables = params.read_variables(ncovparams_csv, 0)
    params = params.set_variables(variables[0])

    # make sure that we can correctly pickle and unpickle these parameters
    data = pickle.dumps(params)

    print(f"Picked params to {data}")

    params2 = pickle.loads(data)

    assert params == params2


if __name__ == "__main__":
    test_parameters()
