======================
Using a Custom Network
======================

You can run a simulation using a custom network by passing filename of
the JSON file that contains the network to ``metawards`` via the
``--model`` or ``-m`` parameter.

For example, to use the ``custom_network.json.bz2`` file from the last section,
together with the ``lurgy4.json`` disease model from previous chapters,
and seed the outbreak with 5 infections in London on day 1
you would run;

.. code-block:: bash

   metawards -d lurgy4 -m custom_network.json.bz2 -a "1 5 London"

You should see that the model runs very quickly, producing output similar
to;

::

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Loading additional seeds from the command line
    ┏━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
    ┃ Day ┃ Demographic ┃                                   Ward                                    ┃   Number   ┃
    ┃     ┃             ┃                                                                           ┃   seeded   ┃
    ┡━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
    │  1  │    None     │ 2 : WardInfo(name='London', alternate_names=, code='', alternate_codes=,  │     5      │
    │     │             │        authority='', authority_code='', region='', region_code='')        │            │
    └─────┴─────────────┴───────────────────────────────────────────────────────────────────────────┴────────────┘
    seeding play_infections[0][2] += 5
    S: 20345  E: 5  I: 0  R: 0  IW: 0  POPULATION: 20350
    Number of infections: 5

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 2 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 20345  E: 0  I: 5  R: 0  IW: 0  POPULATION: 20350
    Number of infections: 5

    ...
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 129 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 2895  E: 0  I: 1  R: 17454  IW: 0  POPULATION: 20350
    Number of infections: 1

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 130 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 2895  E: 0  I: 1  R: 17454  IW: 0  POPULATION: 20350
    Number of infections: 1

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 131 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 2895  E: 0  I: 1  R: 17454  IW: 0  POPULATION: 20350
    Number of infections: 1

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Day 132 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    S: 2895  E: 0  I: 0  R: 17455  IW: 0  POPULATION: 20350
    Number of infections: 0
    Ending on day 132
