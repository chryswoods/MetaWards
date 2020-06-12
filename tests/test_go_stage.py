
import os
import pytest

from metawards import Parameters, Network, Population, \
    OutputFiles, VariableSets, Demographics
from metawards.mixers import mix_evenly
from metawards.movers import go_stage

script_dir = os.path.dirname(__file__)
redblue_json = os.path.join(script_dir, "data", "redblue.json")


def go_stage_test(infections, **kwargs):

    old_num_in_red = sum(infections.subinfs[0].work[2]) + \
        sum(infections.subinfs[0].play[2])
    old_num_in_blue = sum(infections.subinfs[1].work[1]) + \
        sum(infections.subinfs[1].play[1])

    go_stage(go_from="red", go_to="blue", from_stage=2, to_stage=1,
             infections=infections, **kwargs)

    new_num_in_red = sum(infections.subinfs[0].work[2]) + \
        sum(infections.subinfs[0].play[2])
    new_num_in_blue = sum(infections.subinfs[1].work[1]) + \
        sum(infections.subinfs[1].play[1])

    from metawards.utils import Console
    Console.print(f"{old_num_in_blue} -> {new_num_in_blue}, "
                  f"{old_num_in_red} -> {new_num_in_red}")

    assert new_num_in_red == 0
    assert old_num_in_red - new_num_in_red == new_num_in_blue - old_num_in_blue


def move_stage(**kwargs):
    return [go_stage_test]


@pytest.mark.slow
def test_go_stage(prompt=None, nthreads=1):
    seed = 797747

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

    demographics = Demographics.load(redblue_json)

    print("Building the network...")
    network = Network.build(params=params)

    network = network.specialise(demographics, nthreads=nthreads)

    outdir = os.path.join(script_dir, "test_go_to")

    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        trajectory = network.copy().run(population=population, seed=seed,
                                        output_dir=output_dir,
                                        nsteps=nsteps,
                                        mixer=mix_evenly,
                                        mover=move_stage,
                                        nthreads=nthreads)

    OutputFiles.remove(outdir, prompt=None)

    # red demographic was seeded, but all moved to blue, so should have
    # no outbreak
    pop = trajectory[-1]
    print(pop)


if __name__ == "__main__":
    test_go_stage(nthreads=2)
