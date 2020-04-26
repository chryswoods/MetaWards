
import pytest
from metawards.utils import string_to_ints


@pytest.mark.parametrize('s, expect',
    [ (["1"], [1]),
      (["-1"], [-1]),
      ([""], []),
      (["1", "1"], [1]),
      (["1", "2"], [1, 2]),
      (["2", "1"], [1, 2]),
      (["1, 4, 2, 5"], [1,2,4,5]),
      (["5,2,5, 4, 4"], [2,4,5]),
      (["3,4,8-15"], [3,4,8,9,10,11,12,13,14,15])
    ])
def test_string_to_ints(s, expect):
    result = string_to_ints(s)

    assert result == expect
