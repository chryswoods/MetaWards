
from metawards import Wards, Parameters, Demographics

import os

script_dir = os.path.dirname(__file__)

main_json = os.path.join(script_dir, "data", "main.json.bz2")
students_json = os.path.join(script_dir, "data", "students.json.bz2")
teachers_json = os.path.join(script_dir, "data", "teachers.json.bz2")
multinetwork_json = os.path.join(script_dir, "data", "multinetwork.json")


def test_harmonise():
    main = Wards.from_json(main_json)
    students = Wards.from_json(students_json)
    teachers = Wards.from_json(teachers_json)

    overall, subnets = Wards.harmonise([main, students, teachers])

    print(overall)
    print(subnets)

    total_pop = total_workers = total_players = 0

    assert len(subnets) == 3

    for subnet in subnets:
        total_pop += subnet.population()
        total_workers += subnet.num_workers()
        total_players += subnet.num_players()

    assert overall.population() == total_pop
    assert overall.num_workers() == total_workers
    assert overall.num_players() == total_players

    print(overall.to_json())

    # must have the same wards and same links in all
    for subnet in subnets:
        assert len(subnet) == len(overall)
        for overall_ward, other_ward in zip(overall, subnet):
            if overall_ward is None:
                assert other_ward is None
            elif other_ward is None:
                assert overall_ward is None
            else:
                assert overall_ward.id() == other_ward.id()
                assert overall_ward.info() == other_ward.info()

                assert len(overall_ward._workers) == len(other_ward._workers)
                assert len(overall_ward._players) == len(other_ward._players)

                for key in overall_ward._workers.keys():
                    assert key in other_ward._workers

                for key in overall_ward._players.keys():
                    assert key in other_ward._players

        print(subnet.to_json())


def test_duplicated_harmonise():
    params = Parameters.load()
    params.set_disease("ncov")

    demographics = Demographics.load(multinetwork_json)

    network = demographics.build(params=params)

    assert len(network.subnets) == 5

    main = Wards.from_json(main_json)
    students = Wards.from_json(students_json)
    teachers = Wards.from_json(teachers_json)

    assert network.overall.population == main.population() + \
        students.population() + \
        teachers.population()

    assert network.subnets[0].population == main.population()
    assert network.subnets[1].population == int(0.7 * teachers.population())
    assert network.subnets[2].population == int(0.7 * students.population())
    assert network.subnets[3].population == int(0.3 * teachers.population())
    assert network.subnets[4].population == int(0.3 * students.population())


if __name__ == "__main__":
    test_harmonise()
    test_duplicated_harmonise()
