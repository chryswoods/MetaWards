===================
Multiple model runs
===================

In the last page you successfully performed a single run modelling
an outbreak of the lurgy that started in London. This run
(which we call a *model run*) is stochastic, meaning that the results
will be slightly different every time it is performed.

To gain confidence in any predictions, we need to perform a *model run*
multiple times, and average over the results.

Performing multiple model runs
------------------------------

``metawards`` has the command line option ``--repeats`` (or ``-r``) to
set the number of times a ``model run`` should be repeated. For example,
run the below command to repeat the *model run* four times;

.. code-block:: bash

  metawards -d lurgy -a ExtraSeedsLondon.dat --repeats 4

``metawards`` will automatically use as many of the cores on your computer
as it can to parallelise the jobs. On my computer, the output shows;

::

  Performing 4 runs of each set of parameters

  Number of threads to use for each model run is 1
  Number of processes used to parallelise model runs is 4
  Parallelisation will be achieved using multiprocessing

I have four processor cores on my laptop, so I see the four repeats run
in parallel using four processes, with each *model run* performed
using 1 thread. You will see a different distribution of threads
and processes if you have a different number of cores on your computer.
You can set the number of processes that ``metawards`` should use via
the ``--nprocs`` command line option. You can set the number of threads
that ``metawards`` should use via the ``--nthreads`` command line option.

This calculation may take some time (2-3 minutes). This time, instead
of seeing a summary of the outbreak, ``metawards`` will show a summary
of the different *model run* jobs. Something similar to this should
be printed;

::

  Running 4 jobs using 4 process(es)

  Running jobs in parallel using a multiprocessing pool...

  Completed job 1 of 4
  (NO_CHANGE)[repeat 1]
  2020-12-19: DAY: 243 S: 11776504    E: 0    I: 0    R: 44305573    IW: 1   TOTAL POPULATION 56082077

  Completed job 2 of 4
  (NO_CHANGE)[repeat 2]
  2020-12-16: DAY: 240 S: 11787147    E: 0    I: 0    R: 44294930    IW: 0   TOTAL POPULATION 56082077

  Completed job 3 of 4
  (NO_CHANGE)[repeat 3]
  2020-11-25: DAY: 219 S: 11789948    E: 0    I: 0    R: 44292129    IW: 0   TOTAL POPULATION 56082077

  Completed job 4 of 4
  (NO_CHANGE)[repeat 4]
  2020-12-04: DAY: 228 S: 11782418    E: 0    I: 0    R: 44299659    IW: 1   TOTAL POPULATION 56082077

  Writing a summary of all results into the
  csv file /Users/chris/GitHub/tutorial/output/results.csv.bz2.

In this case, all four outbreaks completed within 219-243 days, while the
number of the population who progressed to the '**R**' state were all
around 44.3 million.

The results.csv.bz2 file
------------------------

The day-by-day progress of each the outbreak for each *model run* is
recorded in the output file ``results.csv.bz2``. This is a comma-separated
file that has been compressed using `bzip2 <https://en.wikipedia.org/wiki/Bzip2>`__.

You can read this file easily using
`Python Pandas <https://pandas.pydata.org>`__  or with
`R <https://www.r-project.org>`__. You can even import this into Excel
(although you may need to uncompress this file first using ``bunzip2``).

For example, if you have Pandas installed, then you can read this
file via an `ipython <https://ipython.org>`__ or
`Jupyter notebook <https://jupyter.org>`__ session via;

.. code-block:: python

  >>> import pandas as pd
  >>> df = pd.read_csv("output/results.csv.bz2")
  >>> df
      fingerprint  repeat  day        date         S  E  I         R  IW
  0     NO_CHANGE       1    0  2020-04-20  56082077  0  0         0   0
  1     NO_CHANGE       1    1  2020-04-21  56082077  0  0         0   0
  2     NO_CHANGE       1    2  2020-04-22  56082072  5  0         0   0
  3     NO_CHANGE       1    3  2020-04-23  56082072  0  5         0   0
  4     NO_CHANGE       1    4  2020-04-24  56082068  0  5         4   4
  ..          ...     ...  ...         ...       ... .. ..       ...  ..
  929   NO_CHANGE       4  224  2020-11-30  11782419  0  4  44299654   0
  930   NO_CHANGE       4  225  2020-12-01  11782419  0  3  44299655   0
  931   NO_CHANGE       4  226  2020-12-02  11782419  0  1  44299657   0
  932   NO_CHANGE       4  227  2020-12-03  11782419  0  1  44299657   0
  933   NO_CHANGE       4  228  2020-12-04  11782418  0  0  44299659   1

  [934 rows x 9 columns]

Each repeat is given its own number, which is in the ``repeat`` column.
The day of the outbreak is given in the ``day`` column. This counts up
from *day zero* when the outbreak started, to the last day when the
outbreak was over. You can control the start day of the outbreak using
the ``--start-day`` command line option.

The ``date`` column contains the date of each day in the outbreak. By
default, ``metawards`` assumes that *day zero* is today. You can set the
date of *day zero* using the ``--start-date`` command line option, e.g.
``--start-date tomorrow`` would start tomorrow, while
``--start-date Jan 1`` would start on January 1st this year.

The values of **S**, **E**, **I**, **R** and **IW** for each repeat for
each day are then given in their correspondingly named columns.

The *fingerprint* column not used for this calculation - we will see what it is
later.
