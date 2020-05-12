
import pytest

from metawards.utils import safe_eval_float


@pytest.mark.parametrize(['s', 'expect'],
                         [(5, 5.0),
                          ("5%", 0.05),
                          ("0.3 + 0.5", 0.8),
                          ("1/4", 0.25),
                          ("(25+40)%", 0.65)
                          ])
def test_safe_eval_float(s, expect):
    result = safe_eval_float(s)

    assert result == expect
