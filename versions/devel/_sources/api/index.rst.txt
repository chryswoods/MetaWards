=============
Documentation
=============

The metawards program and associated Python module is composed
of six main units;

* The :doc:`metawards <index_MetaWards_app>` command line program, which is
  what most people would use to run metawards. This program comes with
  full help that is provided by typing ``metawards --help``.

* The :doc:`metawards <index_MetaWards>` top-level Python module, which is
  what you should use if you want to write new Python programs that
  integrate metawards functionality. These could include plugging
  metawards as a model into a higher-level statictical
  analysis package.

* The :doc:`metawards.iterators <index_MetaWards_iterators>` which contains
  all of the package-supplied iterators that are used to advance the
  model infection from day to day. These are used to customise exactly
  how an infection progresses, and how control measures are applied.
  This is described in the :doc:`tutorial <tutorial>`.

* The :doc:`metawards.extractors <index_MetaWards_extractors>` which contains
  all of the package-supplied extractors that are used to extract and
  output data gathered live during a model run and write them to files.
  These are used to customise exactly what information is gathered,
  how it is processed, and where it is written as the infection progresses.
  You can see how to use these to customise output in
  the :doc:`tutorial <tutorial>`.

* The :doc:`metawards.analysis <index_MetaWards_analysis>` contains
  analysis functions that can be used to process the results of a
  ``metawards`` run to generate insights and useful graphics.

* The :doc:`metawards.utils <index_MetaWards_utils>` utility Python module
  which contains lots of functions that are used by metawards to build and
  perform model runs. These functions are internal to metawards and are
  not designed to be used outside of this program.

.. toctree::
   :maxdepth: 1

  index_MetaWards_app
  index_MetaWards
  index_MetaWards_iterators
  index_MetaWards_extractors
  index_MetaWards_analysis
  index_MetaWards_utils
