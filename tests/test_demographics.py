
from metawards import Demographics

import os

script_dir = os.path.dirname(__file__)
demography_json = os.path.join(script_dir, "data", "demography.json")


def test_demographics():

    d0 = Demographics()
    assert len(d0) == 0

    d1 = Demographics()
    assert len(d1) == 0

    assert d0 == d1

    d0 = Demographics.load(demography_json)

    assert d0 != d1

    d1 = Demographics.load(demography_json)

    assert d0 == d1

    assert len(d0) == 3

    red = d0["red"]
    blue = d0["blue"]
    green = d0["green"]

    assert d0[0] == red
    assert d0[1] == green
    assert d0[2] == blue

    assert red.name == "red"
    assert red.work_ratio == 0.0
    assert red.play_ratio == 0.1

    assert blue.name == "blue"
    assert blue.work_ratio == 0.4
    assert blue.play_ratio == 0.1

    assert green.name == "green"
    assert green.work_ratio == 0.6
    assert green.play_ratio == 0.8

    d2 = Demographics()

    d2.add(red)
    d2.add(green)
    d2.add(blue)

    assert d0 == d2
