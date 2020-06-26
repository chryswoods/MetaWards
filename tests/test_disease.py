
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


if __name__ == "__main__":
    test_disease()
    test_disease_hospital()
