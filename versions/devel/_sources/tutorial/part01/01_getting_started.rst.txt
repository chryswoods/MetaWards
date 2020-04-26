===============
Getting Started
===============

This tutorial assumes that you have installed ``metawards``. To check
that you have, type the following into your console;

.. code-block:: bash

   metawards --version

and then press return. You should see something similar to the below
printed to your screen.

.. command-output:: metawards --version

If you don't see this, or the output includes a warning about not being
about to find `MetaWardsData`, then please try
:doc:`installing MetaWards <../../install>` or
:doc:`installing and configuring MetaWardsData <../../model_data>` again.

.. warning::

  This tutorial is written for ``metawards`` version |MetaWardsVersion| or
  higher. If you are using an older version then please upgrade.

Introducing the Lurgy
---------------------

`The Lurgy <https://en.wiktionary.org/wiki/lurgy>`__ is a
**completely ficticious** disease that we will use throughout this
tutorial. We can run a simulation of an outbreak of the lurgy using
the ``--disease`` command line argument. Type the following;

.. code-block:: bash

   metawards --disease lurgy

Press return and you should see a lot of output printed. Near the end
of the output you will see these lines;

::

  S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

   0 0
  S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

   1 0
  S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

   2 0
  S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

   3 0
  S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

   4 0
  S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077
  Infection died ... Ending on day 5

.. note::
   Do not worry if you don't see exactly this output. You may be using
   a different version of ``metawards`` compared to the one used to write
   this tutorial. The main thing to look for is the line
   ``Infection died ... Ending on day 5``

The ``--disease`` option also has the shorthand ``-d``. You can get the same
output as above by typing;

.. code-block:: bash

   metawards -d lurgy

.. note::
   This time when you ran ``metawards`` it stopped to say that the output
   directory already exists, and if you want to remove it.

The ``metawards`` program takes care not to overwrite any of your output.
By default a lot of output files from this run have been written to a
directory called ``output`` (we will take a look at these files later).
``metawards`` will ask you if you want to remove any existing output.
Press ``y`` and hit return to do so. If you want to automatically
remove existing output then use the ``--force-overwrite-output`` option,
e.g.

.. code-block:: bash

   metawards -d lurgy --force-overwrite-output

You can also set the output directory using the ``--output`` or ``-o``
options, e.g.

.. code-block:: bash

   metawards -d lurgy -o output2

Seeding an outbreak
-------------------

The key output from ``metawards`` are the lines which read;

::

  S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

   0 0
  S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

   1 0
  S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

   2 0
  S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

   3 0
  S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

   4 0
  S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077
  Infection died ... Ending on day 5

These tell you how long the outbreak lasted (in this case, 5 days),
together with how many people were infected. These are the numbers next
to the codes;

* **S**: The number of the population who are *susceptible* to infection
* **E**: The number of the population who are *latent*, meaning they are
  infected, but not yet infectious.
* **I**: The number of the population who are *infected*, meaning they
  have symptoms and are infectious
* **R**: The number of the population who are removed from the outbreak,
  e.g. because they have recovered and are no longer susceptible to infection
* **IW**: The number electoral wards that contain at least one infected
  individual.

For more information about these values, please
`read <https://doi.org/10.1016/j.epidem.2009.11.002>`__
`the <https://doi.org/10.1073/pnas.1000416107>`__
`papers <https://doi.org/10.1101/2020.02.12.20022566>`__ detailed
in the :doc:`scientific background <../../index>`.

From this output it is clear that no-one has been infected by the lurgy.
This is because we haven't yet seeded any outbreaks. We can seed an
outbreak in a specific electoral ward by using an additional seeds file.
In this case, we will seed an infection of the lurgy in London using
the `ExtraSeedsLondon.dat <https://github.com/metawards/MetaWardsData/blob/master/extra_seeds/ExtraSeedsLondon.dat>`__
file that comes in ``MetaWardsData``. You specify the additional seeds
file to use via the ``--additional`` or ``-a`` options.

Try typing the below into your console and press return;

.. code-block:: bash

   metawards -d lurgy -a ExtraSeedsLondon.dat

Now the program will run for a long time (minutes), and you will see
an outbreak move through the population. The final lines of your output
may look something like this;

::

   217 9
   S: 11772514    E: 0    I: 7    R: 44309556    IW: 1   TOTAL POPULATION 56082077

   218 7
   S: 11772513    E: 1    I: 7    R: 44309556    IW: 1   TOTAL POPULATION 56082076

   219 8
   S: 11772512    E: 1    I: 5    R: 44309559    IW: 1   TOTAL POPULATION 56082076

   220 6
   S: 11772512    E: 1    I: 5    R: 44309559    IW: 0   TOTAL POPULATION 56082076

   221 6
   S: 11772512    E: 0    I: 3    R: 44309562    IW: 0   TOTAL POPULATION 56082077

   222 3
   S: 11772512    E: 0    I: 2    R: 44309563    IW: 0   TOTAL POPULATION 56082077

   223 2
   S: 11772512    E: 0    I: 2    R: 44309563    IW: 0   TOTAL POPULATION 56082077

   224 2
   S: 11772512    E: 0    I: 0    R: 44309565    IW: 0   TOTAL POPULATION 56082077
   Infection died ... Ending on day 225

.. note::

   Do not worry if your numbers are different. All will be explained :-)

Repeating a calculation
-----------------------

``metawards`` runs a stochastic simulation. This means that random numbers
are used in the decisions on how individuals in the model are infected,
and how quickly they progress through the infection. This means that
every ``metawards`` run is different.

Fortunately, ``metawards`` prints enough information in the output
to enable a job to be repeated. Look the for line the reads;

::

  ******************************************
  *** To repeat this job use the command ***
  ******************************************

  metawards --repeats 1 --seed 20460833 --additional ExtraSeedsLondon.dat --output output --UV 0.0 --disease lurgy --input-data 2011Data --start-date 2020-04-20 --start-day 0 --parameters march29 --repository /Users/chris/GitHub/MetaWardsData --population 57104043 --nthreads 4 --nprocs 1

This is the command line that you can use to repeat a job (note that
the command line you see will be different). We have been careful to
write ``metawards`` so that it gives the same output when you use
the same inputs, using the same version of ``metawards`` and same version
of data in ``MetaWardsData``, for the same random number seed and running
the calculation over the same number of threads. We consider it a bug
if ``metawards`` is not reproducible, and ask that you
`submit an issue <https://github.com/metawards/MetaWards/issues>`__ if
you find you cannot repeat a run.
