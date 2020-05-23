
import os
import pytest

from metawards import Parameters, Network, Population, \
    OutputFiles, VariableSets, Demographics
from metawards.mixers import mix_evenly
from metawards.movers import go_to

script_dir = os.path.dirname(__file__)
redblue_json = os.path.join(script_dir, "data", "redblue.json")


def move_blue_to_red(**kwargs):
    func = lambda **kwargs: go_to(go_from="blue",
                                  go_to="red",
                                  **kwargs)

    return [func]


def move_red_to_blue(**kwargs):
    func = lambda **kwargs: go_to(go_from="red",
                                  go_to="blue",
                                  **kwargs)

    return [func]


def move_red_to_blue_2(population: Population, **kwargs):
    func = lambda **kwargs: go_to(go_from="red",
                                  go_to="blue",
                                  **kwargs)

    if population.day == 2:
        return [func]
    else:
        return []


def move_blue_to_red_2(population: Population, **kwargs):
    func = lambda **kwargs: go_to(go_from="blue",
                                  go_to="red",
                                  **kwargs)

    if population.day == 2:
        return [func]
    else:
        return []


def move_even_odd(population: Population, **kwargs):
    if population.day % 2 == 0:
        return move_red_to_blue(population=population, **kwargs)
    else:
        return move_blue_to_red(population=population, **kwargs)


def move_partial(population: Population, **kwargs):
    if population.day == 1:
        return move_blue_to_red(population=population, **kwargs)

    elif population.day == 2:
        func = lambda **kwargs: go_to(go_from="red",
                                      go_to="blue",
                                      fraction=0.7,
                                      **kwargs)

        return [func]
    else:
        return []


@pytest.mark.slow
def test_go_to(prompt=None, nthreads=1):
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
                                        mover=move_red_to_blue,
                                        nthreads=nthreads)

    OutputFiles.remove(outdir, prompt=None)

    # red demographic was seeded, but all moved to blue, so should have
    # no outbreak
    pop = trajectory[-1]
    print(pop)
    assert pop.susceptibles == pop.population
    assert pop.subpops[0].population == 0
    assert pop.subpops[1].population == pop.population

    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        trajectory = network.copy().run(population=population, seed=seed,
                                        output_dir=output_dir,
                                        nsteps=nsteps,
                                        mixer=mix_evenly,
                                        mover=move_blue_to_red,
                                        nthreads=nthreads)

    OutputFiles.remove(outdir, prompt=None)

    # red demographic was seeded so should all be affected
    final_pop = trajectory[-1]
    print(final_pop)
    assert final_pop.susceptibles != final_pop.population
    assert final_pop.subpops[0].population == final_pop.population
    assert final_pop.subpops[1].population == 0

    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        trajectory = network.copy().run(population=population, seed=seed,
                                        output_dir=output_dir,
                                        nsteps=nsteps,
                                        mixer=mix_evenly,
                                        mover=move_red_to_blue_2,
                                        nthreads=nthreads)

    OutputFiles.remove(outdir, prompt=None)

    # red seeded, but all moved to blue. Should have the same outbreak
    pop = trajectory[-1]
    print(final_pop)
    print(pop)
    assert pop.susceptibles == final_pop.susceptibles
    assert pop.total == final_pop.total
    assert pop.latent == final_pop.latent
    assert pop.recovereds == final_pop.recovereds

    with OutputFiles(outdir, force_empty=True, prompt=prompt) as output_dir:
        trajectory = network.copy().run(population=population, seed=seed,
                                        output_dir=output_dir,
                                        nsteps=nsteps,
                                        mixer=mix_evenly,
                                        mover=move_even_odd,
                                        nthreads=nthreads)

    OutputFiles.remove(outdir, prompt=None)

    # red seeded, but moved back and forth - should all be the same
    pop = trajectory[-1]
    print(final_pop)
    print(pop)
    assert pop.susceptibles == final_pop.susceptibles
    assert pop.total == final_pop.total
    assert pop.latent == final_pop.latent
    assert pop.recovereds == final_pop.recovereds


@pytest.mark.slow
def test_go_partial(prompt=None, nthreads=1):
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
                                        mover=move_partial,
                                        nthreads=nthreads)

    OutputFiles.remove(outdir, prompt=None)

    # 70% of the population (roughly) should be in "blue"
    pop = trajectory[-1]
    print(pop)

    frac0 = pop.subpops[0].population / pop.population
    frac1 = pop.subpops[1].population / pop.population
    print(frac0, frac1)
    # pytest.approx error is percent, e.g. 0.05 is within 5%
    assert pytest.approx(frac0, 0.1) == 0.3
    assert pytest.approx(frac1, 0.05) == 0.7
    assert pytest.approx(frac0+frac1, 0.01) == 1.0


if __name__ == "__main__":
    # test_go_to(nthreads=2)
    test_go_partial(nthreads=2)
