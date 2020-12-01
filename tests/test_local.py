
import os
import pytest
from copy import deepcopy

from metawards import Parameters, Network, Population, OutputFiles
from metawards.iterators import iterate_default

script_dir = os.path.dirname(__file__)


def advance_scale(network, **kwargs):
    scale_uv = network.nodes.scale_uv

    # enforce lockdown
    for i in range(1, network.nnodes + 1):
        scale_uv[i] = 0.0


def iterate_scale(stage, **kwargs):
    funcs = iterate_default(stage=stage, **kwargs)

    if stage == "foi":
        return [advance_scale] + funcs
    else:
        return funcs


def check_scale(workspace, **kwargs):
    # there should be no new infections
    I_in_wards = workspace.I_in_wards
    E_in_wards = workspace.E_in_wards

    # every ward except seeded should have no infections
    for i in range(1, workspace.nnodes + 1):
        if I_in_wards[i] != 0:
            print(f"I_in_wards[{i}] == {I_in_wards[i]}")

        if E_in_wards[i] != 0:
            print(f"E_in_wards[{i}] == {E_in_wards[i]}")

        if i != 2124:
            assert I_in_wards[i] == 0
            assert E_in_wards[i] == 0


def extract_scale(**kwargs):
    return [check_scale]


def advance_cutoff(network, **kwargs):
    cutoff = network.nodes.cutoff

    # enforce cutoff
    for i in range(1, network.nnodes + 1):
        cutoff[i] = 0.0


def iterate_cutoff(stage, **kwargs):
    funcs = iterate_default(stage=stage, **kwargs)

    if stage == "foi":
        return [advance_cutoff] + funcs
    else:
        return funcs


def check_cutoff(workspace, **kwargs):
    # there should be no infections in the unseeded ward
    I_in_wards = workspace.I_in_wards
    E_in_wards = workspace.E_in_wards

    # every ward except seeded should have no infections
    for i in range(1, workspace.nnodes + 1):
        if I_in_wards[i] != 0:
            print(f"I_in_wards[{i}] == {I_in_wards[i]}")

        if E_in_wards[i] != 0:
            print(f"E_in_wards[{i}] == {E_in_wards[i]}")

        if i != 2124:
            assert I_in_wards[i] == 0
            assert E_in_wards[i] == 0


def extract_cutoff(**kwargs):
    return [check_cutoff]


def advance_both(network, **kwargs):
    cutoff = network.nodes.cutoff
    scale_uv = network.nodes.scale_uv

    # enforce cutoff
    for i in range(1, network.nnodes + 1):
        cutoff[i] = 42.0
        scale_uv[i] = 0.5


def iterate_both(stage, **kwargs):
    funcs = iterate_default(stage=stage, **kwargs)

    if stage == "foi":
        return [advance_both] + funcs
    else:
        return funcs


@pytest.mark.slow
def test_local():
    prompt = None

    # user input parameters
    seed = 15324
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
    params.add_seeds("1 5 2124")  #  seeding 5 into ward 2124

    # extra parameters that are set
    params.UV = UV
    params.static_play_at_home = 0
    params.play_to_work = 0
    params.work_to_play = 0
    params.daily_imports = 0.0

    # the size of the starting population
    population = Population(initial=57104043)

    print("Building the network...")
    network = Network.build(params=params)

    outdir = os.path.join(script_dir, "test_local_output")

    # First check that setting the local cutoff has the same effect
    # as setting the global cutoff

    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        trajectory = network.copy().run(population=population, seed=seed,
                                        output_dir=output_dir,
                                        nsteps=50,
                                        iterator=iterate_cutoff,
                                        extractor=extract_cutoff,
                                        nthreads=1)

    OutputFiles.remove(outdir, prompt=None)

    # run setting the global dyn_dist_cutoff to zero
    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        net2 = network.copy()
        net2.params.dyn_dist_cutoff = 0.0
        trajectory2 = net2.run(population=population, seed=seed,
                               output_dir=output_dir,
                               nsteps=50,
                               extractor=extract_cutoff,
                               nthreads=1)

    OutputFiles.remove(outdir, prompt=None)

    print(f"Model output: {trajectory}")
    print(f"Model output: {trajectory2}")

    assert trajectory == trajectory2

    # now test that setting the scale_uv has the same effect as
    # setting the global scale_uv

    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        trajectory = network.copy().run(population=population, seed=seed,
                                        output_dir=output_dir,
                                        nsteps=50,
                                        iterator=iterate_scale,
                                        extractor=extract_scale,
                                        nthreads=1)

    OutputFiles.remove(outdir, prompt=None)

    # run setting the global dyn_dist_cutoff to zero
    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        net2 = network.copy()
        pop2 = deepcopy(population)
        pop2.scale_uv = 0.0

        trajectory2 = net2.run(population=pop2, seed=seed,
                               output_dir=output_dir,
                               nsteps=50,
                               extractor=extract_scale,
                               nthreads=1)

    OutputFiles.remove(outdir, prompt=None)

    print(f"Model output: {trajectory}")
    print(f"Model output: {trajectory2}")

    p = trajectory[-1]
    p2 = trajectory2[-1]

    # won't be identical as different scale_uv causes different order
    # of random numbers - but should still have 0 infections
    assert p.has_equal_SEIR(p2)

    # now test that setting both to non-zero values has the same effect

    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        trajectory = network.copy().run(population=population, seed=seed,
                                        output_dir=output_dir,
                                        nsteps=50,
                                        iterator=iterate_both,
                                        nthreads=1)

    OutputFiles.remove(outdir, prompt=None)

    # run setting the global dyn_dist_cutoff to zero
    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        net2 = network.copy()
        net2.params.dyn_dist_cutoff = 42.0
        pop2 = deepcopy(population)
        pop2.scale_uv = 0.5

        trajectory2 = net2.run(population=pop2, seed=seed,
                               output_dir=output_dir,
                               nsteps=50,
                               nthreads=1)

    OutputFiles.remove(outdir, prompt=None)

    print(f"Model output: {trajectory}")
    print(f"Model output: {trajectory2}")

    p = trajectory[-1]
    p2 = trajectory2[-1]
    p2.scale_uv = 1
    assert p == p2


if __name__ == "__main__":
    test_local()
