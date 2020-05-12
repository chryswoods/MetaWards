
import pytest


@pytest.mark.slow
def test_lookup(shared_network):
    network = shared_network

    info = network.info

    all_wards = info.find()
    assert len(all_wards) == network.nnodes

    bristol = info.find("Bristol")

    assert len(bristol) == 0

    clifton = info.find("Clifton")

    for c in clifton:
        assert info[c].name.find("Clifton") != -1

    assert len(clifton) == 13

    clifton2 = info.find("clifton")

    assert clifton == clifton2

    bristol = info.find(authority="bristol")

    assert len(bristol) == 35

    clifton_bristol = info.find(name="Clifton", authority="Bristol")

    assert len(clifton_bristol) == 2

    clifton_bristol = info.find(name=r"^clifton$", authority="bristol")[0]

    assert clifton_bristol == 3662

    clifton = info[clifton_bristol]

    assert clifton.name == "Clifton"
    assert clifton.code == "E05001980"
    assert clifton.alternate_names[0] == "Clifton"
    assert clifton.alternate_codes[0] == "E36000533"
    assert clifton.authority == "Bristol, City of"
    assert clifton.authority_code == "E06000023"

    clifton2 = info.find("E05001980")

    assert clifton2[0] == clifton_bristol


if __name__ == "__main__":
    test_lookup()
