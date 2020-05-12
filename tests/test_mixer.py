
import os
import pytest

from metawards import Parameters, Network, Population, \
    OutputFiles, Demographics
from metawards.mixers import merge_using_matrix, mix_none, mix_evenly
from metawards.extractors import extract_none

script_dir = os.path.dirname(__file__)
ncovparams_csv = os.path.join(script_dir, "data", "ncovparams.csv")
redgreenblue_json = os.path.join(script_dir, "data", "redgreenblue.json")


def mix_matrix_evenly(network, **kwargs):
    matrix = [[1.0, 1.0, 1.0],
              [1.0, 1.0, 1.0],
              [1.0, 1.0, 1.0]]

    network.demographics.interaction_matrix = matrix

    return [merge_using_matrix]


def mix_matrix_none(network, **kwargs):
    matrix = [[1.0, 0.0, 0.0],
              [0.0, 1.0, 0.0],
              [0.0, 0.0, 1.0]]

    network.demographics.interaction_matrix = matrix

    return [merge_using_matrix]


_network = None


def _get_network(nthreads):
    global _network

    if _network is not None:
        return _network.copy()

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

    demographics = Demographics.load(redgreenblue_json)

    print("Building the network...")
    network = Network.build(params=params)

    network = network.specialise(demographics, nthreads=nthreads)

    _network = network

    return network


@pytest.mark.slow
def test_mixer_none(prompt=None, nthreads=1):
    # user input parameters
    import random
    seed = random.randint(100000, 1000000)
    outdir = os.path.join(script_dir, "test_integration_output")

    network = _get_network(nthreads)

    # the size of the starting population
    population = Population(initial=57104043)

    nsteps = 20

    print("Running mix_none...")
    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        t_mix_none = network.copy().run(population=population, seed=seed,
                                        output_dir=output_dir,
                                        nsteps=nsteps,
                                        extractor=extract_none,
                                        mixer=mix_none,
                                        nthreads=nthreads)

    OutputFiles.remove(outdir, prompt=None)

    print("Running mix_matrix_none...")
    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        t_mix_m_none = network.copy().run(population=population, seed=seed,
                                          output_dir=output_dir,
                                          nsteps=nsteps,
                                          extractor=extract_none,
                                          mixer=mix_matrix_none,
                                          nthreads=nthreads)

    OutputFiles.remove(outdir, prompt=None)

    print(t_mix_none)
    print(t_mix_m_none)
    assert t_mix_none == t_mix_m_none


@pytest.mark.slow
def test_mixer_evenly(prompt=None, nthreads=1):
    # user input parameters
    import random
    seed = random.randint(100000, 1000000)
    outdir = os.path.join(script_dir, "test_integration_output")

    network = _get_network(nthreads)

    # the size of the starting population
    population = Population(initial=57104043)

    nsteps = 20

    print("Running mix_evenly...")
    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        t_mix_evenly = network.copy().run(population=population, seed=seed,
                                          output_dir=output_dir,
                                          nsteps=nsteps,
                                          extractor=extract_none,
                                          mixer=mix_evenly,
                                          nthreads=nthreads)

    OutputFiles.remove(outdir, prompt=None)

    print("Running mix_matrix_evenly...")
    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        t_mix_m_evenly = network.copy().run(population=population, seed=seed,
                                            output_dir=output_dir,
                                            nsteps=nsteps,
                                            extractor=extract_none,
                                            mixer=mix_matrix_evenly,
                                            nthreads=nthreads)

    OutputFiles.remove(outdir, prompt=None)

    print(t_mix_evenly)
    print(t_mix_m_evenly)
    assert t_mix_evenly == t_mix_m_evenly


if __name__ == "__main__":
    test_mixer_none(nthreads=2)
    test_mixer_evenly(nthreads=2)
