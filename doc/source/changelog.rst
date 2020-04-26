=========
Changelog
=========

`0.9.0 <https://github.com/metawards/MetaWards/compare/0.8.4...0.9.0>`__ - April 24th 2020
------------------------------------------------------------------------------------------

* Merged in latest changes from the C code. Now gives complete agreement,
  including via a custom iterator that repeats the lockdown model.
* Support x/y and lat/lon coordinates and distances. Now works properly
  with the 2011UK model data
* Added an example of a lockdown parameter set scan

`0.8.5 <https://github.com/metawards/MetaWards/compare/0.8.3...0.8.5>`__ - April 22nd 2020
------------------------------------------------------------------------------------------

* Small bugfixes to support the loading of the 2011UK model data
* Cleaned up the website and added the version combo box

`0.8.3 <https://github.com/metawards/MetaWards/compare/0.8.0...0.8.3>`__ - April 21st 2020
------------------------------------------------------------------------------------------

* Fixing CI/CD so that I can build and deploy on a new tag (hopefully 0.8.2)

`0.8.0 <https://github.com/metawards/MetaWards/compare/0.7.0...0.8.0>`__ - April 21st 2020
------------------------------------------------------------------------------------------

* Automated github actions for building a versioned website plus automating
  building the packages.
* Switched default for UV parameter to 0.0, as this should not normally be 1.0
* Added custom user variables both for scanning and to act as inputs that
  may be used by custom advance and iterate functions. Detailed tutorial
  now shows how these can be used to model a lockdown.
* Improved speed of custom iterators

`0.7.1 <https://github.com/metawards/MetaWards/compare/0.6.0...0.7.1>`__ - April 17th 2020
------------------------------------------------------------------------------------------

* Small bugfixes to support all of the examples in part 3 of the tutorial

`0.7.0 <https://github.com/metawards/MetaWards/compare/0.6.0...0.7.0>`__ - April 17th 2020
------------------------------------------------------------------------------------------

* Lots of progress with the project website, including a detailed tutorial
* Support fully customisable disease models, and can adjust any disease
  parameter using a more flexible input file format
* Can record the date in a model run, plus set the starting day and date
* Broken up the iterate function into :mod:`metawards.iterators`, and
  can now have the user create their own custom iterators. Tutorial on
  how to do this will appear soon.
* Broken up the extract_data function into :mod:`metawards.extractors`,
  and will soon enable a user to create their own. Tutorial on how
  to do this will appear soon.
* Added metawards-plot to create simple plots and animations. This is
  particularly useful when working through the tutorial.
* General code cleaning, documentation improvements and nice-to-haves
  that make the code easier to use.

`0.6.0 <https://github.com/metawards/MetaWards/compare/0.5.0...0.6.0>`__ - April 9th 2020
-----------------------------------------------------------------------------------------

* Wrote an initial draft of the complete project website
* Fixed packaging problems that prevented installation of older packages
  on some systems

`0.5.0 <https://github.com/metawards/MetaWards/compare/0.4.0...0.5.0>`__ - April 8th 2020
-----------------------------------------------------------------------------------------

* Support running multiple model runs in serial or in parallel
* Support aggregation and writing of model multiple model run outputs
  to the same directory, including to a single shared CSV data file.
* Support for parallel running via multiprocessing, mpi4py or scoop

`0.4.0 <https://github.com/metawards/MetaWards/compare/0.3.1...0.4.0>`__ - April 7th 2020
-----------------------------------------------------------------------------------------

* Parallelisation of individual model runs using OpenMP
* Parallel code scales to large numbers of cores and can complete individual
  runs in 10-15 seconds.

`0.3.1 <https://github.com/metawards/MetaWards/compare/0.3.0...0.3.1>`__ - April 5th 2020
-----------------------------------------------------------------------------------------

* Minor bug fixes in packaging and misplaced commits caused by move of
  repository

`0.3.0 <https://github.com/metawards/MetaWards/compare/v0.2.0...0.3.0>`__ - April 5th 2020
------------------------------------------------------------------------------------------

* Adding in a simple profiler to support optimisation of the code
* Replaced GSL random number generator with a more liberally licensed and
  easily bundled generator extracted from numpy.
* Switched code to the https://github.com/metawards organisation
* Optimised more using cython and raw C for file reading
* Added automatic versioning of packages and files using versioneer
* Cleaned up the repository and added status badges

`0.2.0 <https://github.com/metawards/MetaWards/compare/v0.1.0...v0.2.0>`__ - March 31st 2020
--------------------------------------------------------------------------------------------

* Cythonizing the bottleneck code to bring the python code up to a comparable
  performance as the original C code.
* Added in packaging information and general repository and file cleaning.

`0.1.0 <https://github.com/metawards/MetaWards/releases/tag/v0.1.0>`__ - March 29th 2020
----------------------------------------------------------------------------------------

* Fully working Python port of the original C code that completely reproduces
  the results of the C code when given the same random number seed. However,
  it is *significantly* slower! Python port has promise, so worth exploring
  different options for speeding the code up.

`Start of the Python port <https://github.com/metawards/MetaWards/commit/ef989ece450c40fe0ddb9f22e21693c90afb432e>`__ - March 25th 2020
---------------------------------------------------------------------------------------------------------------------------------------

* Imported code from https://github.com/ldanon/metawards and began thinking
  about what the code was and trying to understand it. Decided to write
  a port as I find that if I can translate something, then I can
  understand it.
