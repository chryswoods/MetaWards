
from typing import List
from itertools import chain
import copy

__all__ = ["string_to_ints"]


def rangeString(commaString):
    """Convert the passed comma-separated string of ints (including ranges)
       into a list of integers. Thanks for the great answers on
       stackoverflow
       https://stackoverflow.com/questions/6405208/how-to-convert-numeric-string-ranges-to-a-list-in-python

       This answer was provided by ninjagecko - Cheers :-)
    """
    def hyphenRange(hyphenString):
        hyphenString = hyphenString.strip()

        if len(hyphenString) == 0:
            return []

        try:
            x = [int(x) for x in hyphenString.split('-')]
            return range(x[0], x[-1]+1)
        except ValueError:
            # this can happen if it is a negative number
            if len(hyphenString) == 0:
                return []
            else:
                return [int(hyphenString)]

    return chain(*[hyphenRange(r) for r in commaString.split(',')])


def string_to_ints(string: str = None,
                   strings: List[str] = None):
    """Convert the passed string (or strings) containing
       integers (or ranges of integers) into a single sorted
       list of integers where no value is repeated
    """
    if string is not None:
        if strings is None:
            strings = []
        else:
            if len(strings) > 0:
                strings = copy.copy(strings)

        if isinstance(string, list):
            strings += string
        else:
            strings.append(string)

    ints = {}

    for string in strings:
        for i in rangeString(string):
            ints[int(i)] = 1

    ints = list(ints.keys())
    ints.sort()

    return ints
