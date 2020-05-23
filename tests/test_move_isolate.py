
import os
import pytest

from metawards import Parameters, Network, Population, \
    OutputFiles, Demographics
from metawards.mixers import merge_using_matrix
from metawards.movers import go_isolate

script_dir = os.path.dirname(__file__)
isolate_json = os.path.join(script_dir, "data", "isolate.json")


def move_isolate(**kwargs):
    func = lambda **kwargs: go_isolate(go_from="home",
                                       go_to="isolate",
                                       release_to="released",
                                       self_isolate_stage=2,
                                       duration=7,
                                       **kwargs)

    return [func]


def mix_isolate(network, **kwargs):
    matrix = [[1.0, 1.0, 1.0],
              [1.0, 1.0, 1.0],
              [1.0, 1.0, 1.0]]

    network.demographics.interaction_matrix = matrix

    return [merge_using_matrix]


@pytest.mark.slow
def test_move_isolate(prompt=None, nthreads=1):

    # user input parameters
    import random
    seed = random.randint(100000, 1000000)

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

    # the size of the starting population
    population = Population(initial=57104043)

    nsteps = 20

    demographics = Demographics.load(isolate_json)

    print("Building the network...")
    network = Network.build(params=params)

    network = network.specialise(demographics, nthreads=nthreads)

    outdir = os.path.join(script_dir, "test_zero_demographic_output")

    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        trajectory = network.run(population=population, seed=seed,
                                 output_dir=output_dir,
                                 nsteps=nsteps, profiler=None,
                                 mixer=mix_isolate,
                                 mover=move_isolate,
                                 nthreads=nthreads)

    OutputFiles.remove(outdir, prompt=None)

    # no-one should be in the 'released' demographic yet...
    assert trajectory[-1].subpops[2].population == 0

    # there should be no latents in the 'isolate' demographic
    assert trajectory[-1].subpops[1].latent == 0

    print("End of the run")


if __name__ == "__main__":
    test_move_isolate(nthreads=2)
