=========
Changelog
=========

`0.11.1 <https://github.com/metawards/MetaWards/compare/0.11.0...0.11.1>`__ - May 10th 2020
--------------------------------------------------------------------------------------------

* Fixed CI/CD to produce working sdist and bdist packages

`0.11.0 <https://github.com/metawards/MetaWards/compare/0.10.0...0.11.0>`__ - May 10th 2020
--------------------------------------------------------------------------------------------

* Code now fully works and has been tested on Windows :-)
* Major update of the API to support a Networks of multiple Network objects
* This has been used to support modelling multiple demographics
* Added in movers and mixers to enable a user to customise how individuals
  are moved between demographics and how the FOIs of demographics are
  merged together (e.g. via an interaction matrix). This is demonstrated
  in part 5 of the tutorial which shows how this can be used to model
  shielding
* Allow compilation using compilers that don't support OpenMP - now compiles
  even on stock OS X.
* Added more extractors and can now output files that are needed for graphics
* Added a special random number seed to support debugging
* Moved random number files to a separate library which is now properly
  compiled and linked.
* Updated CI to CI/CD and now build the OS X, Windows and ManyLinux wheels
* Updated URLs to metawards.org
* Allow multiple multi-node jobs to run from a single directory (they now
  have their own hostfiles)
* Updated metawards-plot to render multi-demographic trajectories and
  to make better animations.
* General bug fixes and speed-ups :-)

`0.10.0 <https://github.com/metawards/MetaWards/compare/0.9.0...0.10.0>`__ - April 27th 2020
--------------------------------------------------------------------------------------------

* Created all of the extract framework to support customising the output
  and analysis during a run.
* Created a better Workspace class for holding accumulated data during extract
* Completed most of the extractor tutorial
* Added in WardInfo(s) to get metadata about wards, and to support searching
  for wards via their name, code, authority and region

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
