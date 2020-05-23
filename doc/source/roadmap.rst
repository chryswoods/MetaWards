=======
Roadmap
=======

The planned development roadmap for ``metawards`` is below. These features
are planned so that we can support urgent modelling of specific
scenarios. This roadmap is subject to change, and is given here to
give insight into what the developers are thinking, and where
they intend the code to go.

Different demographics using different parameters
-------------------------------------------------

This is planned for MetaWards 1.1. Currently each demographic uses the
same disease parameters, though there is no technical reason why this
has to be the case. We'd like to have different disease parameters for
different demographics, also with different numbers of disease stages.
This will enable modelling of;

* different disease progress and effect on different societal demographics,
  e.g. modelling a disease that effects different genders or ages
  disproportionaly

* different numbers and tags for disease stages for different demographics,
  so that individuals can be conditionally moved along different
  pathways. This would enable subsets of the population to be modelled
  as going to hospital, with different path ways within hospital modelled.

Different demographics using different networks
-----------------------------------------------

This is planned for MetaWards 1.2.
Currently each demographic is using the same network topology. There is
no technical reason why this should be the case, and a small amount of
work is needed to enable different demographics to use different
networks.

This will enable modelling of;

* holidays - we can move individuals to separate networks to represent
  holiday destinations, and then investigate what happens when they return

* age-related behaviour - we can use different networks for different
  societal demographics, so to better represent the behaviours of
  different groups in society


Different nodes using different parameters
------------------------------------------

This is planned for MetaWards 1.3. Currently disease and control parameters
affect all wards equally. Custom iterators can be written now that change
those parameters on a ward-by-ward or regional basis, but this is clumsy.
We would like to implement per-ward, and per-demographic/per-ward disease,
control and user parameters.

This will enable modelling of;

* regional and local differences in, e.g. beta depending on levels of
  adherence to lockdown or availability of suitable accommodation

* regional differences in control measures, and modelling local differences
  in enacting and releasing controls
