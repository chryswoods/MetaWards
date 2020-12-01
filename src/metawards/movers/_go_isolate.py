
from typing import Union as _Union
from typing import List as _List

from .._network import Network
from .._networks import Networks

__all__ = ["go_isolate"]

_str_or_int = _Union[str, int]
_list_str_or_int = _List[_str_or_int]
_strs_or_ints = _Union[_str_or_int, _list_str_or_int]


def go_isolate(network: _Union[Network, Networks],
               go_from: _strs_or_ints = None,
               from_demographic: _strs_or_ints = None,
               go_to: _strs_or_ints = None,
               to_demographic: _strs_or_ints = None,
               self_isolate_stage: _Union[_List[int], int] = 2,
               fraction: _Union[_List[float], float] = 1.0,
               number: int = None,
               **kwargs) -> None:
    """This go function will move individuals from the "from"
       demographic(s) to the "to" demographic if they show any
       signs of infection (the disease stage is greater or equal
       to 'self_isolate_stage'. This can move
       a subset of individuals if 'fraction' is less than 1, e.g.
       0.5 would move 50% of individuals (chosen using
       a random binomial distribution)

       This can move a subset of individuals if 'fraction' is less than 1,
       e.g. 0.5 would move 50% of individuals (chosen using
       a random binomial distribution). You can also specify the
       maximum number of individuals to move per ward by
       specifying the 'number' parameters

       Parameters
       ----------
       go_from: int, str or list of int / str
         The ID(s) of the demographic(s) to move from. This is the old
         parameter name used to maintain backwards compatibility.
         Prefer to use from_demo if you can
       go_to: int, str or list of int / str
         The ID(s) of the demographic(s) to move to. This is the old
         parameter name used to maintain backwards compatibility.
         Prefer to use to_demo if you can
       from_demographic: int, str or list of int / str
         The ID(s) of the demographic(s) to move from. This can be either
         a single demographic (identified by an integer ID or string),
         a list of demographics, or, if None, then all demographics.
       to_demographic: int, str or list of int / str
         The ID(s) of the demographic to move to. This can be either
         a single demographic (identified by an integer ID or string),
         a list of demographics, or, if None, then all demographics.
         If this is not set, then it is equal to "from_demo"
       self_isolate_stage: int or List[int]
         The stage of infection an individual must be at before they
         are moved into this demographic. If a list is passed then
         this can be multiple stages, e.g. [2, 3] will move at
         stages 2 and 3. Multiple stages are needed if only
         a fraction of individuals move.
       fraction: float or List[float]
         The fraction (percentage) of individuals who are moved from
         this stage into isolation. If this is a single value then
         the same fraction applies to all self_isolation_stages. Otherwise,
         the fraction for self_isolate_stage[i] is fraction[i]
       number: int
         The maximum number of individuals in each ward / ward-link to move.
         The fraction is taken from min(number, number_in_ward). By
         default all individuals in a ward / ward-link are sampled.
       **kwargs:
         This calls go_ward, so any options that are acceptible to go_ward
         (with the exception of 'generator') can be passed here too
    """
    from ._movegenerator import MoveGenerator
    from ._go_ward import go_ward

    if from_demographic is None:
        from_demographic = go_from

    if to_demographic is None:
        to_demographic = go_to

    # first get the base moves...
    generator = MoveGenerator(from_demographic=from_demographic,
                              to_demographic=to_demographic)

    # find the largest index of the disease stage
    N_INF_CLASSES = 0

    for stage in generator.generate(network):
        N_INF_CLASSES = max(N_INF_CLASSES, stage[1], stage[3])

    if isinstance(self_isolate_stage, list):
        stages = [int(stage) for stage in self_isolate_stage]
    else:
        stages = [int(self_isolate_stage)]

    if isinstance(fraction, list):
        fractions = [float(frac) for frac in fraction]
    else:
        fractions = [float(fraction)] * len(stages)

    for fraction in fractions:
        if fraction < 0 or fraction > 1:
            raise ValueError(
                f"The move fractions {fractions} should all be 0 to 1")

    for stage in stages:
        if stage < 1 or stage >= N_INF_CLASSES:
            raise ValueError(
                f"The stage(s) of self-isolation {stages} "
                f"is invalid for a disease with {N_INF_CLASSES} stages")

    if len(stages) != len(fractions):
        raise ValueError(
            f"The number of self isolation stages {stages} must equal "
            f"the number of fractions {fractions}")

    for stage, fraction in zip(stages, fractions):
        from_stage = list(range(stage, N_INF_CLASSES))
        to_stage = from_stage

        generator = MoveGenerator(from_demographic=from_demographic,
                                  to_demographic=to_demographic,
                                  from_stage=from_stage,
                                  to_stage=to_stage,
                                  fraction=fraction)

        go_ward(network=network, generator=generator, **kwargs)
