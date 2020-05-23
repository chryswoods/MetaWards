========
Features
========

.. figure:: images/uq4map.jpg
    :width: 100%
    :figwidth: 35%
    :align: right
    :alt: Map of an outbreak modelled in England and Wales
    :figclass: align-right

    `Analysis of a simulation <https://uq4covid.github.io/vignettes/metawards_plot>`__
    run that used MetaWards to chart disease spread across England and Wales.

MetaWards is a geographic SIR-based epidemic modelling program. The
software models individuals who reside in a home ward (e.g. as in
an electoral ward in the UK) and who, optionally commute to a work ward.

The program is designed to enable researchers to model how an infection
may spread, and what impact different control measures or individual
behaviours may make.

To this end, MetaWards features;

* a flexible plugin architecture that makes it easy to implement new
  control measures. For example, the tutorial shows how this can be
  used to
  :doc:`model shielding <tutorial/part05/03_custom>`,
  :doc:`different lockdown scenarios <tutorial/part03/06_scan_lockdown>`
  and to
  :doc:`investigate necessary durations of quarantine or self-isolation <tutorial/part06/02_duration>`.

.. figure:: images/demographic_model.jpg
    :width: 100%
    :figwidth: 35%
    :align: right
    :alt: Output during modelling different self-isolation durations
    :figclass: align-right

    Multiple connected networks enable complex scenarios to be modelled

* multi-network demographic support. Multiple networks can be run as
  a single combined group, with custom plugins used to merge data
  between networks, and conditionally move individuals between
  different demographics. We've used to model shielding and self-isolation,
  with future plans to use this to model hospital admissions,
  impact of demography on transmission, regional variation in disease
  parameters and the impact of holidays.

.. figure:: images/tutorial_5_3_1_demographics.jpg
    :width: 100%
    :figwidth: 35%
    :align: right
    :alt: Results of a shielding experiment
    :figclass: align-right

    Built in metawards-plot tool for rapid visualisation of results,
    including across multiple networks

* flexible data output support - again handled using an array of in-built
  or user-supplied data extraction plugin functions. Output the data you
  need in the format you want to perform analysis.

* full reproducibility support baked in throughout. The code records
  enough data to make reproduction easy, with results designed to
  be the same given the same inputs, random number seed and number of threads.

* a :doc:`complete tutorial <tutorial/tutorial>` that takes you from beginning to
  learn how to run SIR simulations, to writing powerful plugins that let you
  model complex scenarios.

* support for scanning design files for optimisation or sensitivity analysis
  of nearly all input parameters, plus any user custom parameters used
  in the main code or any plugins. These scans can use as much compute
  you have available, parallelising individual runs over multiple cores,
  and scaling multiple runs up to full supercomputers (if you are lucky
  enough to have access to one)...

.. figure:: images/pandas_example.jpg
    :width: 100%
    :figwidth: 35%
    :align: right
    :alt: Analysing data in pandas
    :figclass: align-right

    Easily load compressed data files into pandas, R or Excel for analysis

* ...but - the individual code is optimised and can run happily on small
  laptops. Individual networks fit in approximately 80 MB of memory, and model
  runs can take 15-90 seconds to perform. This scales with the number of
  demographics that are added, but high performance and low memory consumption
  are design goals.

* :doc:`flexible input files <model_data>` that would enable modelling of any
  region or country to be undertaken (subject to good input data). Currently
  models of the UK and England and Wales have been created.

* a colourful, modern and informative console output, with full unicode
  support and progress indicators. All outputs are duplicated to
  text files to ensure that no data from a run is lost.

.. figure:: images/parallel_output.jpg
    :width: 100%
    :figwidth: 35%
    :align: right
    :alt: Running multiple jobs in parallel
    :figclass: align-right

    Perform multiple runs in parallel, with live summary updates as
    jobs finish

* both command-line and API interfaces. Feel free to run MetaWards as
  a standalone program, or to use the Python API to embed it as part
  of a larger framework. A modular, robust design has been used, so
  feel free to take and re-use the parts of MetaWards that are most
  of use to you.

Software design
---------------

MetaWards is a modern piece of software that has been engineered following
recognised best practice, e.g. using a modular design,
lots of documentation, copious run-time and unit tests, and following
a "tutorial-driven" development philosophy.

The software is mostly Python, with C used (via cython) to accelerate
key parts. This is parallelised using OpenMP, with multiple model runs
parallelised using multiprocessing, scoop or MPI.

We take testing very seriously, and have lots of unit, integration and
run-time tests. These are run as part of our CI/CD system deployed
via `GitHub Actions <https://github.com/metawards/MetaWards/actions>`__
The code has in-built developer
:doc:`support for debug logging and profiling <devsupport>`, with
:doc:`full API docs available <api/index>`
that we hope will help new developers get quickly up to speed.

We also take versioning and backwards compatibility seriously. We follow
the `semantic versioning <https://semver.org>`__  system for the main API,
which should give confidence
to anyone wanting to build on top of MetaWards. We also maintain
compatibility of inputs and outputs, with the strong aim that all tutorials
will be runnable, as-is, in future versions of the code.
