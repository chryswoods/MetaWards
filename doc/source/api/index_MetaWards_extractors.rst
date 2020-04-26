====================
MetaWards.extractors
====================

These are the extractor functions that are used during a model run
to extract data from the outbreak to process and write live to files.
The functions divide into three main types,
the most important of which are described below;

The functions that decide which output functions will be called
    * :meth:`~metawards.extractors.extract_default`

Functions that extract and output information from the outbreak
    * :meth:`~metawards.extractors.output_default`

Functions that set up the different `output_XXX` functions
    * :meth:`~metawards.extractors.setup_output_default`

All of the above functions (and the many others in metawards.extractors) are
described :doc:`in more detail here <./index_api_MetaWards_extractors>`;

.. toctree::
   :maxdepth: 1

   index_api_MetaWards_extractors
