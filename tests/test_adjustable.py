
import pytest

from metawards import Parameters, VariableSet


def test_adjustable():

    params = Parameters.load()
    params.set_disease("lurgy")

    variables = VariableSet()
    variables["user.something[5]"] = 0.5
    variables["user.something[2]"] = 0.3
    variables["user.another[1]"] = 0.8
    variables["user.flag"] = True   # this will be converted to 1.0

    variables["beta[2]"] = 0.2
    variables["too_ill_to_move[1]"] = 0.15
    variables["progress[0]"] = 0.99
    variables["contrib_foi[4]"] = 0.45

    variables["length_day"] = 0.75
    variables["plength_day"] = 0.85

    variables["UV"] = 0.4

    with pytest.raises(KeyError):
        variables["broken"] = 0.9

    with pytest.raises(KeyError):
        variables["Beta[2]"] = 0.8

    variables.adjust(params)

    print(params)
    print(params.disease_params)
    print(params.user_params)

    assert params.user_params["something"][5] == 0.5
    assert params.user_params["something"][2] == 0.3
    assert params.user_params["another"][1] == 0.8
    assert params.user_params["flag"] == 1.0

    assert params.disease_params.beta[2] == 0.2
    assert params.disease_params.too_ill_to_move[1] == 0.15
    assert params.disease_params.progress[0] == 0.99
    assert params.disease_params.contrib_foi[4] == 0.45

    assert params.length_day == 0.75
    assert params.plength_day == 0.85
    assert params.UV == 0.4


if __name__ == "__main__":
    test_adjustable()
