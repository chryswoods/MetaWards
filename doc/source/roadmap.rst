=======
Roadmap
=======

The planned development roadmap for ``metawards`` is below. These features
are planned so that we can support urgent modelling of specific
scenarios. This roadmap is subject to change, and is given here to
give insight into what the developers are thinking, and where
they intend the code to go.

More details about individual feature branches, which contain the new
features being actively worked on, is available on the
`GitHub issues <https://github.com/metawards/MetaWards/issues?q=is%3Aissue+is%3Aopen+label%3Afeature-branch>`_
page.

Moving individuals between different networks
---------------------------------------------

This is planned for MetaWards 1.4. Currently the move functions move
individuals between demographics but keeping the same location in
the network. There is no technical reason why this should be the case.
We'd like to write a move function that can move individuals to
different locations in a network, and to also remember the move so
that it can be reverted after a period of time, or when a condition
is reached.

This will enable modelling of;

* holidays - we can move individuals to separate networks to represent
  holiday destinations, and then investigate what happens when they return

* returning from hospital, or moving between hospitals and care homes -
  we can move an individual from their home ward to a separate ward
  to represent a regional hospital, or to a regional care home.

This work will take place in the
`feature_holidays <https://github.com/metawards/MetaWards/issues/135>`_
feature branch.

Different nodes using different parameters
------------------------------------------

This is planned for MetaWards 1.4. Currently disease and control parameters
affect all wards equally. Custom iterators can be written now that change
those parameters on a ward-by-ward or regional basis, but this is clumsy.
We would like to implement per-ward, and per-demographic/per-ward disease,
control and user parameters.

This will enable modelling of;

* regional and local differences in, e.g. beta depending on levels of
  adherence to lockdown or availability of suitable accommodation

* regional differences in control measures, and modelling local differences
  in enacting and releasing controls
