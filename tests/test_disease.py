
import os

from metawards import Disease

script_dir = os.path.dirname(__file__)

home_json = os.path.join(script_dir, "data", "lurgy_home.json")
super_json = os.path.join(script_dir, "data", "lurgy_super.json")


def test_disease():
    lurgy = Disease.load(home_json)
    super_lurgy = Disease.load(super_json)

    assert lurgy.mapping == ["*", "E", "I", "I", "R"]
    assert super_lurgy.mapping == ["*", "E", "I", "I", "I", "R"]

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
