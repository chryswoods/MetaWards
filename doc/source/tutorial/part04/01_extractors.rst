=================
Custom extractors
=================

You have now learned how to use custom iterators to customise the
advancement of the outbreak during a model run.

In a similar way, ``metawards`` provides custom extractors that
enable you to customise the output that is produced and written
to a file (or files).

Hello extractors
----------------

You create an extractor in an almost identical manner as an iterator.
Start by creating a python file called ``hello.py`` and copy in the
below;

.. code-block:: python

  def extract_hello(**kwargs):
      print("Hello extract_hello")

      return []

The extractor is passed using the ``--extractor`` command-line argument.
Run ``metawards`` using;

.. code-block:: bash

   metawards --extractor hello

You should see output something similar to this;

::

    Loaded iterator from hello.py
    <function extract_hello at 0x10fe935f0>
    Building a custom extractor for <function extract_hello at 0x10fe935f0>
    Setup by seeding all wards
    Hello extract_hello
    S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

    0 0
    Hello extract_hello
    S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

    1 0
    Hello extract_hello
    S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

    2 0
    Hello extract_hello
    S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

    3 0
    Hello extract_hello
    S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

    4 0
    Hello extract_hello
    S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077
    Infection died ... Ending on day 5

extract_XXX and output_XXX
--------------------------

At the end of each model day, ``metawards`` calls the
:meth:`~metawards.utils.extract` function. This calls your ``extract_XXX``
function. The signature is very similar to the custom iterator functions,
namely it should take ``**kwargs``, and then return a list of functions
that :meth:`~metawards.utils.extract` will then call to output data
(what we term ``output_XXX`` functions).

At the moment, nothing is being written to the output directory. We
can change this by adding an ``output_XXX`` function. For example,
create a new python file called ``population.py`` and copy in
the below;

.. code-block:: python

    def output_population(population, output_dir, **kwargs):
        print("Hello output_population")

        # create an output file called 'population.dat'
        popfile = output_dir.open("population.dat")

        # write the population to this file
        popfile.write(f"{population.day} {population.date.isoformat()} "
                      f"{population.susceptibles} {population.latent} "
                      f"{population.total} {population.recovereds}\n")

    def extract_population(**kwargs):
        print("hello extract_population")

        return [output_population]

This defines two functions;

* ``extract_population``, which tells ``metawards`` to use your
  ``output_population`` function,

* and ``output_population`` that uses the passed
  :class:`population <metawards.Population>` and
  :class:`output_dir <metawards.OutputFiles>` objects to write
  the population of the different disease states to a file
  in the output directory called ``population.dat``.

Use this extractor using the command;

.. code-block:: bash

   metawards --extractor population

If you take a look in the ``output`` directory you should see that a file
called ``population.dat.bz2`` has been created. You can take a look at
this in R, Python pandas or excel. For example, we can load this in
pandas using;

.. code-block:: python

   >>> import pandas as pd
   >>> df = pd.read_csv("output/population.dat.bz2", sep=" ", header=None)
   >>> print(df)
         0           1         2  3  4  5
      0  0  2020-04-26  56082077  0  0  0
      1  1  2020-04-27  56082077  0  0  0
      2  2  2020-04-28  56082077  0  0  0
      3  3  2020-04-29  56082077  0  0  0
      4  4  2020-04-30  56082077  0  0  0

.. note::
   ``metawards`` will auto-compress all files written into the output
   directory. If you don't want this, then use the command-line argument
   ``--no-auto-bzip``.

Notice that there are no headers to the columns. We can add a header
by passing in the headers to the
:meth:`~metawards.OutputFiles.open` function, e.g. change ``population.py``
to read;

.. code-block:: python

    def output_population(population, output_dir, **kwargs):
        print("Hello output_population")

        # create an output file called 'population.dat'
        popfile = output_dir.open("population.dat",
                                  headers=["day", "date", "S", "E",
                                           "I", "R"])

        # write the population to this file
        popfile.write(f"{population.day} {population.date.isoformat()} "
                      f"{population.susceptibles} {population.latent} "
                      f"{population.total} {population.recovereds}\n")

    def extract_population(**kwargs):
        print("hello extract_population")

        return [output_population]

Run ``metawards`` again, and now if you load the ``population.dat.bz2``
file into pandas (or R or Excel) you will see something similar to;

.. code-block:: python

  >>> import pandas as pd
  >>> df = pd.read_csv("output/population.dat.bz2", sep=" ", index_col="day")
  >>> print(df)
               date         S  E  I  R
    day
    0    2020-04-26  56082077  0  0  0
    1    2020-04-27  56082077  0  0  0
    2    2020-04-28  56082077  0  0  0
    3    2020-04-29  56082077  0  0  0
    4    2020-04-30  56082077  0  0  0

.. note::
  Note how I have used ``index_col`` to set the ``day`` as the index
  in pandas

Occasional functions
--------------------

Just as with iterators, we can choose to only call the output function
on specific days. For example, to only output the population to the
file on even days, change ``population.py`` to read;

.. code-block:: python

    def output_population(population, output_dir, **kwargs):
        print("Hello output_population")

        # create an output file called 'population.dat'
        popfile = output_dir.open("population.dat",
                                headers=["day", "date", "S", "E",
                                        "I", "R"])

        # write the population to this file
        popfile.write(f"{population.day} {population.date.isoformat()} "
                    f"{population.susceptibles} {population.latent} "
                    f"{population.total} {population.recovereds}\n")


    def extract_population(population, **kwargs):
        print("hello extract_population")

        if population.day % 2 == 0:
            return [output_population]
        else:
            return []

Run ``metawards`` using this extractor and you should see that the
``population.dat.bz2`` file contains output only for days 0, 2, and 4.

.. note::
   The line ``population.day % 2 == 0`` takes the remainder division
   of ``population.day`` with 2. Any day that is divisible by 2 will
   return 0. You can output every ``N`` days using
   ``population.day % N == 0``.

.. note::
   You are also able to only print out on other conditions, e.g.
   when the **model run** reaches a certain date, or when the
   infected population grows above a certain size.
