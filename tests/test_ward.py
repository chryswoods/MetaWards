
from metawards import WardInfo, Ward, Wards, Parameters, Network
from metawards.utils import Profiler, Console
import json
import pytest


def _assert_equal(x, y, delta=1e-10):
    if x != y:
        if abs(x - y) > delta:
            print(f"{x} != {y}")
            assert x == y


def test_ward_json():
    w = WardInfo(name="something", alternate_names=["one", "two"],
                 code="123", alternate_codes=["1", "2", "cat"],
                 authority="somewhere", authority_code="s123",
                 region="place name", region_code="r789")

    s = json.dumps(w.to_data())
    print(s)

    w2 = WardInfo.from_data(json.loads(s))

    assert w == w2

    ward = Ward(id=10, info=w)

    ward.set_position(x=1500, y=2500, units="m")
    ward.set_num_players(1200)
    ward.set_num_workers(500)

    ward.add_workers(number=30, destination=1)
    ward.add_workers(number=20, destination=30)

    ward.add_player_weight(weight=0.2, destination=30)
    ward.add_player_weight(weight=0.5, destination=1)

    print(ward)

    s = json.dumps(ward.to_data())

    print(s)

    ward2 = Ward.from_data(json.loads(s))

    assert json.dumps(ward.to_data()) == json.dumps(ward2.to_data())
    assert ward == ward2

    ward2 = Ward(id=1, name="something else")

    ward3 = Ward(id=30, name="another name")

    wards = Wards([ward, ward2, ward3])

    print(wards)

    _assert_equal(wards[ward.id()], ward)
    _assert_equal(wards[ward2.id()], ward2)
    _assert_equal(wards[ward3.id()], ward3)

    s = json.dumps(wards.to_data())

    print(s)

    wards2 = Wards.from_data(json.loads(s))

    assert wards == wards2

    ward3 = Ward(id=50, name="another ward")
    wards2.insert(ward3)

    assert wards != wards2


@pytest.mark.slow
def test_ward_conversion():
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

    params.set_input_files("2011Data")

    print("Building the network...")
    network = Network.build(params=params)

    profiler = Profiler()

    profiler = profiler.start("to_json")
    wards = network.to_wards(profiler=profiler)

    print(f"{wards.num_workers()} / {wards.num_players()}")

    _assert_equal(wards.num_workers(), network.work_population)
    _assert_equal(wards.num_players(), network.play_population)

    print(f"{wards.num_work_links()} / {wards.num_play_links()}")

    _assert_equal(wards.num_work_links(), network.nlinks)
    _assert_equal(wards.num_play_links(), network.nplay)

    print("Converting to data...")
    data = wards.to_data(profiler=profiler)

    print("Converting to json...")
    profiler = profiler.start("Convert to JSON")
    s = json.dumps(data)
    profiler = profiler.stop()

    profiler = profiler.stop()  #  end to_json

    print(f"Done - {len(s)/(1024*1024.0)} MB : {s[0:1024]}...")

    print(f"Converting from json...")
    profiler = profiler.start("Convert from JSON")

    profiler = profiler.start("from_json")
    data = json.loads(s)
    profiler = profiler.stop()

    wards2 = Wards.from_data(data, profiler=profiler)

    assert wards2 == wards

    network2 = Network.from_wards(wards2, profiler=profiler)

    profiler = profiler.stop()

    Console.print(profiler)

    Console.print("Validating equality - may take some time...")

    _assert_equal(network2.nnodes, network.nnodes)
    _assert_equal(network2.nlinks, network.nlinks)
    _assert_equal(network2.nplay, network.nplay)

    if network.info is None:
        assert network2.info is None

    _assert_equal(len(network.info), len(network2.info))

    Console.print(f"{len(network.info)}, {network.nnodes}")

    with Console.progress() as progress:
        task1 = progress.add_task("Validating info", total=len(network.info))
        task2 = progress.add_task("Validating nodes", total=network.nnodes)
        task3 = progress.add_task("Validating work", total=network.nlinks)
        task4 = progress.add_task("Validating play", total=network.nplay)

        for i in range(0, len(network.info)):
            assert network.info[i] == network2.info[i]
            progress.update(task1, advance=1)

        progress.update(task1, completed=len(network.info), force_update=True)

        for i in range(1, network.nnodes + 1):
            _assert_equal(network.nodes.label[i], network2.nodes.label[i])
            _assert_equal(
                network.nodes.begin_to[i], network2.nodes.begin_to[i])
            _assert_equal(network.nodes.end_to[i], network2.nodes.end_to[i])
            _assert_equal(network.nodes.self_w[i], network2.nodes.self_w[i])
            _assert_equal(network.nodes.begin_p[i], network2.nodes.begin_p[i])
            _assert_equal(network.nodes.end_p[i], network2.nodes.end_p[i])
            _assert_equal(network.nodes.self_p[i], network2.nodes.self_p[i])
            _assert_equal(network.nodes.x[i], network2.nodes.x[i])
            _assert_equal(network.nodes.y[i], network2.nodes.y[i])
            progress.update(task2, advance=1)

        progress.update(task2, completed=network.nnodes, force_update=True)

        for i in range(1, network.nlinks + 1):
            _assert_equal(network.links.ifrom[i], network2.links.ifrom[i])
            _assert_equal(network.links.ito[i], network2.links.ito[i])
            _assert_equal(network.links.weight[i], network2.links.weight[i])
            _assert_equal(network.links.suscept[i], network2.links.suscept[i])
            progress.update(task3, advance=1)

        progress.update(task3, completed=network.nlinks, force_update=True)

        for i in range(1, network.nplay + 1):
            _assert_equal(network.play.ifrom[i], network2.play.ifrom[i])
            _assert_equal(network.play.ito[i], network2.play.ito[i])
            _assert_equal(network.play.weight[i], network2.play.weight[i])
            _assert_equal(network.play.suscept[i], network2.play.suscept[i])
            progress.update(task4, advance=1)

        progress.update(task4, completed=network.nplay, force_update=True)


if __name__ == "__main__":
    test_ward_json()
    test_ward_conversion()
