
from metawards import Ward, Wards, Network
import json
import os
import pytest

script_dir = os.path.dirname(__file__)

simple_network = os.path.join(script_dir, "data", "simple_network.json.bz2")


def test_wards():
    wards = Wards()
    bristol = Ward(name="Bristol")
    london = Ward(name="London")
    bristol.add_workers(500, destination=bristol)
    bristol.add_workers(500, destination=london)
    bristol.set_num_players(750)
    london.add_workers(8500, destination=london)
    london.add_workers(100, destination=bristol)
    london.set_num_players(10000)
    print(bristol)
    print(london)

    wards.add(bristol)
    wards.add(london)

    print(wards)

    assert wards.num_workers() == 9600
    assert wards.num_players() == 10750
    assert wards.population() == 10750 + 9600

    data = wards.to_data()

    print(data)

    wards2 = Wards.from_data(data)

    print(wards2)

    assert wards == wards2

    try:
        filename = "_test_wards.json"

        with open(filename, "w") as FILE:
            json.dump(data, FILE, indent=2)

        print("".join(open(filename).readlines()))

        with open(filename) as FILE:
            data2 = json.load(FILE)

        wards2 = Wards.from_data(data2)
        print(wards2)
        assert wards == wards2

    finally:
        import os
        os.unlink(filename)

    network = Network.from_wards(wards, disease="lurgy")

    assert network.work_population == wards.num_workers()
    assert network.play_population == wards.num_players()
    assert network.population == wards.population()

    wards2 = network.to_wards()

    assert len(wards) == len(wards2)

    for w1, w2 in zip(wards, wards2):
        if w1 is None:
            assert w2 is None
            continue

        assert w1.id() == w2.id()
        assert w1.name() == w2.name()
        assert w1.info() == w2.info()
        assert w1.num_workers() == w2.num_workers()
        assert w1.num_players() == w2.num_players()
        assert w1.get_player_lists() == w2.get_player_lists()
        assert w1.get_worker_lists() == w2.get_worker_lists()
        assert w1.position() == w2.position()

    s = wards.to_json()
    wards2 = Wards.from_json(s)

    assert wards2 == wards

    filename = wards.to_json("_test_wards_data.json", indent=4)

    print(filename)

    try:
        wards2 = Wards.from_json(filename)
    finally:
        import os
        os.unlink(filename)

    assert wards2 == wards


def test_add_wards():

    bristol = Ward("Bristol")
    london = Ward("London")
    glasgow = Ward("Glasgow")

    wards = Wards()

    assert bristol not in wards
    assert london not in wards
    assert glasgow not in wards

    bristol.add_workers(5, london)
    bristol.add_workers(10, bristol)
    bristol.add_workers(15, glasgow)

    assert not bristol.is_resolved()

    print(bristol._workers, bristol._players)

    bristol.add_player_weight(0.2, london)
    bristol.add_player_weight(0.5, glasgow)

    wards.add(bristol)

    assert bristol in wards
    assert london not in wards
    assert glasgow not in wards

    wards.add(london)

    assert london in wards
    assert glasgow not in wards

    assert bristol + london == wards

    wards2 = wards + glasgow

    assert glasgow in wards2

    wards += glasgow

    assert wards == wards2

    assert bristol + london + glasgow == wards

    print(wards)

    print(bristol._workers, bristol._players)

    assert not bristol.is_resolved()

    bristol2 = bristol.resolve(wards)

    print(bristol2)
    print(bristol2._workers, bristol2._players)

    assert bristol2.is_resolved()
    assert bristol != bristol2

    bristol2 = bristol2.dereference(wards)

    assert not bristol2.is_resolved()
    assert bristol == bristol2

    assert wards == wards2

    sheffield = Ward("Sheffield")
    norwich = Ward("Norwich")

    wards2 = sheffield + norwich

    print(wards)
    print(wards2)

    wards3 = wards + wards2

    print(wards3)

    assert bristol in wards3
    assert london in wards3
    assert glasgow in wards3
    assert sheffield in wards3
    assert norwich in wards3

    wards3 = wards2 + wards

    bristol2 = wards3["Bristol"]

    assert bristol2.is_resolved()

    print(bristol2._workers, bristol2._players)

    bristol2 = bristol2.dereference(wards3)

    assert not bristol2.is_resolved()

    print(bristol2._workers, bristol2._players)

    assert bristol == bristol2


def test_duplicate_wards():
    bristol = Ward("Bristol")
    bristol.set_num_players(100)

    london = Ward("London")
    london.set_num_players(200)

    bristol.add_workers(50, london)
    bristol.add_player_weight(0.5, london)

    wards = bristol + london

    print(wards)

    assert bristol in wards
    assert london in wards

    assert wards.num_workers() == bristol.num_workers() + london.num_workers()
    assert wards.num_players() == bristol.num_players() + london.num_players()

    print(wards.to_json())

    wlist1 = wards[bristol].get_worker_lists()
    plist1 = wards[bristol].get_player_lists()

    wards += bristol

    print(wards)

    print(wards.to_json())

    assert wards[bristol].num_players() == 2 * bristol.num_players()
    assert wards[bristol].num_workers() == 2 * bristol.num_workers()

    wlist2 = wards[bristol].get_worker_lists()
    plist2 = wards[bristol].get_player_lists()

    print(wlist1)
    print(wlist2)

    assert wlist1[0][0] == wlist2[0][0]
    assert 2 * wlist1[1][0] == wlist2[1][0]

    print(plist1)
    print(plist2)

    assert plist1 == plist2


def test_harmonise_wards():
    bristol = Ward("Bristol")
    london = Ward("London")
    oxford = Ward("Oxford")

    bristol.set_num_players(1000)
    london.set_num_players(5000)
    oxford.set_num_players(800)

    bristol.add_workers(500, destination=bristol)
    bristol.add_workers(200, destination=oxford)
    bristol.add_workers(900, destination=london)

    oxford.add_workers(100, destination=bristol)
    oxford.add_workers(1000, destination=oxford)
    oxford.add_workers(2000, destination=london)

    london.add_workers(100, destination=bristol)
    london.add_workers(400, destination=oxford)
    london.add_workers(10000, destination=london)

    bristol.add_player_weight(0.1, destination=oxford)
    oxford.add_player_weight(0.2, destination=bristol)
    oxford.add_player_weight(0.15, destination=london)
    london.add_player_weight(0.3, destination=oxford)

    home_wards = bristol + london + oxford
    print(home_wards)

    holiday = Ward("holiday")
    bristol = Ward("Bristol")
    oxford = Ward("Oxford")
    holiday.add_player_weight(0.5, destination=bristol)
    holiday.add_player_weight(0.5, destination=oxford)

    holiday_wards = bristol + oxford + holiday
    print(holiday_wards)

    hospital = Ward("hospital")
    london = Ward("London")
    london.add_workers(50, destination=hospital)
    hospital.set_num_players(150)

    hospital_wards = london + hospital
    print(hospital_wards)

    overall, harmonised = Wards.harmonise([home_wards, holiday_wards,
                                           hospital_wards])

    print(overall)
    print(harmonised)

    assert overall.num_workers() == home_wards.num_workers() + \
        holiday_wards.num_workers() + \
        hospital_wards.num_workers()

    assert overall.num_players() == home_wards.num_players() + \
        holiday_wards.num_players() + \
        hospital_wards.num_players()

    assert harmonised[0].num_workers() == home_wards.num_workers()
    assert harmonised[0].num_players() == home_wards.num_players()
    assert harmonised[1].num_workers() == holiday_wards.num_workers()
    assert harmonised[1].num_players() == holiday_wards.num_players()
    assert harmonised[2].num_workers() == hospital_wards.num_workers()
    assert harmonised[2].num_players() == hospital_wards.num_players()

    print(overall.to_json())


@pytest.mark.parametrize("scl", [1.0, 2.0, 0.5, 0.1, 0.0])
def test_scale_wards(scl):
    wards = Wards.from_json(simple_network)

    def scale_and_round(value, scale):
        import math

        if scale > 0.5:
            # round up for large scales, as smaller scales will always
            # round down
            return int(math.floor((value * scale) + 0.5))
        else:
            # rounding down - hopefully this will minimise the number
            # of values that need to be redistributed
            return int(math.floor(value * scale))

    wards2 = scl * wards

    if int(scl) == scl:
        assert scale_and_round(wards.num_players(),
                               scl) == wards2.num_players()
        assert scale_and_round(wards.num_workers(),
                               scl) == wards2.num_workers()

    for w1, w2 in zip(wards._wards, wards2._wards):
        if w1 is None:
            assert w2 is None
            continue

        assert scale_and_round(w1.num_players(), scl) == w2.num_players()

        for key, value in w1._workers.items():
            assert scale_and_round(value, scl) == w2._workers[key]

    wards2 = wards.scale(work_ratio=scl)

    assert wards.num_players() == wards2.num_players()

    if int(scl) == scl:
        assert scale_and_round(wards.num_workers(),
                               scl) == wards2.num_workers()

    for w1, w2 in zip(wards._wards, wards2._wards):
        if w1 is None:
            assert w2 is None
            continue

        assert w1.num_players() == w2.num_players()

        for key, value in w1._workers.items():
            assert scale_and_round(value, scl) == w2._workers[key]

    wards2 = wards.scale(play_ratio=scl)

    if int(scl) == scl:
        assert scale_and_round(wards.num_players(),
                               scl) == wards2.num_players()
        assert wards.num_workers() == wards2.num_workers()

    for w1, w2 in zip(wards._wards, wards2._wards):
        if w1 is None:
            assert w2 is None
            continue

        assert scale_and_round(w1.num_players(), scl) == w2.num_players()


if __name__ == "__main__":
    test_add_wards()
    test_wards()
    test_duplicate_wards()
    test_harmonise_wards()
    test_scale_wards(2.0)
