==============================
Multi-demographic sub-networks
==============================

So far every member of the population during a ``metawards`` *model run* has
been treated equally. There was no concept of different groups of individuals,
e.g. school children, hospital patients, holiday-makers etc. being
modelled any differently. The only distinction was between *workers*,
who made fixed movements (potentially between wards)
during the day, and random interactions within their home ward in
the evening, and *players*, who just made random interactions within
their home ward.

Understanding Network
---------------------

The :class:`~metawards.Network` class models this network of *workers* and
*players*. It holds a set of :class:`~metawards.Nodes` that represent each
electoral ward, and a set of :class:`~metawards.Links` that represent the
fixed motions between wards made by the "workers".

The :class:`~metawards.Node` class holds the number of *players* who
are susceptible to infection (S). This is held in the variable
:data:`metawards.Node.play_suscept`.

The :class:`~metawards.Link` class contains the number of *workers* who are
susceptible to infection (S) who travel regularly between their
"home" ward and their "work" ward. This is held in the
variable :data:`metawards.Link.suscept`.

During a *model run* these values will be reduced as individuals are
infected and then progressed through the different disease stages.

.. note::

  These variables are stored as double precision floating point numbers,
  despite representing integer values. This is because it
  is more efficient to use double precision numbers when they are used
  for calculations during a *model run*.

Understanding Networks
----------------------

To model multiple demographics, we need to create space for multiple different
sets of *workers* and *players*. This is achieved in ``metawards`` by
giving each demographic its own :class:`~metawards.Network`. All of these
demographic sub-networks are merged and managed via the
:class:`~metawards.Networks` class.

We create a :class:`~metawards.Networks` object by first specifying the way
we would like to distribute the population between different demographics.
We do this by writing a *demographics* file, which is a simple
`JSON-format <https://guide.couchdb.org/draft/json.html>`__
file. First, create a file called ``demographics.json`` and copy in the below;

::

    {
      "demographics" : ["red", "blue"],
      "work_ratios"  : [ 0.0,   1.0  ],
      "play_ratios"  : [ 0.5,   0.5  ]
    }

This file specifies that the population will be distributed between
two demographics, *red* and *blue*, named in the ``demographics``
field. You can have as many or as few demographics as you wish, and
can name them in any way you want.

The ``work_ratios`` lists the ratio (or percentage) of the *worker* population
that should belong to each demographic. For example, here all of the
*workers* are in the *blue* demographic, and none of the workers are
in the *red* demographic.

The ``play_ratios`` lists the ratio (or percentage) of the *player* population
that should belong to each demographic. For example, here 50% of the
*players* are in the *red* demographic, and 50% of the *players* are in the
*blue* demographic.

.. note::
  You can specify the work and play ratios using either numbers between
  0.0 and 1.0, or you can pass in strings that are interpreted using
  :func:`metawards.utils.safe_eval_float`, e.g. "50%", "1/4" or
  "(10+15)%". The only requirement is that the sum of ratios must
  equal 1.0 (or 100%), as every individual must be assigned to one
  of the demographics.

Now that you have created the ``demographics.json`` file, you can tell
``metawards`` to use it via the ``--demographics``, or ``-D``,
command line argument. Run ``metawards`` using;

.. code-block:: bash

   metawards -d lurgy2 -D demographics.json

In the output you should see lines such as;

::

    demographics = [
        Demographic(name='red', work_ratio=0.0, play_ratio=0.5, adjustment=None)
        Demographic(name='blue', work_ratio=1.0, play_ratio=0.5, adjustment=None)
    ]

    [and]

    Specialising network - population = 56082077
      red - population = 16806528
      blue - population = 39275549

These show that your demographics file was read correctly. In this case,
this has specialised the :class:`~metawards.Network` which modelled a
population of 56082077 individuals into a :class:`~metawards.Networks`
which has a *red* population of 16806528 and a *blue* population of
39275549.

.. warning::
  A fixed random number seed is used to assign left-over individuals
  to a random demographic. For example, 10 individuals cannot be divided
  equally between 3 demographics, so one randomly chosen demographic
  will have 4 individuals, while the other two will have 3. This
  division is performed by ``metawards`` in every single
  :class:`~metawards.Node` and every single :class:`~metawards.Link`,
  to ensure that every individual is allocated. This random seed is
  hard-coded to ``4751828``. Or, you can set it for a demographic
  by adding ``"random_seed" = number`` to the *demographics* file,
  e.g. ``"random_seed" = 10859403``.

Once the :class:`~metawards.Networks` had been specialised, the *model run*
was performed as before. Now, the output shows the S, E, I, R values
for both the overall total population, and also for the demographic
sub-network populations, e.g.

::

    S: 56082077  E: 0  I: 0  R: 0  IW: 0  POPULATION: 56082077
      red  S: 16806528  E: 0  I: 0  R: 0  IW: 0  POPULATION: 16806528
      blue  S: 39275549  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275549

    0 0
    S: 56082077  E: 0  I: 0  R: 0  IW: 0  POPULATION: 56082077
      red  S: 16806528  E: 0  I: 0  R: 0  IW: 0  POPULATION: 16806528
      blue  S: 39275549  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275549

    1 0
    S: 56082077  E: 0  I: 0  R: 0  IW: 0  POPULATION: 56082077
      red  S: 16806528  E: 0  I: 0  R: 0  IW: 0  POPULATION: 16806528
      blue  S: 39275549  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275549

    2 0
    S: 56082077  E: 0  I: 0  R: 0  IW: 0  POPULATION: 56082077
       red  S: 16806528  E: 0  I: 0  R: 0  IW: 0  POPULATION: 16806528
      blue  S: 39275549  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275549

    3 0
    S: 56082077  E: 0  I: 0  R: 0  IW: 0  POPULATION: 56082077
      red  S: 16806528  E: 0  I: 0  R: 0  IW: 0  POPULATION: 16806528
      blue  S: 39275549  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275549

    4 0
    Infection died ... Ending on day 5

In this case no infection was seeded, so nothing appears to happen.

We can seed an infection just as before, by using the ``--additional``
(or ``-a``) option, e.g. now run;

.. code-block:: bash

   metawards -d lurgy2 -D demographics.json -a ExtraSeedsLondon.dat

You should see output similar (but not identical) to;

::

    S: 56082077  E: 0  I: 0  R: 0  IW: 0  POPULATION: 56082077
       red  S: 16806526  E: 0  I: 0  R: 0  IW: 0  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275551

    0 0
    seeding demographic 0 play_infections[0][255] += 5
    S: 56082072  E: 5  I: 0  R: 0  IW: 0  POPULATION: 56082077
       red  S: 16806521  E: 5  I: 0  R: 0  IW: 0  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275551

    1 0
    S: 56082072  E: 0  I: 5  R: 0  IW: 0  POPULATION: 56082077
       red  S: 16806521  E: 0  I: 5  R: 0  IW: 0  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275551

    2 5
    S: 56082072  E: 0  I: 5  R: 0  IW: 0  POPULATION: 56082077
       red  S: 16806521  E: 0  I: 5  R: 0  IW: 0  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275551

    3 5
    S: 56082070  E: 0  I: 5  R: 2  IW: 1  POPULATION: 56082077
       red  S: 16806519  E: 0  I: 5  R: 2  IW: 1  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275551

    4 5
    S: 56082070  E: 2  I: 4  R: 1  IW: 0  POPULATION: 56082077
       red  S: 16806519  E: 2  I: 4  R: 1  IW: 0  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275551

    5 5
    S: 56082070  E: 0  I: 5  R: 2  IW: 0  POPULATION: 56082077
       red  S: 16806519  E: 0  I: 5  R: 2  IW: 0  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275551

    6 6
    S: 56082068  E: 0  I: 3  R: 6  IW: 1  POPULATION: 56082077
       red  S: 16806517  E: 0  I: 3  R: 6  IW: 1  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275551

    7 5
    S: 56082068  E: 2  I: 3  R: 4  IW: 0  POPULATION: 56082077
       red  S: 16806517  E: 2  I: 3  R: 4  IW: 0  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275551

    8 3
    S: 56082068  E: 0  I: 5  R: 4  IW: 0  POPULATION: 56082077
       red  S: 16806517  E: 0  I: 5  R: 4  IW: 0  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275551

    9 5
    S: 56082068  E: 0  I: 4  R: 5  IW: 0  POPULATION: 56082077
       red  S: 16806517  E: 0  I: 4  R: 5  IW: 0  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275551

    10 5
    S: 56082067  E: 0  I: 4  R: 6  IW: 1  POPULATION: 56082077
       red  S: 16806516  E: 0  I: 4  R: 6  IW: 1  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275551

    11 4
    S: 56082066  E: 1  I: 3  R: 7  IW: 1  POPULATION: 56082077
       red  S: 16806515  E: 1  I: 3  R: 7  IW: 1  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275551

    12 4
    S: 56082065  E: 1  I: 3  R: 8  IW: 1  POPULATION: 56082077
       red  S: 16806514  E: 1  I: 3  R: 8  IW: 1  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275551

    13 4
    S: 56082064  E: 1  I: 3  R: 9  IW: 1  POPULATION: 56082077
       red  S: 16806513  E: 1  I: 3  R: 9  IW: 1  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R: 0  IW: 0  POPULATION: 39275551

    14 4
    S: 56082063  E: 1  I: 3  R: 10  IW: 1  POPULATION: 56082077
       red  S: 16806512  E: 1  I: 3  R: 10  IW: 1  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R:  0  IW: 0  POPULATION: 39275551

    15 4
    S: 56082063  E: 1  I: 3  R: 10  IW: 0  POPULATION: 56082077
       red  S: 16806512  E: 1  I: 3  R: 10  IW: 0  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R:  0  IW: 0  POPULATION: 39275551

    16 4
    S: 56082063  E: 0  I: 4  R: 10  IW: 0  POPULATION: 56082077
       red  S: 16806512  E: 0  I: 4  R: 10  IW: 0  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R:  0  IW: 0  POPULATION: 39275551

    17 4
    S: 56082063  E: 0  I: 3  R: 11  IW: 0  POPULATION: 56082077
       red  S: 16806512  E: 0  I: 3  R: 11  IW: 0  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R:  0  IW: 0  POPULATION: 39275551

    18 4
    S: 56082062  E: 0  I: 2  R: 13  IW: 1  POPULATION: 56082077
       red  S: 16806511  E: 0  I: 2  R: 13  IW: 1  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R:  0  IW: 0  POPULATION: 39275551

    19 3
    S: 56082062  E: 1  I: 1  R: 13  IW: 0  POPULATION: 56082077
       red  S: 16806511  E: 1  I: 1  R: 13  IW: 0  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R:  0  IW: 0  POPULATION: 39275551

    20 2
    S: 56082062  E: 0  I: 1  R: 14  IW: 0  POPULATION: 56082077
       red  S: 16806511  E: 0  I: 1  R: 14  IW: 0  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R:  0  IW: 0  POPULATION: 39275551

    21 2
    S: 56082062  E: 0  I: 1  R: 14  IW: 0  POPULATION: 56082077
       red  S: 16806511  E: 0  I: 1  R: 14  IW: 0  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R:  0  IW: 0  POPULATION: 39275551

    22 1
    S: 56082062  E: 0  I: 1  R: 14  IW: 0  POPULATION: 56082077
       red  S: 16806511  E: 0  I: 1  R: 14  IW: 0  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R:  0  IW: 0  POPULATION: 39275551

    23 1
    S: 56082061  E: 0  I: 0  R: 16  IW: 1  POPULATION: 56082077
       red  S: 16806510  E: 0  I: 0  R: 16  IW: 1  POPULATION: 16806526
      blue  S: 39275551  E: 0  I: 0  R:  0  IW: 0  POPULATION: 39275551

    24 1
    Infection died ... Ending on day 25

By default, infections are seeded into the first demographic (in this case
*red*). This demographic are *players*, so only interact in their home
ward via random interactions. As such, the infection did not spread
beyond that home ward and so it died out quite quickly.

Seeding different demographics
------------------------------

You can seed different demographics by specifying the demographic in
the additional seeding file. Create a new seeding file called
``ExtraSeedsLondonBlue.dat`` and copy in the below;

::

  1  5  255  blue

The format of this file is a list of lines that say which wards should
be seeded. In this case, there is just one line containing four values.

* The first value (``1``) is the day of seeding, in this case on day 1.
* The second value  (``5``) is the number of individuals to infect, in
  this case 5.
* The third value (``255``) is the index of the ward to infect. You can find
  the index of the ward you want using the :class:`~metawards.WardInfos`
  object, e.g. via ``network.info.find("...")``.
* The fourth value (``blue``) is the name or index of the demographic
  you want to seed.

.. note::

  If you want, you could have specified the demographic in this file by
  its index (``1``) rather than by its name (``blue``). It is up to you.

The *blue* demographic contains all of the *workers*, so we would expect
to see a different outbreak. Perform a *model run* using;

.. code-block:: bash

  metawards -d lurgy2 -D demographics.json -a ExtraSeedsLondonBlue.dat

You should see a more sustained outbreak, ending in a similar way to this;

::

    135 3
    S: 19079821  E: 1  I: 1  R: 37002254  IW: 0  POPULATION: 56082077
       red  S: 16806610  E: 0  I: 0  R:        0  IW: 0  POPULATION: 16806610
      blue  S:  2273211  E: 1  I: 1  R: 37002254  IW: 0  POPULATION: 39275467

    136 1
    S: 19079821  E: 0  I: 2  R: 37002254  IW: 0  POPULATION: 56082077
       red  S: 16806610  E: 0  I: 0  R:        0  IW: 0  POPULATION: 16806610
      blue  S:  2273211  E: 0  I: 2  R: 37002254  IW: 0  POPULATION: 39275467

    137 2
    S: 19079821  E: 0  I: 2  R: 37002254  IW: 0  POPULATION: 56082077
       red  S: 16806610  E: 0  I: 0  R:        0  IW: 0  POPULATION: 16806610
      blue  S:  2273211  E: 0  I: 2  R: 37002254  IW: 0  POPULATION: 39275467

    138 2
    S: 19079821  E: 0  I: 2  R: 37002254  IW: 0  POPULATION: 56082077
       red  S: 16806610  E: 0  I: 0  R:        0  IW: 0  POPULATION: 16806610
      blue  S:  2273211  E: 0  I: 2  R: 37002254  IW: 0  POPULATION: 39275467

    139 2
    S: 19079821  E: 0  I: 0  R: 37002256  IW: 0  POPULATION: 56082077
       red  S: 16806610  E: 0  I: 0  R:        0  IW: 0  POPULATION: 16806610
      blue  S:  2273211  E: 0  I: 0  R: 37002256  IW: 0  POPULATION: 39275467

    140 2
    Infection died ... Ending on day 141

Because the *blue workers* could move between wards, they were able to carry
the infection across the country, meaning that most members of the *blue*
demographic were infected.
