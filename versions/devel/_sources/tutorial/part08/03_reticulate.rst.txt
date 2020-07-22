======================
Creating Networks in R
======================

While ``metawards`` is a Python module, you can use the :mod:`metawards`
module directly in R.

This is because the `reticulate project <https://rstudio.github.io/reticulate/>`__
lets you embed and use Python directly in your R scripts.

Installing reticulate
---------------------

You can install reticulate by starting R and typing;

.. code-block:: R

    > install.packages("reticulate")

Next, you need to set the path to the ``python`` executable for which
``metawards`` has been installed. For me, this is
``/Users/chris/miniconda3/bin/python``. Your path will be different.
To set this, use the ``use_python`` function in R, e.g.

.. code-block:: R

   > library(reticulate)
   > use_python("/Users/chris/miniconda3/bin/python", required = TRUE)

(remembering to use the path that is appropriate for your computer)

.. note::

   We have provided the ``metawards-reticulate`` command. Run this from
   the console/terminal to get the list of commmands you need to type into
   R to import reticulate, set the Python executable and import the
   :mod:`metawards` module.

Using metawards in R
--------------------

Next, you can import the :mod:`metawards` module by typing;

.. code-block:: R

   > metawards <- import("metawards")

This loads all of the :mod:`metawards` Python objects into the
``metawards`` namespace in R. You can then call those objects directly
as you would in Python.

For example, we can create the same custom network containing Bristol
and London in R as we did in Python via;

.. code-block:: R

   > wards <- metawards$Wards()
   > bristol <- metawards$Ward(name="Bristol")
   > bristol$add_workers(500, destination=bristol)
   > bristol$set_num_players(750)
   > print(bristol)
   Ward( id=1, name=Bristol, num_workers=500, num_players=750 )
   > london <- metawards$Ward(name="London")
   > london$add_workers(8500, destination=london)
   > london$set_num_players(10000)
   > print(london)
   Ward( id=2, name=London, num_workers=8500, num_players=10000 )
   > bristol$add_workers(500, destination=london)
   > london$add_workers(100, destination=bristol)
   > wards$add(bristol)
   > wards$add(london)
   > print(wards)
   [ Ward( id=1, name=Bristol, num_workers=1000, num_players=750 ), Ward( id=2, name=London, num_workers=8600, num_players=10000 ) ]
   > wards$to_json("custom_network.json", indent=2)
   [1] "/path/to/custom_network.json.bz2"

This should result in a (compressed) file called ``custom_network.json.bz2``,
which should have identical contents as if you have run these commands
in Python, e.g.

::

  [
    {
      "id": 1,
      "info": {
        "name": "Bristol"
      },
      "num_workers": 1000,
      "num_players": 750,
      "workers": {
        "destination": [
          1,
          2
        ],
        "population": [
          500,
          500
        ]
      }
    },
    {
      "id": 2,
      "info": {
        "name": "London"
      },
      "num_workers": 8600,
      "num_players": 10000,
      "workers": {
        "destination": [
          1,
          2
        ],
        "population": [
          100,
          8500
        ]
      }
    }
  ]

Going further
-------------

This was a simple example. However, I hope this is enough to show you how
you can begin to use the Python :mod:`metawards` module within R using
`reticulate <https://rstudio.github.io/reticulate/>`__. More details about
reticulate, more advanced ways of calling Python, plus how to set up
code completion and inline help are also available at the
`reticulate project webpage <https://rstudio.github.io/reticulate/>`__.
