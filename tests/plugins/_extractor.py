
from metawards import Population


def output_test(population: Population, **kwargs):
    if not hasattr(population, "output_test"):
        population.output_test = "output_test_value"

    assert population.output_test == "output_test_value"


def extract_test(**kwargs):
    return [output_test]
