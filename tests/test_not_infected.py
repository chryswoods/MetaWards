
from metawards import Disease, Network, Population, Parameters, OutputFiles, \
    Demographics

import os

script_dir = os.path.dirname(__file__)
redblue_json = os.path.join(script_dir, "data", "redblue.json")


def test_not_infected():
    # create a disease where it will finish with everyone in the V state
    lurgy = Disease("lurgy")
    lurgy.add("E", beta=0.0, progress=1.0)
    lurgy.add("I1", beta=0.4, progress=0.2)
    lurgy.add("I2", beta=0.5, progress=0.5, too_ill_to_move=0.5)
    lurgy.add("I3", beta=0.5, progress=0.8, too_ill_to_move=0.8)
    lurgy.add("V", beta=0.0, progress=0.0, is_infected=False)
    lurgy.add("R")

    params = Parameters()
    params.set_input_files("single")
    params.add_seeds("5")
    params.set_disease(lurgy)

    network = Network.build(params=params, population=Population(1000))

    outdir = os.path.join(script_dir, "test_not_infected")

    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        trajectory = network.copy().run(population=Population(),
                                        output_dir=output_dir,
                                        nsteps=1000, nthreads=1)

    # should finish at about 60 days and not run to 1000
    p = trajectory[-1]
    assert p.day < 900

    # there should be no recovereds, as all who were ill went to 'others'
    assert p.recovereds == 0
    assert p.others == p.population - p.susceptibles

    # Now repeat with more threads
    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        trajectory = network.copy().run(population=Population(),
                                        output_dir=output_dir,
                                        nsteps=1000, nthreads=8)

    # should finish at about 60 days and not run to 1000
    p = trajectory[-1]
    assert p.day < 900

    # there should be no recovereds, as all who were ill went to 'others'
    assert p.recovereds == 0
    assert p.others == p.population - p.susceptibles

    # now repeat with demographics
    demographics = Demographics.load(redblue_json)

    network.params.add_seeds("demographic,number\\n1,10")

    network = network.specialise(demographics)

    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        trajectory = network.copy().run(population=Population(),
                                        output_dir=output_dir,
                                        nsteps=1000)

    # should finish at about 60 days and not run to 1000
    p = trajectory[-1]
    assert p.day < 900
    assert p.recovereds == 0
    assert p.others > 0
    assert p.others == p.population - p.susceptibles

    p_red = p.subpops[0]
    p_blue = p.subpops[1]

    assert p_red.day < 900
    assert p_red.recovereds == 0
    assert p_red.others > 0
    assert p_red.others == p_red.population - p_red.susceptibles

    assert p_blue.day < 900
    assert p_blue.recovereds == 0
    assert p_blue.others > 0
    assert p_blue.others == p_blue.population - p_blue.susceptibles

    OutputFiles.remove(outdir, prompt=None)


if __name__ == "__main__":
    test_not_infected()
