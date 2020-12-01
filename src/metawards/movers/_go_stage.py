
from typing import Union as _Union
from typing import List as _List

__all__ = ["go_stage"]

_str_or_int = _Union[str, int]
_list_str_or_int = _List[_str_or_int]
_strs_or_ints = _Union[_str_or_int, _list_str_or_int]


def go_stage(go_from: _strs_or_ints = None,
             from_demographic: _strs_or_ints = None,
             go_to: _strs_or_ints = None,
             to_demographic: _strs_or_ints = None,
             from_stage: _strs_or_ints = None,
             to_stage: _strs_or_ints = None,
             fraction: float = 1.0,
             number: int = None,
             **kwargs) -> None:
    """This go function will move individuals from the "go_from"
       demographic(s) to the "go_to" demographic, as well as
       the 'from_stage' disease stage(s) to the 'to_stage'
       diseaes stage(s).

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
       from_stage: int, str or list of int / str
         The ID(s) of the disease stage(s) to move from. This can be either
         a single stage (identified by an integer ID or string),
         a list of stages, or, if None, then all stages.
       to_stage: int, str or list of int / str
         The ID(s) of the disease stage(s) to move to. This can be either
         a single stage (identified by an integer ID or string),
         a list of stages, or, if None, then all stages. If this
         is not set, then it is equal to "from_stage"
       fraction: float
         The fraction of individuals in each ward to move, e.g. 0.75 would move
         75% of the individuals in a ward / ward-link. By default 100%
         are moved.
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

    generator = MoveGenerator(from_demographic=from_demographic,
                              to_demographic=to_demographic,
                              from_stage=from_stage, to_stage=to_stage,
                              fraction=fraction, number=number)

    go_ward(generator=generator, **kwargs)
