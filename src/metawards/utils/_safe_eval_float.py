
from typing import Union as _Union

__all__ = ["safe_eval_float"]


def safe_eval_float(s: _Union[float, int, str]) -> float:
    """Convert 's' to a float. This supports normal floats,
       but also simple maths expressions like 1/1.2,
       plus anything that ends with a "%" is recognised
       as a percentage

       Examples
       --------

       safe_eval_float(0.3)         -> 0.3
       safe_eval_float("5%")        -> 0.05
       safe_eval_float("1/4")       -> 0.25
       safe_eval_float("(30+100)%)  -> 1.3
    """
    try:
        return float(s)
    except Exception:
        pass

    try:
        # this is about as save as eval gets in python
        return float(eval(s, {"__builtins__": None}, {}))
    except Exception:
        pass

    if isinstance(s, str):
        s = s.strip()
        if s.endswith("%"):
            try:
                return safe_eval_float(s[0:-1]) / 100.0
            except Exception:
                pass

    raise ValueError(f"Cannot interpret '{s}' as a float")
