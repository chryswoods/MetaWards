
from metawards import Network, Ward, Disease, Parameters, OutputFiles, \
    Population

from metawards.extractors import extract_default

import os

script_dir = os.path.dirname(__file__)


def _check_infections(**kwargs):
    def check(population, workspace, **kwargs):
        if population.day > 5:
            S = workspace.S_in_wards
            R = workspace.R_in_wards
            print(S)
            print(R)

            # No infections in oxford
            assert S[3] == 100
            assert R[3] == 0

            # bristol has more infections than london
            assert S[1] < S[2]
            assert R[1] > R[2]

    return extract_default(**kwargs) + [check]


def test_bg_foi():
    bristol = Ward("Bristol")
    london = Ward("London")
    oxford = Ward("Oxford")

    bristol.set_num_players(100)
    london.set_num_players(100)
    oxford.set_num_players(100)

    bristol.set_bg_foi(10)
    london.set_bg_foi(1)

    wards = bristol + london + oxford

    lurgy = Disease("lurgy")

    lurgy.add("E", beta=0.0, progress=1.0)
    lurgy.add("I", beta=0.0, progress=1.0)
    lurgy.add("R")

    params = Parameters()
    params.set_disease(lurgy)

    network = Network.from_wards(wards, params=params)

    outdir = os.path.join(script_dir, "test_bg_foi")

    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        trajectory = network.run(population=Population(),
                                 output_dir=output_dir,
                                 extractor=_check_infections)

    OutputFiles.remove(outdir, prompt=None)

    # the only source of infection should be the bg. Should have
    # no infections in oxford, some in london and most in bristol
    print(trajectory[-1])

    assert trajectory[-1].recovereds <= 200
    assert trajectory[-1].susceptibles >= 100


if __name__ == "__main__":
    test_bg_foi()
