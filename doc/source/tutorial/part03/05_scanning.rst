================
Custom variables
================

In the last example we got ``metawards`` to model a lockdown. However,
we put a lot of hard-coded parameters into ``iterate_lockdown`` function
we wrote. One of the main purposes of ``metawards`` is to enable us
to scan through multiple variables to see their affect on the
population trajectories.

User variables
--------------

``metawards`` supports the use of any custom user variables. For example,
create a new file called ``custom.inp`` and copy in the below;

::

    # first state
    user.scale[0] = 0.2
    user.flag[0]  = False

    # second state
    user.scale[1] = 0.5
    user.flag[1]  = True

    # third state
    user.scale[2] = 0.7
    user.flag[2]  = True

.. note::
  Comments start with a '#'. The file format is very flexible. You can
  use an '=' sign or a ':' or even nothing, e.g. "user.scale[1] 0.5".
  You can abbreviate "user.variable" to ".variable" too if you want.

This file is going to be used to define three states. The first (at index 0)
has a scale factor of 0.2, and a flag set to ``False``. The second has
a scale factor of 0.5 and a flag set to ``True``. The third has a
scale factor of 0.7 and a flag set also to ``True``.

We can pass this input file into ``metawards`` using the ``--user-variables``
(or ``-u``) parameter, e.g. try typing;

.. code-block:: bash

   metawards -d lurgy3 --user-variables custom.inp

In the output you should see a line that reads;

::

  Adjusting variables to (.scale[0]=0.2, .flag[0]=0.0, .scale[1]=0.5, .flag[1]=1.0, .scale[2]=0.7, .flag[2]=1.0)[repeat 1]

.. note::
  See how "user.variable" has been abbreviated to ".variable" in this output

This shows that ``metawards`` has read your custom parameters into the
program. They are stored as ``user_params`` in a
:class:`~metawards.Parameters` object that is stored in the
:class:`~metawards.Network` that holds the network of wards being modelled.

Reading user variables in custom iterators
------------------------------------------

You can access these parameters in an iterator or advance function using
``network.params.user_params[X]`` when ``X`` is the name of the parameter
you want. For example, ``network.params.user_params["scale[0]"] returns
``0.2``. For example, copy the below into a file called ``custom.py``;

.. code-block:: python

    def get_state(population):
        if population.day < 2:
            return 0
        elif population.day < 4:
            return 1
        else:
            return 2

    def advance_lockdown(network, population, **kwargs):
        params = network.params
        state = get_state(population)
        scale = params.user_params["scale"][state]
        print(f"Hello advance_lockdown - scale = {scale}")

    def advance_relaxed(network, population, **kwargs):
        params = network.params
        state = get_state(population)
        scale = params.user_params["scale"][state]
        print(f"Hello advance_relaxed - scale = {scale}")

    def iterate_custom(network, population, **kwargs):
        params = network.params
        state = get_state(population)
        flag = params.user_params["flag"][state]
        print(f"Hello iterate_custom - state = {state}, flag = {flag}")

        if flag:
            return [advance_lockdown]
        else:
            return [advance_relaxed]

This code defines four functions:

1. ``get_state`` - this returns the state that the population should be
   set to. In this case, the state is 0, 1 or 2 depending on the day
   of the outbreak.

2. ``iterate_custom`` - this gets the state using ``get_state``. It then
   looks up the ``flag`` custom parameter at index ``state``.
   If the flag is True, then it returns ``advance_lockdown``. Otherwise
   it returns ``advance_relaxed``.

3. ``advance_lockdown`` - this gets the state using ``get_state``. It then
   looks up the ``scale`` custom parameter at index ``state``.
   It prints this to the screen.

4. ``advance_relaxed`` - this does the same as ``advance_lockdown``, but
   prints a different message to the screen.

Use this iterator by running ``metawards`` via;

.. code-block:: bash

   metawards -d lurgy3 -u custom.inp --iterator custom

You should now see printed to the screen something very similar to the below;

::

    S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077
    Hello iterate_custom - state = 0, flag = 0.0
    Hello advance_relaxed - scale = 0.2

    0 0
    S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077
    Hello iterate_custom - state = 0, flag = 0.0
    Hello advance_relaxed - scale = 0.2

    1 0
    S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077
    Hello iterate_custom - state = 1, flag = 1.0
    Hello advance_lockdown - scale = 0.5

    2 0
    S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077
    Hello iterate_custom - state = 1, flag = 1.0
    Hello advance_lockdown - scale = 0.5

    3 0
    S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077
    Hello iterate_custom - state = 2, flag = 1.0
    Hello advance_lockdown - scale = 0.7

    4 0
    S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077
    Infection died ... Ending on day 5

Hopefully the change between state, functions called and values of the
scale factor printed makes sense and follows what you expected.

Scanning custom variables
-------------------------

You can also adjust your custom variables by scanning in the same way
that we adjusted in-built variables like **beta** and **progress**
in :doc:`an earlier part of this tutorial <../part02/02_adjustable>`.

In this case, we use the full (``user.variable``) or abbreviated
(``.variable``) names as titles in the ``metawards`` input file.

For example, create a new file called ``scan.csv`` and copy in the below;

::

    .scale[0]  .flag[0]
      0.1        False
      0.2        False
      0.3        False
      0.1         True
      0.2         True
      0.3         True

This tells ``metawards`` to perform six *model runs*, with ``user.scale[0]``
varied from 0.1-0.3, and ``user.flag[0]`` varied from "True" to "False".

Perform these model runs using;

.. code-block:: bash

   metawards -d lurgy3  -u custom.inp --iterator custom -i scan.csv

You should get output that is very similar to this;

::

    Completed job 1 of 6
    (.scale[0]=0.1, .flag[0]=0.0)[repeat 1]
    2020-04-26: DAY: 5 S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

    Completed job 2 of 6
    (.scale[0]=0.2, .flag[0]=0.0)[repeat 1]
    2020-04-26: DAY: 5 S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

    Completed job 3 of 6
    (.scale[0]=0.3, .flag[0]=0.0)[repeat 1]
    2020-04-26: DAY: 5 S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

    Completed job 4 of 6
    (.scale[0]=0.1, .flag[0]=1.0)[repeat 1]
    2020-04-26: DAY: 5 S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

    Completed job 5 of 6
    (.scale[0]=0.2, .flag[0]=1.0)[repeat 1]
    2020-04-26: DAY: 5 S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

    Completed job 6 of 6
    (.scale[0]=0.3, .flag[0]=1.0)[repeat 1]
    2020-04-26: DAY: 5 S: 56082077    E: 0    I: 0    R: 0    IW: 0   TOTAL POPULATION 56082077

.. note::
   Note that "True" and "False" are converted to "1.0" and "0.0". This
   is because all custom variables are stored internally in ``metawards``
   as floating point numbers.

A quick look in the ``output/results.csv.bz2`` file, e.g. using pandas,
shows that the fingerprint and columns for custom variables are
constructed identially to in-built variables, e.g.

.. code-block:: python

    >>> import pandas as pd
    >>> df = pd.read_csv("output/results.csv.bz2")
    >>> print(df)
       fingerprint  repeat  .scale[0]  .flag[0]  day        date         S  E  I  R  IW
    0          1_0       1        0.1       0.0    0  2020-04-21  56082077  0  0  0   0
    1          1_0       1        0.1       0.0    1  2020-04-22  56082077  0  0  0   0
    2          1_0       1        0.1       0.0    2  2020-04-23  56082077  0  0  0   0
    3          1_0       1        0.1       0.0    3  2020-04-24  56082077  0  0  0   0
    4          1_0       1        0.1       0.0    4  2020-04-25  56082077  0  0  0   0
    5          1_0       1        0.1       0.0    5  2020-04-26  56082077  0  0  0   0
    6          2_0       1        0.2       0.0    0  2020-04-21  56082077  0  0  0   0
    7          2_0       1        0.2       0.0    1  2020-04-22  56082077  0  0  0   0
    8          2_0       1        0.2       0.0    2  2020-04-23  56082077  0  0  0   0
    9          2_0       1        0.2       0.0    3  2020-04-24  56082077  0  0  0   0
    10         2_0       1        0.2       0.0    4  2020-04-25  56082077  0  0  0   0
    11         2_0       1        0.2       0.0    5  2020-04-26  56082077  0  0  0   0
    12         3_0       1        0.3       0.0    0  2020-04-21  56082077  0  0  0   0
    13         3_0       1        0.3       0.0    1  2020-04-22  56082077  0  0  0   0
    14         3_0       1        0.3       0.0    2  2020-04-23  56082077  0  0  0   0
    15         3_0       1        0.3       0.0    3  2020-04-24  56082077  0  0  0   0
    16         3_0       1        0.3       0.0    4  2020-04-25  56082077  0  0  0   0
    17         3_0       1        0.3       0.0    5  2020-04-26  56082077  0  0  0   0
    18       1_1.0       1        0.1       1.0    0  2020-04-21  56082077  0  0  0   0
    19       1_1.0       1        0.1       1.0    1  2020-04-22  56082077  0  0  0   0
    20       1_1.0       1        0.1       1.0    2  2020-04-23  56082077  0  0  0   0
    21       1_1.0       1        0.1       1.0    3  2020-04-24  56082077  0  0  0   0
    22       1_1.0       1        0.1       1.0    4  2020-04-25  56082077  0  0  0   0
    23       1_1.0       1        0.1       1.0    5  2020-04-26  56082077  0  0  0   0
    24       2_1.0       1        0.2       1.0    0  2020-04-21  56082077  0  0  0   0
    25       2_1.0       1        0.2       1.0    1  2020-04-22  56082077  0  0  0   0
    26       2_1.0       1        0.2       1.0    2  2020-04-23  56082077  0  0  0   0
    27       2_1.0       1        0.2       1.0    3  2020-04-24  56082077  0  0  0   0
    28       2_1.0       1        0.2       1.0    4  2020-04-25  56082077  0  0  0   0
    29       2_1.0       1        0.2       1.0    5  2020-04-26  56082077  0  0  0   0
    30       3_1.0       1        0.3       1.0    0  2020-04-21  56082077  0  0  0   0
    31       3_1.0       1        0.3       1.0    1  2020-04-22  56082077  0  0  0   0
    32       3_1.0       1        0.3       1.0    2  2020-04-23  56082077  0  0  0   0
    33       3_1.0       1        0.3       1.0    3  2020-04-24  56082077  0  0  0   0
    34       3_1.0       1        0.3       1.0    4  2020-04-25  56082077  0  0  0   0
    35       3_1.0       1        0.3       1.0    5  2020-04-26  56082077  0  0  0   0
