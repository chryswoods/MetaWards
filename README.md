# MetaWards

[![Build status](https://github.com/metawards/MetaWards/workflows/Build/badge.svg)](https://github.com/metawards/MetaWards/actions?query=workflow%3ABuild)
[![PyPI version](https://badge.fury.io/py/metawards.svg)](https://pypi.python.org/pypi/metawards)

This is a Python port of the [MetaWards](https://github.com/ldanon/MetaWards)
package originally written by Leon Danon. The port is kept in sync with
the original C code, with checks in place to ensure that the two codes
give identical results. This improves the robustness of both codes, as
it minimises the footprint to bugs that can evade both C and Python.

The aim of this port is to make it easier for others to contribute to the
program, to improve robustness by adding in unit and integration test,
and to also open up scope for further optimisation and parallelisation.

The package makes heavy use of [cython](https://cython.org) which is used
with [OpenMP](https://openmp.org) to compile bottleneck parts of the
code to parallelised C. This enables this Python port
to run at approximately the same speed as the original C program on one core,
and to run several times faster across multiple cores.

The program compiles on any system that has a working C compiler that
supports OpenMP, and a working Python >= 3.7. This include X86-64 and
ARM64 servers.

The software supports running over a cluster using MPI
(via [mpi4py](https://mpi4py.readthedocs.io/en/stable/)) or via
simple networking (via [scoop](http://scoop.readthedocs.io)).

Full instructions on how to use the program, plus example job submission
scripts can be found on the [project website](https://metawards.github.io).

## Data

The data and input parameters needed to use this package are stored in
the [MetaWardsData](https://github.com/metawards/MetaWardsData)
repository. Please make sure that you clone this repository to your
computer and supply the full path to that repository to the program
when it runs. There are three ways to do this;

1. Set the `METAWARDSDATA` environment variable to point to this directory,
   e.g. `export METAWARDSDATA=$HOME/GitHub/MetaWards`

2. Pass the `repository` variable to the input data classes
   [Disease](https://github.com/metawards/MetaWards/blob/devel/src/metawards/_disease.py), [InputFiles](https://github.com/metawards/MetaWards/blob/devel/src/metawards/_inputfiles.py) and [Parameters](https://github.com/metawards/MetaWards/blob/devel/src/metawards/_parameters.py)

3. Or simply make sure you clone into the directory `$HOME/GitHub/MetaWardsData`
   as this is the default path.

## References

These are the references behind the
[original C code](https://github.com/ldanon/MetaWards) are;

- _"Individual identity and movement networks for disease metapopulations"_
Matt J. Keeling, Leon Danon, Matthew C. Vernon, Thomas A. House
Proceedings of the National Academy of Sciences May 2010, 107 (19) 8866-8870; DOI: [10.1073/pnas.1000416107](https://doi.org/10.1073/pnas.1000416107)

- _"A spatial model of CoVID-19 transmission in England and Wales: early spread and peak timing"_
Leon Danon, Ellen Brooks-Pollock, Mick Bailey, Matt J Keeling
medRxiv 2020.02.12.20022566; doi: [10.1101/2020.02.12.20022566](https://doi.org/10.1101/2020.02.12.20022566)

## Dependencies

The code requires Python 3.7 or above, and requires no other dependencies
to install. For development you will need [cython](https://cython.org)
to build the code, plus [pytest](https://docs.pytest.org/en/latest/)
for running the tests.

## Installation

[Full installation instructions are here](https://metawards.github.io/MetaWards/install.html).

As you are here, I guess you want to install the latest code from GitHub ;-)

To do that, type;

```
git clone https://github.com/metawards/MetaWards
cd MetaWards
pip install -r requirements-dev.txt
CYTHONIZE=1 python setup.py install
```

(assuming that `python` is version 3.7)

You can run tests using pytest, e.g.

```
METAWARDSDATA="/path/to/MetaWardsData" pytest tests
```

You can generate the docs using

```
cd docs
make
```

## Running

[Full usage instructions are here](https://metawards.github.io/MetaWards/usage.html)

You can either load and use the Python classes directly, or you can
run the `metawards` front-end command line program that is automatically installed.

```
metawards --help
```

will print out all of the help for the program. For example;

```
metawards --input tests/data/ncovparams.csv --seed 15324 --nsteps 30 --nthreads 1
```

This will duplicate the run of the MetaWards C program that is bundled
in this repository that was run using;

```
./original/metawards 15324 tests/data/ncovparams.csv 0 1.0
```

The original C code, command line and expected output are in the
[original](https://github.com/metawards/MetaWards/tree/devel/original)
directory that is bundled in this repo.

### Running an ensemble

This program supports parallel running of an ensemble of jobs using
[multiprocessing](https://docs.python.org/3.7/library/multiprocessing.html)
for single-node jobs, and [mpi4py](https://mpi4py.readthedocs.io/en/stable/)
or [scoop](http://scoop.readthedocs.io) for multi-node cluster jobs.

[Full instructions for running on a cluster are here](https://metawards.github.io/MetaWards/cluster_usage.html)

### Next stages...

The next stages of the program includes finishing up the custom extractor
code, improving some of the analysis, providing more integrators,
optimising the random number generator and finishing up the tutorial.

In addition, we plan to integrate the software into the Bayesian / MCMC
package [PyMC3](https://docs.pymc.io).
