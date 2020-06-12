
import os
import pytest

from metawards import Parameters, Network, Population, \
    OutputFiles, Demographics, Disease, VariableSets, VariableSet

from metawards.mixers import mix_evenly

script_dir = os.path.dirname(__file__)

demographics_json = os.path.join(script_dir, "data",
                                 "spreader_demographics.json")

home_json = os.path.join(script_dir, "data", "lurgy_home.json")
super_json = os.path.join(script_dir, "data", "lurgy_super.json")


@pytest.mark.slow
def test_pathway():
    demographics = Demographics.load(demographics_json)
    assert len(demographics) == 2

    disease_home = Disease.load(filename=home_json)
    disease_super = Disease.load(filename=super_json)

    assert demographics[1].disease is None
    assert demographics[0].disease == disease_super

    params = Parameters.load()
    params.set_disease(disease_home)
    params.set_input_files("single")
    params.add_seeds("ExtraSeedsOne.dat")

    network = Network.build(params)

    print(network.params.disease_params)
    print(disease_home)

    assert network.params.disease_params == disease_home

    network = network.specialise(demographics)

    print(network.params.disease_params)
    print(disease_home)

    assert network.params.disease_params == disease_home

    print(network.subnets[1].params.disease_params)
    print(disease_home)

    assert network.subnets[1].params.disease_params == disease_home

    print(network.subnets[0].params.disease_params)
    print(disease_super)

    assert network.subnets[0].params.disease_params == disease_super

    infections = network.initialise_infections()

    assert infections.N_INF_CLASSES == disease_home.N_INF_CLASSES()

    assert \
        infections.subinfs[1].N_INF_CLASSES == disease_home.N_INF_CLASSES()

    assert \
        infections.subinfs[0].N_INF_CLASSES == disease_super.N_INF_CLASSES()

    assert disease_super.N_INF_CLASSES() != disease_home.N_INF_CLASSES()

    outdir = os.path.join(script_dir, "test_pathway")

    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        results = network.copy().run(population=Population(),
                                     output_dir=output_dir,
                                     mixer=mix_evenly,
                                     nthreads=1,
                                     seed=36538943)

    # using one thread, but if use 2 then have a system crash after
    # any other test that uses the big network. This is because we
    # have intialised some global data that assumes a large network,
    # which then fails for the small network

    OutputFiles.remove(outdir, prompt=None)

    print(results[-1])
    print(results[-1].initial)

    expected = Population(susceptibles=519,
                          latent=0,
                          total=0,
                          recovereds=481,
                          n_inf_wards=0,
                          day=90)

    print(expected)

    assert results[-1].has_equal_SEIR(expected)
    assert results[-1].day == expected.day

    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        results = network.copy().run(population=Population(),
                                     output_dir=output_dir,
                                     mixer=mix_evenly,
                                     nthreads=1,
                                     seed=36538943)

    OutputFiles.remove(outdir, prompt=None)

    print(results[-1])
    print(results[-1].initial)

    print(expected)

    assert results[-1].has_equal_SEIR(expected)
    assert results[-1].day == expected.day

    variables = VariableSet()

    print("\nUpdate with null variables")
    oldparams = network.params
    params = network.params.set_variables(variables)
    network.update(params)

    assert oldparams == network.params

    print(network.params.disease_params)
    print(disease_home)

    assert network.params.disease_params == disease_home

    print(network.subnets[1].params.disease_params)
    print(disease_home)

    assert network.subnets[1].params.disease_params == disease_home

    print(network.subnets[0].params.disease_params)
    print(disease_super)

    assert network.subnets[0].params.disease_params == disease_super

    infections = network.initialise_infections()

    assert infections.N_INF_CLASSES == disease_home.N_INF_CLASSES()

    assert \
        infections.subinfs[1].N_INF_CLASSES == disease_home.N_INF_CLASSES()

    assert \
        infections.subinfs[0].N_INF_CLASSES == disease_super.N_INF_CLASSES()

    assert disease_super.N_INF_CLASSES() != disease_home.N_INF_CLASSES()

    outdir = os.path.join(script_dir, "test_pathway")

    with OutputFiles(outdir, force_empty=True, prompt=None) as output_dir:
        results = network.copy().run(population=Population(),
                                     output_dir=output_dir,
                                     mixer=mix_evenly,
                                     nthreads=1,
                                     seed=36538943)

    OutputFiles.remove(outdir, prompt=None)

    print(results[-1])
    print(expected)

    assert results[-1].has_equal_SEIR(expected)
    assert results[-1].day == expected.day


def test_variable_pathway():
    demographics_json = os.path.join(script_dir, "data", "red_one_blue.json")
    variables_csv = os.path.join(script_dir, "data", "demographic_scan.csv")

    demographics = Demographics.load(demographics_json)
    variables = VariableSets.read(variables_csv)

    print(variables[0].fingerprint(include_index=True))

    params = Parameters.load()
    params.set_disease("lurgy")
    params.set_input_files("single")

    network = Network.build(params)
    network = network.specialise(demographics)

    params = network.params.set_variables(variables[0])

    assert params.disease_params.beta == [0.0, 0.0, 0.1, 0.2, 0.0]
    assert params["overall"].disease_params.beta == \
        [0.0, 0.0, 0.1, 0.2, 0.0]
    assert params["red one"].disease_params.beta == \
        [0.0, 0.0, 0.1, 0.5, 0.27]
    print(params["blue"].disease_params.beta)
    assert params["blue"].disease_params.beta == \
        [0.0, 0.0, 0.1, 0.2, 0.25, 0.0]

    network.update(params)

    d = network.params.disease_params
    print(d.beta)
    assert d.beta == [0.0, 0.0, 0.1, 0.2, 0.0]

    d = network.subnets[0].params.disease_params
    print(d.beta)
    assert d.beta == [0.0, 0.0, 0.1, 0.5, 0.27]

    d = network.subnets[1].params.disease_params
    print(d.beta)
    assert d.beta == [0.0, 0.0, 0.1, 0.2, 0.25, 0.0]


if __name__ == "__main__":
    test_variable_pathway()
    test_pathway()
