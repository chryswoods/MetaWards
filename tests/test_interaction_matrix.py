
import pytest

from metawards.mixers import InteractionMatrix


@pytest.mark.parametrize('n, value',
                         [(1, 0.0),
                          (2, 0.5),
                          (4, 1.0),
                          (4, 3.141)])
def test_ones(n, value):
    m = InteractionMatrix.ones(n=n, value=value)

    for i in range(0, n):
        for j in range(0, n):
            assert m[i][j] == value

    m = InteractionMatrix.zeroes(n=n, value=value)

    for i in range(0, n):
        for j in range(0, n):
            assert m[i][j] == value


@pytest.mark.parametrize('n, value, off_diagonal',
                         [(1, 1.0, 0.0),
                          (2, 1.0, 0.0),
                          (3, 2.5, 0.8)])
def test_diagonal(n, value, off_diagonal):
    m = InteractionMatrix.diagonal(n=n, value=value, off_diagonal=off_diagonal)

    for i in range(0, n):
        for j in range(0, n):
            if i == j:
                assert m[i][j] == value
            else:
                assert m[i][j] == off_diagonal

    m = InteractionMatrix.identity(n=n, value=value, off_diagonal=off_diagonal)

    for i in range(0, n):
        for j in range(0, n):
            if i == j:
                assert m[i][j] == value
            else:
                assert m[i][j] == off_diagonal


def test_matrix():
    m = InteractionMatrix(n=3)

    for i in range(0, 3):
        for j in range(0, 3):
            assert m[i][j] == 0.0

    m[0][0] = 1
    m[1][1] = 1
    m[2][2] = 1

    for i in range(0, 3):
        assert m[i][i] == 1

    assert m == InteractionMatrix.identity(n=3)
    assert m != InteractionMatrix.ones(n=3)

    from copy import deepcopy
    m2 = deepcopy(m)
    m2.resize(6)

    for i in range(0, 3):
        for j in range(0, 3):
            assert m[i][j] == m2[i][j]

        for j in range(3, 6):
            assert m2[i][j] == 0

    for i in range(3, 6):
        for j in range(0, 6):
            assert m2[i][j] == 0

    m2.detach(1)

    for i in range(0, 6):
        if i != 1:
            assert m2[i][1] == 0
            assert m2[1][i] == 0

    m3 = InteractionMatrix.diagonal(n=4, value=1.0, off_diagonal=0.5)

    m3.detach(2)

    print(m3)

    for i in range(0, 4):
        for j in range(0, 4):
            if i == j:
                assert m3[i][j] == 1.0
            elif i == 2 or j == 2:
                assert m3[i][j] == 0.0
            else:
                assert m3[i][j] == 0.5
