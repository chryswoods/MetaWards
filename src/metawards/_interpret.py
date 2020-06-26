
from typing import Union as _Union

__all__ = ["Interpret"]


_Number = _Union[int, float]


def _clamp_range(val, minval, maxval):
    """Ensure that 'val' is clamped to between 'minval' and 'maxval'
       inclusive (if they have been set)
    """
    if minval is not None:
        if val < minval:
            return minval

    if maxval is not None:
        if val > maxval:
            return maxval

    return val


class Interpret:
    """This is a static class that provides some routines for interpreting
       values from inputs (normally strings). This is used heavily by
       code that reads values from the user or from files
    """
    @staticmethod
    def string(s: any) -> str:
        """Interpret and return a string from 's'"""
        return str(s)

    @staticmethod
    def random_integer(s: str = None, rng=None, minval: int = None,
                       maxval: int = None) -> int:
        """Interpret a random integer from the passed string,
           specifying the random number generator to use, and
           optionally adding additional constraints on the minimum
           and maximum values
        """
        if s is None:
            rmin = None
            rmax = None
        else:
            import re

            m = re.search(r"rand\(\s*(-?\d*)\s*\,?\s*(-?\d*)\s*\)",
                          Interpret.string(s), re.IGNORECASE)

            if m is None:
                raise ValueError(
                    f"Cannot interpret a random integer from {s}")

            try:
                rmin = int(m.groups()[0])
            except Exception:
                rmin = None

            try:
                rmax = int(m.groups()[1])
            except Exception:
                rmax = None

        if minval is not None:
            minval = int(minval)

            if rmin is None:
                rmin = minval
            else:
                if rmin < minval:
                    rmin = minval

        if maxval is not None:
            maxval = int(maxval)

            if rmax is None:
                rmax = maxval
            else:
                if rmax > maxval:
                    rmax = maxval

        if rmin is None:
            rmin = 1

        if rmax is None:
            rmax = 2**32 - 1

        if rmax < rmin:
            tmp = rmin
            rmin = rmax
            rmax = tmp

        from .utils._ran_binomial import ran_int
        # we want to be from 'min' to 'max' inclusive
        return ran_int(rng, rmin, rmax)

    @staticmethod
    def random_number(s: str = None, rng=None, minval: float = None,
                      maxval: float = None) -> float:
        """Interpret a random number (float) from the passed string,
           specifying the random number generator to use, and
           optionally adding additional constraints on the minimum
           and maximum values
        """
        if s is None:
            rmin = None
            rmax = None
        else:
            import re

            m = re.search(r"rand\(\s*([-?\d\.]*)\s*\,?\s*([-?\d\.]*)\s*\)",
                          Interpret.string(s), re.IGNORECASE)

            if m is None:
                raise ValueError(
                    f"Cannot interpret a random integer from {s}")

            try:
                rmin = float(m.groups()[0])
            except Exception:
                rmin = None

            try:
                rmax = float(m.groups()[1])
            except Exception:
                rmax = None

        if minval is not None:
            minval = float(minval)

            if rmin is None:
                rmin = minval
            else:
                if rmin < minval:
                    rmin = minval

        if maxval is not None:
            maxval = float(maxval)

            if rmax is None:
                rmax = maxval
            else:
                if rmax > maxval:
                    rmax = maxval

        if rmin is None:
            rmin = 0.0

        if rmax is None:
            rmax = rmin + 1.0

        if rmax < rmin:
            tmp = rmin
            rmin = rmax
            rmax = tmp

        from .utils._ran_binomial import ran_uniform
        return rmin + ((rmax - rmin) * ran_uniform(rng))

    @staticmethod
    def integer(s: any, rng=None, minval: int = None,
                maxval: int = None) -> int:
        """Interpret and return an integer from 's', using the
           passed random number generator if this is a request
           for a random integer, and within the specified bounds
           of 'minval' and 'maxval' if needed.

           This can interpret 's' as an expression, e.g. "6 / 3" etc.
        """
        try:
            d = int(s)
        except Exception:
            d = None

        if d is not None:
            return _clamp_range(d, minval=minval, maxval=maxval)

        s = Interpret.string(s)

        try:
            d = Interpret.random_integer(s=s, rng=rng, minval=minval,
                                         maxval=maxval)
            return d
        except Exception:
            d = None

        try:
            from .utils._safe_eval import safe_eval_number
            d = int(safe_eval_number(s))
        except Exception:
            d = None

        if d is not None:
            return _clamp_range(d, minval=minval, maxval=maxval)
        else:
            raise ValueError(f"Cannot interpret an integer from {s}")

    @staticmethod
    def number(s: any, rng=None, minval: _Number = None,
               maxval: _Number = None) -> _Number:
        """Interpret and return a number (integer or float) using
           the passed random number generator if this is a request
           for a random number, and within the specified bound of
           'minval' and 'maxval' is needed

           This can interpret 's' as an expression, e.g. "2.4 * 3.6" etc.
        """
        try:
            d = float(s)
            if d.is_integer():
                d = int(s)

        except Exception:
            d = None

        if d is not None:
            return _clamp_range(d, minval=minval, maxval=maxval)

        s = Interpret.string(s)

        try:
            d = Interpret.random_number(s=s, rng=rng, minval=minval,
                                        maxval=maxval)
            return d
        except Exception:
            d = None

        try:
            from .utils._safe_eval import safe_eval_number
            d = safe_eval_number(s)
        except Exception:
            d = None

        if d is not None:
            return _clamp_range(d, minval=minval, maxval=maxval)
        else:
            raise ValueError(f"Cannot interpret a number from {s}")

    @staticmethod
    def boolean(s: any, rng=None) -> bool:
        """Interpret and return a boolean (True or False) using
           the passed random number generator if this is a request
           for a random boolean
        """
        if s is None:
            return False
        elif isinstance(s, bool):
            return s
        else:
            s = Interpret.string(s)

            s = s.strip().lower()

            if s in ["true", "yes", "on"]:
                return True
            elif s in ["false", "no", "off"]:
                return False

            d = Interpret.integer(s, rng=rng, minval=0, maxval=1)

            if d == 0:
                return False
            else:
                return True

    @staticmethod
    def date(s: any, allow_fuzzy: bool = True):
        """Return a Python datetime.date object from the passed
           's', allowing fuzzy dates if 'allow_fuzzy' is true
        """
        s = Interpret.string(s)

        try:
            from datetime import date
            d = date.fromisoformat(s)
        except Exception:
            d = None

        if d is None:
            try:
                from dateparser import parse
                d = parse(s).date()
            except Exception:
                d = None

        if d is None:
            raise ValueError(f"Could not interpret a date from '{s}'")

        return d

    @staticmethod
    def day(s: any, rng=None, minval: int = None, maxval: int = None) -> int:
        """Return a day number (integer) from the passed 's'. This is
           a shorthand for 'integer', but may take on more meaning
           if the day needs to be more specialised
        """
        return Interpret.integer(s=s, rng=rng, minval=minval, maxval=maxval)

    @staticmethod
    def day_or_date(s: any, rng=None, minval: int = None, maxval: int = None,
                    allow_fuzzy: bool = True):
        """Convenience function that matches a day or a date from the
           passed 's'
        """
        # Try a simple integer first, to prevent date weirdness
        try:
            return int(s)
        except Exception:
            pass

        # Do date first so that we can parse POSIX dates
        try:
            return Interpret.date(s=s, allow_fuzzy=allow_fuzzy)
        except Exception:
            pass

        try:
            return Interpret.day(s=s, rng=rng, minval=minval, maxval=maxval)
        except Exception:
            pass

        raise ValueError(f"Cannot interpret a day or date from {s}")
