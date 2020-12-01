
from metawards import Population


def go_test(population: Population, **kwargs):
    if not hasattr(population, "go_test"):
        population.go_test = "go_test_value"

    assert population.go_test == "go_test_value"


def move_test(**kwargs):
    return [go_test]
