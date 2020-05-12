
from typing import List as _List

__all__ = ["align_strings"]


def align_strings(strings: _List[str], sep: str = ":") -> _List[str]:
    """Align the passed list of strings such that they are aligned
       against every appearance of 'sep'
    """
    results = []

    size = []

    for string in strings:
        words = string.split(sep)

        for i, word in enumerate(words):
            if i >= len(size):
                size.append(len(word))
            elif len(word) > size[i]:
                size[i] = len(word)

    for string in strings:
        words = string.split(sep)

        result = ""

        for i, word in enumerate(words):
            diff = size[i] - len(word)
            result += diff * " " + word

            if i < len(words) - 1:
                result += sep

        results.append(result)

    return results
