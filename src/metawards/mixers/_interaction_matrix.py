
from typing import List as _List

__all__ = ["InteractionMatrix"]


class InteractionMatrix:
    """This is an interaction matrix, which is used to control
       how the FOIs of different demographics are merged together.

       An interaction matrix is just a square matrix, with
       a list[][] being perfectly acceptable. This is really
       a convenience class that makes it easier to create
       more complex interaction matrixes
    """

    def __init__(self, n: int, value: float = 0.0):
        """Construct an interaction matrix that is n x n in size,
           where all values equal 'value'
        """
        n = int(n)

        if n <= 0:
            raise ValueError(
                "You cannot create a zero-sized interaction matrix")

        value = float(value)

        self._matrix = []

        for i in range(0, n):
            row = [value] * n
            self._matrix.append(row)

    def __getitem__(self, i: int):
        """Return the ith row of the matrix"""
        return self._matrix[i]

    def __len__(self):
        return len(self._matrix)

    def __eq__(self, other):
        if len(self) != len(other):
            return False

        for i, row in enumerate(self._matrix):
            if len(row) != len(other[i]):
                return False

            for j, value in enumerate(row):
                if value != other[i][j]:
                    return False

        return True

    def __setitem__(self, i: int, row: _List[int]):
        """"Set the ith row of the matrix equal to 'row'"""
        if len(row) != len(self):
            raise ValueError(f"Incorrect row size {len(row)} for a "
                             f"{len(self)} by {len(self)} interaction matrix")

    @staticmethod
    def ones(n: int, value: float = 1.0):
        """Return a n x n matrix where each element equals 'value'"""
        return InteractionMatrix(n=n, value=value)

    @staticmethod
    def zeroes(n: int, value: float = 0.0):
        """Return a n x n matrix where each element equals 'value'"""
        return InteractionMatrix.ones(n=n, value=value)

    @staticmethod
    def diagonal(n: int, value: float = 1.0,
                 off_diagonal: float = 0.0):
        """Return a n x n matrix where each diagonal element equals
           'value' and each off-diagonal element equals 'off_diagonal'
        """
        m = InteractionMatrix(n=n, value=off_diagonal)

        for i in range(0, n):
            m[i][i] = value

        return m

    @staticmethod
    def identity(n: int, value: float = 1.0,
                 off_diagonal: float = 0.0):
        """Return a n x n matrix where each diagonal element equals
           'value' and each off-diagonal element equals 'off_diagonal'
        """
        return InteractionMatrix.diagonal(n=n, value=value,
                                          off_diagonal=off_diagonal)

    def __str__(self):
        lines = []

        for row in self._matrix:
            r = ["%5.3f" % x for x in row]
            lines.append("| " + ", ".join(r) + " |")

        return "\n".join(lines)

    def resize(self, n: int, value: float = 0.0):
        """Resize this matrix to 'n x n', adding in extra
           values equal to 'value' if needed
        """
        if len(self) == n:
            return

        elif n < len(self):
            m = InteractionMatrix(n=n)

            for i in range(0, n):
                for j in range(0, n):
                    m[i][j] = self[i][j]

            self._matrix = m._matrix

        else:
            m = InteractionMatrix(n=n, value=value)

            n = len(self)

            for i in range(0, n):
                for j in range(0, n):
                    m[i][j] = self[i][j]

            self._matrix = m._matrix

    def detach(self, n: int):
        """Detach the 'nth' demographic from interacting with
           any other demographics. This sets the ith row and ith
           column equal to zero (which not changing m[n][n])
        """
        for i in range(len(self)):
            if i != n:
                self[i][n] = 0.0
                self[n][i] = 0.0
