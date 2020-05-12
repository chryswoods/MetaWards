
import pytest

from metawards import VariableSet

test_vals = [[0.4],
             [0, 1, 2, 3, 4],
             [0.5, 0.7, True, False, 1.3, 22.9],
             []
             ]


@pytest.mark.parametrize('vals', test_vals)
def test_fingerprints(vals):
    fingerprint = VariableSet.create_fingerprint(vals=vals)

    result, repeat = VariableSet.extract_values(fingerprint)

    assert result == vals
    assert repeat is None

    for i in range(0, 10):
        fingerprint = VariableSet.create_fingerprint(vals=vals, index=i,
                                                     include_index=True)

        result, repeat = VariableSet.extract_values(fingerprint)

        print(vals, fingerprint, result, repeat)

        assert result == vals
        assert repeat == i


def test_with_dirs():
    filenames = [("output_catalyst/overview_0i2v0i1.jpg", [0.2, 0.1]),
                 ("output_catalyst/overview_0i4v0i1.jpg", [0.4, 0.1]),
                 ("output_catalyst/overview_0i2v0i2.jpg", [0.2, 0.2]),
                 ("output_catalyst/overview_0i4v0i2.jpg", [0.4, 0.2]),
                 ("output_catalyst/overview_0i2v0i3.jpg", [0.2, 0.3]),
                 ("output_catalyst/overview_0i4v0i3.jpg", [0.4, 0.3]),
                 ("output_catalyst/overview_0i2v0i4.jpg", [0.2, 0.4]),
                 ("output_catalyst/overview_0i4v0i4.jpg", [0.4, 0.4]),
                 ("output_catalyst/overview_0i2v0i5.jpg", [0.2, 0.5]),
                 ("output_catalyst/overview_0i4v0i5.jpg", [0.4, 0.5]),
                 ("output_catalyst/overview_0i3v0i1.jpg", [0.3, 0.1]),
                 ("output_catalyst/overview_0i5v0i1.jpg", [0.5, 0.1]),
                 ("output_catalyst/overview_0i3v0i2.jpg", [0.3, 0.2]),
                 ("output_catalyst/overview_0i5v0i2.jpg", [0.5, 0.2]),
                 ("output_catalyst/overview_0i3v0i3.jpg", [0.3, 0.3]),
                 ("output_catalyst/overview_0i5v0i3.jpg", [0.5, 0.3]),
                 ("output_catalyst/overview_0i3v0i4.jpg", [0.3, 0.4]),
                 ("output_catalyst/overview_0i5v0i4.jpg", [0.5, 0.4]),
                 ("output_catalyst/overview_0i3v0i5.jpg", [0.3, 0.5]),
                 ("output_catalyst/overview_0i5v0i5.jpg", [0.5, 0.5])]

    for (filename, expect) in filenames:
        print(filename, expect)
        values, repeat_idx = VariableSet.extract_values(filename)

        print(values, repeat_idx)

        assert repeat_idx is None
        assert values == expect


if __name__ == "__main__":
    for vals in test_vals:
        test_fingerprints(vals=vals)

    test_with_dirs()
