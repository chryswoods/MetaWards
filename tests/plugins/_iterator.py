
from metawards import Population


def advance_test(population: Population, **kwargs):
    if not hasattr(population, "advance_test"):
        population.advance_test = "advance_test_value"

    assert population.advance_test == "advance_test_value"


def iterate_test(**kwargs):
    return [advance_test]
