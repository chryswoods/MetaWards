

import pytest
import math
from datetime import date
from dateparser import parse
from metawards import Interpret


@pytest.mark.parametrize("s, expect", [
    ("5", 5),
    (10, 10),
    (3.4, 3),
    ("10 * 5", 50),
    ("-3", -3),
    ("(-6 * 10) + 30", -30)
])
def test_interpret_integer(s, expect):
    v = Interpret.integer(s)
    assert v == expect


@pytest.mark.parametrize("s, expect", [
    ("5", 5),
    (10, 10),
    (3.4, 3.4),
    ("50%", 0.5),
    ("(10 + 20)%", 0.3),
    ("10 * 5", 50),
    ("-3", -3),
    ("(-6 * 10) + 30", -30),
    ("pi", math.pi),
    ("cos(0.5)", math.cos(0.5)),
    ("4.2 + pi**2", 4.2 + math.pi**2)
])
def test_interpret_number(s, expect):
    v = Interpret.number(s)
    assert v == expect


@pytest.mark.parametrize("s, expect", [
    ("true", True),
    ("tRuE  ", True),
    ("fAlsE", False),
    ("  no  ", False),
    (1, True),
    (0, False),
    (True, True),
    (False, False)
])
def test_interpret_bool(s, expect):
    v = Interpret.boolean(s)
    assert v == expect


@pytest.mark.parametrize("s, expect", [
    ("March 10th", parse("March 10th").date()),
    ("2020-06-24", date(year=2020, month=6, day=24)),
    ("tomorrow", parse("tomorrow").date())
])
def test_interpret_date(s, expect):
    v = Interpret.date(s)
    assert v == expect


@pytest.mark.parametrize("s, expect_min, expect_max", [
    ("rand(0, 10)", 0, 10),
    ("rand(5,50)", 5, 50),
    ("rand( -4, 8)", -4, 8),
    ("rand(11)", 11, 2 ** 32 - 1),
    ("rand()", 0, 2**32 - 1)
])
def test_interpret_ranint(s, expect_min, expect_max):
    for i in range(0, 100):
        v = Interpret.integer(s)
        assert v >= expect_min
        assert v <= expect_max


def test_interpret_ranbool():
    ntrue = 0
    nfalse = 0

    from metawards.utils import seed_ran_binomial, ran_bool

    # I've double-checked and this random number seed will
    # generate exactly 500 true and 500 false values
    rng = seed_ran_binomial(45748111)

    rng2 = seed_ran_binomial(45748111)

    for i in range(0, 1000):
        v = Interpret.boolean("rand()", rng=rng)

        expect = ran_bool(rng2)

        if v:
            assert expect
            ntrue += 1
        else:
            assert not expect
            nfalse += 1

    # choice of seed means 500 each
    assert ntrue == nfalse


@pytest.mark.parametrize("s, expect_min, expect_max", [
    ("rand(0, 10)", 0, 10),
    ("rand(5,50)", 5, 50),
    ("rand( -4, 8)", -4, 8),
    ("rand(11)", 11, 12),
    ("rand()", 0, 1),
    ("rand(3.2, 4.5)", 3.2, 4.5)
])
def test_interpret_rannum(s, expect_min, expect_max):
    for i in range(0, 100):
        v = Interpret.number(s)
        assert v >= expect_min
        assert v <= expect_max
