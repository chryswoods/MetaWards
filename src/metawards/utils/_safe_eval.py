
from typing import Union as _Union

__all__ = ["safe_eval_number"]


def safe_eval_number(s: _Union[float, int, str]) -> float:
    """Convert 's' to a number. This supports normal floats,
       but also simple maths expressions like 1/1.2,
       plus anything that ends with a "%" is recognised
       as a percentage

       Examples
       --------

       safe_eval_number(0.3)         -> 0.3
       safe_eval_number("5%")        -> 0.05
       safe_eval_number("1/4")       -> 0.25
       safe_eval_number("(30+100)%)  -> 1.3
    """
    if isinstance(s, float) or isinstance(s, int):
        return s

    if not isinstance(s, str):
        s = str(s)

    try:
        # this is about as save as eval gets in python
        x = eval(s, {"__builtins__": None}, {})

        v = float(x)
        if v.is_integer():
            return int(x)
        else:
            return v
    except Exception:
        pass

    if isinstance(s, str):
        s = s.strip()
        if s.endswith("%"):
            try:
                return safe_eval_number(s[0:-1]) / 100.0
            except Exception:
                pass

    raise ValueError(f"Cannot interpret '{s}' as a float")
