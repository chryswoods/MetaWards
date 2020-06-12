
import pytest
import os

from metawards import VariableSets

script_dir = os.path.dirname(__file__)
ncovparams_csv = os.path.join(script_dir, "data", "ncovparams.csv")
params_with_repeats_csv = os.path.join(script_dir, "data",
                                       "params_with_repeats.csv")
compliance_dat = os.path.join(script_dir, "data", "compliance.dat")


def test_variableset():
    variables = VariableSets.read(ncovparams_csv)

    assert len(variables) == 2

    for v in variables:
        assert v.repeat_index() == 1

    v2 = variables.repeat(2)

    assert len(v2) == 4

    assert v2[0] == variables[0]
    assert v2[1] == variables[1]
    assert v2[2].variables() == variables[0].variables()
    assert v2[2].repeat_index() == 2
    assert v2[3].variables() == variables[1].variables()
    assert v2[3].repeat_index() == 2

    v3 = variables.repeat([2, 4])

    assert len(v3) == 6

    assert v3[0] == variables[0]
    assert v3[1] == variables[1]
    assert v3[2].variables() == variables[0].variables()
    assert v3[2].repeat_index() == 2
    assert v3[3].variables() == variables[1].variables()
    assert v3[3].repeat_index() == 2
    assert v3[4].variables() == variables[1].variables()
    assert v3[4].repeat_index() == 3
    assert v3[5].variables() == variables[1].variables()
    assert v3[5].repeat_index() == 4

    v4 = variables.repeat([4, 2])

    assert len(v4) == 6

    assert v4[0] == variables[0]
    assert v4[1] == variables[1]
    assert v4[2].variables() == variables[0].variables()
    assert v4[2].repeat_index() == 2
    assert v4[3].variables() == variables[1].variables()
    assert v4[3].repeat_index() == 2
    assert v4[4].variables() == variables[0].variables()
    assert v4[4].repeat_index() == 3
    assert v4[5].variables() == variables[0].variables()
    assert v4[5].repeat_index() == 4

    with pytest.raises(ValueError):
        variables.repeat([2, 4, 6])

    for variable in v4:
        assert variable.output_dir() == variable.fingerprint(
            include_index=True)


def test_variables_with_repeats():
    from metawards.utils import Profiler
    p = Profiler()
    p = p.start("read")
    variables = VariableSets.read(params_with_repeats_csv)
    p = p.stop()

    p = p.start("loop")
    for variable in variables:
        assert variable.output_dir() != variable.fingerprint(
            include_index=True)

        o = "beta_%.1f_ill_%.2f" % (variable["beta[2]"],
                                    variable["too_ill_to_move[2]"])
        o = o.replace(".", "i")

        print(variable.output_dir(), o)

        assert variable.output_dir() == o
    p = p.stop()
    print(p)


def test_variables_compliance():
    variables = VariableSets.read(compliance_dat)

    assert len(variables) == 11

    values = [1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7,
              0.65, 0.6, 0.55, 0.5]

    for variable, f in zip(variables, values):
        print(variable)
        print(len(variable))
        print(variable[".compliance"], f)
        assert len(variable) == 1
        assert variable[".compliance"] == f


if __name__ == "__main__":
    test_variableset()
    test_variables_with_repeats()
    test_variables_compliance()
