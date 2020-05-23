
from metawards import Parameters, Disease, VariableSet, VariableSets

import os
import pytest

script_dir = os.path.dirname(__file__)
ncovparams_csv = os.path.join(script_dir, "data", "ncovparams.csv")
testparams_csv = os.path.join(script_dir, "data", "testparams.csv")
testparams2_csv = os.path.join(script_dir, "data", "testparams2.csv")
testparams3_csv = os.path.join(script_dir, "data", "testparams3.csv")
testparams4_csv = os.path.join(script_dir, "data", "testparams4.csv")

l0 = {'beta[2]': 0.95, 'beta[3]': 0.95,
      'progress[1]': 0.19, 'progress[2]': 0.91, 'progress[3]': 0.91}

l1 = {'beta[2]': 0.90, 'beta[3]': 0.93,
      'progress[1]': 0.18, 'progress[2]': 0.92, 'progress[3]': 0.90}

vars01 = VariableSets()
vars01.append(l0)
vars01.append(l1)

vars0 = VariableSets()
vars0.append(l0)

vars1 = VariableSets()
vars1.append(l1)


def test_variableset():
    v1 = VariableSet()
    v2 = VariableSet()

    assert len(v1) == 0
    assert len(v2) == 0

    with pytest.raises(KeyError):
        v1["beta[1]"]

    v1["beta[1]"] = 0.5

    assert v1["beta[1]"] == 0.5
    assert len(v1) == 1

    assert v1 != v2

    v2["beta[1]"] = 0.5

    assert v1 == v2

    d = Disease.load("ncov")

    p = Parameters()
    p.set_disease("ncov")

    assert p.disease_params == d

    assert p.disease_params.beta[1] != 0.5

    p = p.set_variables(v1)

    assert p.disease_params.beta[1] == 0.5


@pytest.mark.parametrize('lines, expect',
                         [(0, vars0),
                          (1, vars1),
                          ([0, 1], vars01),
                          ([1, 0], vars01)])
def test_read_variables(lines, expect):
    result = Parameters.read_variables(testparams2_csv, lines)
    print(f"{result} == {expect}?")
    assert result == expect


@pytest.mark.parametrize('lines, expect, repeats',
                         [(0, vars0, [2]),
                          (1, vars1, [4]),
                          ([0, 1], vars01, [2, 4]),
                          ([1, 0], vars01, [2, 4])])
def test_read_variables(lines, expect, repeats):
    result = Parameters.read_variables(testparams4_csv, lines)
    r = expect.repeat(repeats)
    print(f"{result} ==\n{r}?")
    assert result == r


@pytest.mark.parametrize('lines, expect',
                         [(0, vars0),
                          (1, vars1),
                          ([0, 1], vars01),
                          ([1, 0], vars01)])
def test_read_variables2(lines, expect):
    result = Parameters.read_variables(ncovparams_csv, lines)
    print(f"{result} == {expect}?")
    assert result == expect


def test_parameterset():
    vars0 = VariableSet(variables=l0)

    assert vars0.repeat_index() == 1

    for key, value in l0.items():
        assert key in vars0.variable_names()
        assert value in vars0.variable_values()
        assert vars0[key] == value

    vars1 = VariableSet(l1, 2)

    assert vars1.repeat_index() == 2

    for key, value in l1.items():
        assert key in vars1.variable_names()
        assert value in vars1.variable_values()
        assert vars1[key] == value

    assert vars0.fingerprint() != vars1.fingerprint()
    assert vars0.fingerprint() != vars0.fingerprint(include_index=True)
    assert vars1.fingerprint() != vars1.fingerprint(include_index=True)

    variables = VariableSets()
    assert len(variables) == 0

    variables.append(vars0)
    variables.append(vars1)

    assert len(variables) == 2
    assert variables[0] == vars0
    assert variables[1] == vars1

    variables = variables.repeat(5)

    assert len(variables) == 10

    for i in range(0, 5):
        idx0 = 2*i
        idx1 = idx0 + 1

        print(f"{idx0} : {variables[idx0]} vs {l0}")
        print(f"{idx1} : {variables[idx1]} vs {l1}")

        assert variables[idx0].variables() == l0
        assert variables[idx1].variables() == l1
        assert variables[idx0].fingerprint() == vars0.fingerprint()
        assert variables[idx1].fingerprint() == vars1.fingerprint()
        assert variables[idx0].repeat_index() == i+1
        assert variables[idx1].repeat_index() == i+1


def test_make_compatible():
    v1 = VariableSet()
    v1["beta[1]"] = 0.95
    v1["beta[2]"] = 0.9

    v2 = VariableSet(repeat_index=5)
    v2["beta[2]"] = 0.5

    v3 = v2.make_compatible_with(v1)
    assert v3["beta[1]"] == v1["beta[1]"]
    assert v2["beta[2]"] == v2["beta[2]"]
    assert v3.repeat_index() == v2.repeat_index()

    with pytest.raises(ValueError):
        v1.make_compatible_with(v2)


def test_set_variables():
    d = Disease.load("ncov")

    p = Parameters()
    p.set_disease("ncov")

    assert p.disease_params == d

    variables = VariableSet(l1)

    p2 = p.set_variables(variables)

    assert p.disease_params == d
    assert p2.disease_params != d

    assert p2.disease_params.beta[2] == 0.9
    assert p2.disease_params.beta[3] == 0.93
    assert p2.disease_params.progress[1] == 0.18
    assert p2.disease_params.progress[2] == 0.92
    assert p2.disease_params.progress[3] == 0.90

    variables = VariableSet(l0)

    p3 = p2.set_variables(variables)

    assert p3.disease_params.beta[2] == 0.95
    assert p3.disease_params.beta[3] == 0.95
    assert p3.disease_params.progress[1] == 0.19
    assert p3.disease_params.progress[2] == 0.91
    assert p3.disease_params.progress[3] == 0.91


def test_set_custom():

    horiz = os.path.join(script_dir, "data", "horizontal.dat")
    vert = os.path.join(script_dir, "data", "vertical.dat")

    h = VariableSet.read(horiz)

    v = VariableSet.read(vert)

    assert v == h

    assert v[".something[1]"] == 5.0
    assert v["user.another[2]"] == 100.0
    assert v[".flag"] == 1.0
    assert v["beta[3]"] == 0.5


@pytest.mark.slow
def test_read_edgecase():
    vertical2 = os.path.join(script_dir, "data", "vertical2.dat")
    v = VariableSet.read(vertical2)

    from datetime import date
    d = date(year=2020, month=12, day=31)

    print(v)
    assert v[".animal"] == "cat"
    assert v[".long"] == "This is a really long line"
    assert v[".comma"] == "This is a long line with, a comma!"
    assert v[".string"] == "2020-12-31"
    assert v[".date"] == d
    assert v[".date2"] == d
    assert v[".date3"] == d
    assert v[".int"] == 42
    assert v[".float"] == 3.141
    assert v[".bool"]
    assert not v[".bool2"]

    v = VariableSet.read(testparams3_csv)
    print(v)

    assert v["beta[0]"] == 0.5
    assert v["beta[1]"] == 0.6
    assert v["progress[0]"] == 0.6
    assert v["progress[1]"] == 5
    assert v[".date"] == d
    assert v[".number"] == 2

    try:
        from dateparser import parse
    except ImportError:
        parse = None

    if parse is not None:
        print(v[".date2"])
        d2 = parse("five days ago").date()
        print(d2)
        assert v[".date2"] == d2
    else:
        print("string")
        assert v[".date2"] == "five days ago"


if __name__ == "__main__":
    test_variableset()
    test_parameterset()
    test_make_compatible()
    test_set_variables()
    test_set_custom()
    test_read_edgecase()
