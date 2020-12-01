
from metawards import Population


def merge_test(population: Population, **kwargs):
    if not hasattr(population, "merge_test"):
        population.merge_test = "merge_test_value"

    assert population.merge_test == "merge_test_value"


def mix_test(**kwargs):
    return [merge_test]
