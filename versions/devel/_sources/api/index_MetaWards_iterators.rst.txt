===================
MetaWards.iterators
===================

These are the iterator functions that are used by the model to advance
the outbreak from day to day. The functions divide into three main types,
the most important of which are described below;

What should be applied on specific days of the outbreak
    * :meth:`~metawards.iterators.iterate_default`

Functions that advance the outbreak in different ways
    * :meth:`~metawards.iterators.advance_foi`
    * :meth:`~metawards.iterators.advance_additional`
    * :meth:`~metawards.iterators.advance_infprob`
    * :meth:`~metawards.iterators.advance_fixed`
    * :meth:`~metawards.iterators.advance_play`

Functions that set up the different `advance_XXX` functions
    * :meth:`~metawards.iterators.setup_additional_seeds`

All of the above functions (and the many others in metawards.iterators) are
described :doc:`in more detail here <./index_api_MetaWards_iterators>`;

.. toctree::
   :maxdepth: 1

   index_api_MetaWards_iterators
