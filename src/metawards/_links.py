
from ._link import Link


__all__ = ["Links"]


class Links:
    """This is a container class for Links. This uses arrays
       to store a list of Link objects as a "struct of arrays".
       This should improve speed of loading and access.
    """

    def __init__(self, N: int = 0):
        """Create a container for up to "N" Links"""
        if N <= 0:
            self._is_null = True
        else:
            self._is_null = False

            from .utils._array import create_double_array, create_int_array

            # Struct of arrays for each piece of data. See the
            # Link class for information about what each variable
            # holds. Code uses "-1" to represent a null value
            self.ifrom = create_int_array(N, -1)
            self.ito = create_int_array(N, -1)

            self.weight = create_double_array(N, 0.0)
            self.suscept = create_double_array(N, 0.0)
            self.distance = create_double_array(N, 0.0)

    def is_null(self):
        return self._is_null

    def __len__(self):
        """Return the number of links in this container"""
        if self._is_null:
            return 0
        else:
            return len(self.ifrom)

    def population(self) -> int:
        """Return the population of these links"""
        if self.weight is None:
            return 0
        else:
            return sum(self.weight)

    def copy(self):
        """Return a copy of these links, using a shallow copy for
           things that stay the same (e.g. ifrom, ito, distance)
           and a deep copy for things that are variable
           (e.g. weight and suscept)
        """
        from copy import copy, deepcopy
        links = copy(self)

        links.weight = deepcopy(self.weight)
        links.suscept = deepcopy(self.suscept)

        return links

    def assert_not_null(self):
        """Assert that this collection of links is not null"""
        assert not self.is_null()

    def assert_valid_index(self, i):
        """Assert that the passed index 'i' is valid for this collection.
           This will return the index with Python reverse indexing,
           so that "-1" refers to the last link in the collection
        """
        self.assert_not_null()
        n = len(self)

        if i < 0:
            i = n + i

        if i < 0 or i >= n:
            raise IndexError(f"Invalid link index {i}. Number of links "
                             f"in this container equals {n}")

        return i

    def __getitem__(self, i: int):
        """Return the link at index 'i'. Note that this is a
           deep copy of the link. Changing the link will not change
           the data in this container. To update the data in this
           container you need to use __setitem__, e.g. via the
           index operator (see __setitem__)
        """
        i = self.assert_valid_index(i)

        return Link(ifrom=self.ifrom[i], ito=self.ito[i],
                    weight=self.weight[i], suscept=self.suscept[i],
                    distance=self.distance[i])

    def __setitem__(self, i: int, value: Link):
        """Set the item as index 'i' equal to 'value'. This deep-copies
           'value' into this container
        """
        i = self.assert_valid_index(i)

        self.ifrom[i] = value.ifrom if value.ifrom is not None else -1
        self.ito[i] = value.ito if value.ito is not None else -1
        self.weight[i] = value.weight if value.weight is not None else 0.0
        self.suscept[i] = value.suscept if value.suscept is not None else 0.0
        self.distance[i] = value.distance if value.distance is not None else 0.0

    def resize(self, N: int):
        """Resize this container to hold 'N' links. This will expand
           the container if 'N' is greater than len(self), or will
           contract the container (deleting excess links) if 'N'
           is less than len(self). This function is called typically
           when you pre-allocate a large Links container, and then
           want to reduce the size to fit the number of loaded links
        """
        if self.is_null():
            # Assign to a new Links object created with this size
            self.__dict__ = Links(N).__dict__
            return
        elif N <= 0:
            self.__dict__ = Links(0).__dict__

        size = len(self)

        if N == size:
            return

        from .utils._array import resize_array

        self.ifrom = resize_array(self.ifrom, N, -1)
        self.ito = resize_array(self.ito, N, -1)
        self.weight = resize_array(self.weight, N, 0.0)
        self.suscept = resize_array(self.suscept, N, 0.0)
        self.distance = resize_array(self.distance, N, 0.0)

    def scale_susceptibles(self, ratio: any = None):
        """Scale the number of susceptibles in these Links
           by the passed scale ratio. This can be a value, e.g.
           ratio = 2.0 will scale the total number of susceptibles
           by 2.0. This can also be lists of values,
           where ward[i] will be scaled by ratio[i]. They can also
           be dictionaries, e.g. ward[i] scaled by ratio[i]

           Parameters
           ----------
           ratio: None, float, list or dict
             The amount by which to scale the total population of
             susceptibles - evenly scales the work and play populations

           Returns
           -------
           None
        """
        from .utils._scale_susceptibles import scale_link_susceptibles
        scale_link_susceptibles(links=self, ratio=ratio)
