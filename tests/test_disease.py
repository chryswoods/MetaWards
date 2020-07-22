
import os
import pytest

from metawards import Disease

script_dir = os.path.dirname(__file__)

home_json = os.path.join(script_dir, "data", "lurgy_home.json")
super_json = os.path.join(script_dir, "data", "lurgy_super.json")
hospital_json = os.path.join(script_dir, "data", "lurgy_hospital.json")
overall_json = os.path.join(script_dir, "data", "lurgy_overall.json")


def test_disease_hospital():
    lurgy = Disease.load(hospital_json)
    print(lurgy)

    assert lurgy.mapping == ["H", "H", "ICU", "R"]
    assert lurgy.stage == ["H1", "H2", "ICU", "R"]
    assert lurgy.start_symptom == 1

    super_lurgy = Disease.load(super_json)

    mapping = lurgy.get_mapping_to(super_lurgy)
    print(mapping)

    assert mapping == [2, 3, 4, 5]

    with pytest.raises(ValueError):
        mapping = super_lurgy.get_mapping_to(lurgy)

    lurgy_overall = Disease.load(overall_json)
    print(lurgy_overall)

    assert lurgy_overall.mapping == ["*", "E", "I", "H", "ICU", "R"]

    mapping = lurgy.get_mapping_to(lurgy_overall)
    print(mapping)

    assert mapping == [3, 3, 4, 5]

    mapping = super_lurgy.get_mapping_to(lurgy_overall)
    print(mapping)

    assert mapping == [0, 1, 2, 2, 2, 5]


def test_disease():
    lurgy = Disease.load(home_json)
    print(lurgy)
    super_lurgy = Disease.load(super_json)
    print(super_lurgy)

    assert lurgy.mapping == ["*", "E", "I", "I", "R"]
    assert lurgy.stage == ["*", "E", "I1", "I2", "R"]
    assert super_lurgy.mapping == ["*", "E", "I", "I", "I", "R"]
    assert super_lurgy.stage == ["*", "E", "I1", "I2", "I3", "R"]

    assert super_lurgy.get_mapping_to(super_lurgy) is None
    assert lurgy.get_mapping_to(lurgy) is None

    mapping = super_lurgy.get_mapping_to(lurgy)

    print(mapping)

    assert len(mapping) == super_lurgy.N_INF_CLASSES()

    assert mapping == [0, 1, 2, 3, 3, 4]

    mapping = lurgy.get_mapping_to(super_lurgy)

    print(mapping)

    assert len(mapping) == lurgy.N_INF_CLASSES()

    assert mapping == [0, 1, 2, 3, 5]


def test_disease_api():
    d = Disease(name="lurgy")

    d.add("E", progress=0.25)
    d.add("I1", progress=0.5, beta=0.7)
    d.add("I2", progress=0.2, beta=0.3)
    d.add("R")

    assert len(d) == 4
    assert d.start_symptom == 2

    assert d[0]["name"] == "E"
    assert d[1]["name"] == "I1"
    assert d[2]["name"] == "I2"
    assert d[3]["name"] == "R"

    assert d.mapping == ["E", "I", "I", "R"]
    assert d.beta == [0.0, 0.7, 0.3, 0.0]
    assert d.progress == [0.25, 0.5, 0.2, 0.0]
    assert d.too_ill_to_move == [0.0, 0.0, 0.0, 0.0]
    assert d.contrib_foi == [1.0, 1.0, 1.0, 1.0]

    s = d.to_json(indent=4)
    print(s)

    d2 = Disease.from_json(s)

    assert d == d2

    d2.insert(3, "I3", beta=0.1, progress=0.1)

    assert d != d2

    assert d2.stage == ["E", "I1", "I2", "I3", "R"]
    assert d2.mapping == ["E", "I", "I", "I", "R"]
    assert d2.beta == [0.0, 0.7, 0.3, 0.1, 0.0]
    assert d2.progress == [0.25, 0.5, 0.2, 0.1, 0.0]
    assert d2.too_ill_to_move == [0.0, 0.0, 0.0, 0.0, 0.0]
    assert d2.contrib_foi == [1.0, 1.0, 1.0, 1.0, 1.0]


if __name__ == "__main__":
    test_disease()
    test_disease_hospital()
    test_disease_api()
