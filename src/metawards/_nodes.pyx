
from ._node import Node

__all__ = ["Nodes"]


class Nodes:
    """This is a container class for Nodes. This uses Numpy arrays
       to store a list of Node objects as a "struct of arrays".
       This should improve speed of loading and access.
    """
    def __init__(self, N: int=0):
        """Create a container for up to "N" nodes"""
        if N <= 0:
            self._is_null = True
        else:
            self._is_null = False

            from .utils._array import create_double_array, create_int_array, \
                                      create_string_array

            # Struct of arrays for each piece of data. See the
            # Node class for information about what each variable
            # holds. Code uses "-1" to represent a null value
            self.label = create_int_array(N, -1)
            self.begin_to = create_int_array(N, -1)
            self.end_to = create_int_array(N, -1)
            self.self_w = create_int_array(N, -1)

            self.begin_p = create_int_array(N, -1)
            self.end_p = create_int_array(N, -1)
            self.self_p = create_int_array(N, -1)

            self.begin_we = create_int_array(N, -1)
            self.end_we = create_int_array(N, -1)
            self.self_we = create_int_array(N, -1)

            self.day_foi = create_double_array(N, 0.0)
            self.night_foi = create_double_array(N, 0.0)
            self.weekend_foi = create_double_array(N, 0.0)

            self.play_suscept = create_double_array(N, 0.0)
            self.save_play_suscept = create_double_array(N, 0.0)

            self.denominator_n = create_double_array(N, 0.0)
            self.denominator_d = create_double_array(N, 0.0)

            self.denominator_p = create_double_array(N, 0.0)
            self.denominator_pd = create_double_array(N, 0.0)

            self.day_inf_prob = create_double_array(N, 0.0)
            self.night_inf_prob = create_double_array(N, 0.0)

            self.x = create_double_array(N, 0.0)  # no good initialiser for x
            self.y = create_double_array(N, 0.0)  # no good initialiser for y

            self.b = create_double_array(N, 0.0)

            self.id = create_string_array(N)
            self.vacid = create_int_array(N, -1)

    def is_null(self):
        return self._is_null

    def __len__(self):
        """Return the number of nodes in this container"""
        if self._is_null:
            return 0
        else:
            return len(self.label)

    def assert_not_null(self):
        """Assert that this collection of nodes is not null"""
        assert not self.is_null()

    def assert_valid_index(self, i):
        """Assert that the passed index 'i' is valid for this collection.
           This will return the index with  Python reverse indexing,
           so that "-1" refers to the last node in the collection
        """
        self.assert_not_null()
        n = len(self)

        if i < 0:
            i = n + i

        if i < 0 or i >= n:
            raise IndexError(f"Invalid node index {i}. Number of nodes "
                             f"in this container equals {n}")

        return i

    def __getitem__(self, i: int):
        """Return the node at index 'i'. Note that this is a
           deep copy of the node. Changing the node will not change
           the data in this container. To update the data in this
           container you need to use __setitem__, e.g. via the
           index operator (see __setitem__)
        """
        i = self.assert_valid_index(i)

        try:
            return Node(label=self.label[i],
                        begin_to=self.begin_to[i],
                        end_to=self.end_to[i],
                        self_w=self.self_w[i],

                        begin_p=self.begin_p[i],
                        end_p=self.end_p[i],
                        self_p=self.self_p[i],

                        begin_we=self.begin_we[i],
                        end_we=self.end_we[i],
                        self_we=self.self_we[i],

                        day_foi=self.day_foi[i],
                        night_foi=self.night_foi[i],
                        weekend_foi=self.weekend_foi[i],

                        play_suscept=self.play_suscept[i],
                        save_play_suscept=self.save_play_suscept[i],

                        denominator_n=self.denominator_n[i],
                        denominator_d=self.denominator_d[i],

                        denominator_p=self.denominator_p[i],
                        denominator_pd=self.denominator_pd[i],

                        x=self.x[i],
                        y=self.y[i],

                        b=self.b[i],

                        id=self.id[i],
                        vacid=self.vacid[i])
        except Exception as e:
            print(f"Error at index {i}: size = {len(self)}: {e.__class__} {e}")
            raise e

    def __setitem__(self, i: int, value: Node):
        """Set the item as index 'i' equal to 'value'. This deep-copies
           'value' into this container
        """
        i = self.assert_valid_index(i)

        self.label[i] = value.label if value.label is not None else -1
        self.begin_to[i] = value.begin_to if value.begin_to is not None else -1
        self.end_to[i] = value.end_to if value.end_to is not None else -1
        self.self_w[i] = value.self_w if value.self_w is not None else -1

        self.begin_p[i] = value.begin_p if value.begin_p is not None else -1
        self.end_p[i] = value.end_p if value.end_p is not None else -1
        self.self_p[i] = value.self._p if value.self_p is not None else -1

        self.begin_we[i] = value.begin_we if value.begin_we is not None else -1
        self.end_we[i] = value.end_we if value.end_we is not None else -1
        self.self_we[i] = value.self_we if value.self_we is not None else -1

        self.day_foi[i] = value.day_foi if value.day_foi is not None else 0.0
        self.night_foi[i] = value.night_foi if value.night_foi is not None else 0.0
        self.weekend_foi[i] = value.weekend_foi if value.weekend_foi is not None else 0.0

        self.play_suscept[i] = value.play_suscept if value.play_suscept is not None else 0.0
        self.save_play_suscept[i] = value.save_play_suscept if value.save_play_suscept is not None else 0.0

        self.denominator_n[i] = value.denominator_n if value.denominator_n is not None else 0.0
        self.denominator_d[i] = value.denominator_d if value.denominator_d is not None else 0.0

        self.denominator_p[i] = value.denominator_p if value.denominator_p is not None else 0.0
        self.denominator_pd[i] = value.denominator_pd if value.denominator_pd is not None else 0.0

        self.x[i] = value.x if value.x is not None else 0.0
        self.y[i] = value.y if value.y is not None else 0.0

        self.b[i] = value.b if value.b is not None else 0.0

        self.id[i] = value.id  # this is a python list and can have None
        self.vacid[i] = value.vacid if value.vacid is not None else -1

    def resize(self, N: int):
        """Resize this container to hold 'N' nodes. This will expand
           the container if 'N' is greater than len(self), or will
           contract the container (deleting excess nodes) if 'N'
           is less than len(self). This function is called typically
           when you pre-allocate a large Nodes container, and then
           want to reduce the size to fit the number of loaded nodes
        """
        if self.is_null():
            # Assign to a new Nodes object created with this size
            self.__dict__ = Nodes(N).__dict__
            return
        elif N <= 0:
            self.__dict__ = Nodes(0).__dict__

        size = len(self)

        if N == size:
            return

        from .utils._array import resize_array
        self.label = resize_array(self.label, N, -1)
        self.begin_to = resize_array(self.begin_to, N, -1)
        self.end_to = resize_array(self.end_to, N, -1)
        self.self_w = resize_array(self.self_w, N, -1)

        self.begin_p = resize_array(self.begin_p, N, -1)
        self.end_p = resize_array(self.end_p, N, -1)
        self.self_p = resize_array(self.self_p, N, -1)

        self.begin_we = resize_array(self.begin_we, N, -1)
        self.end_we = resize_array(self.end_we, N, -1)
        self.self_we = resize_array(self.self_we, N, -1)

        self.day_foi = resize_array(self.day_foi, N, 0.0)
        self.night_foi = resize_array(self.night_foi, N, 0.0)
        self.weekend_foi = resize_array(self.weekend_foi, N, 0.0)

        self.play_suscept = resize_array(self.play_suscept, N, 0.0)
        self.save_play_suscept = resize_array(self.save_play_suscept, N, 0.0)

        self.denominator_n = resize_array(self.denominator_n, N, 0.0)
        self.denominator_d = resize_array(self.denominator_d, N, 0.0)

        self.denominator_p = resize_array(self.denominator_p, N, 0.0)
        self.denominator_pd = resize_array(self.denominator_pd, N, 0.0)

        self.x = resize_array(self.x, N, 0.0)
        self.y = resize_array(self.y, N, 0.0)

        self.b = resize_array(self.b, N, 0.0)

        self.vacid = resize_array(self.vacid, N, -1)

        self.id = resize_array(self.id, N)
