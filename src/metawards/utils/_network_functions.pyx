

from typing import Tuple as _Tuple

from .._network import Network, PersonType
from .._wardid import WardID

from ._get_array_ptr cimport get_int_array_ptr

def network_get_index(network: Network, id: WardID) -> _Tuple[PersonType, int]:
    """Return the index of the Node or Link(s) that corresponds
        to the passed WardID.

        This returns a tuple of three values;

        (PersonType, start_idx, end_idx)

        If this is a worker, then it will either return the
        index of the Link for a specific work-link connection,
        or the range of indicies for all of the work links
        to this ward, so

        (PersonType.WORKER, link_idx, link_idx+!)  for a single link, or

        (PersonType.WORKER, link.begin_to, link.end_to) for all links

        If this is a player, then it will return the ID of the
        Node (which is the index of the Node in Nodes), and
        so

        (PersonType.PLAYER, node_index, node_index+1)

        This returns (PersonType, -1, -1) if there is no ward
        or connection that matches this request.
    """
    if id.is_null():
        raise ValueError(f"Cannot get the index of a null WardID")

    cdef int home = -1

    try:
        home = network.get_node_index(id.home())
    except Exception:
        pass

    if home < 0 or home > network.nnodes:
        if id.is_ward():
            return (PersonType.PLAYER, -1, -1)
        else:
            return (PersonType.WORKER, -1, -1)

    if id.is_ward():
        return (PersonType.PLAYER, home, home + 1)
    elif id.is_all_commute():
        nodes = network.nodes
        return (PersonType.WORKER, nodes.begin_to[home], nodes.end_to[home])

    cdef int commute = network.get_node_index(id.commute())

    if home == 0 and commute == 0:
        # this is the null worker link
        return (PersonType.WORKER, 0, 1)

    # need to see if there is a work link between these
    # two wards...
    wards = network.nodes
    links = network.links

    cdef int * wards_begin_to = get_int_array_ptr(wards.begin_to)
    cdef int * wards_end_to = get_int_array_ptr(wards.end_to)

    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)
    cdef int * links_ito = get_int_array_ptr(links.ito)

    cdef int i = 0
    cdef int index = -1
    cdef int ifrom = 0
    cdef int ito = 0

    with nogil:
        if wards_begin_to[home] != -1 and wards_end_to[home] != -1:
            for i in range(wards_begin_to[home], wards_end_to[home]):
                ifrom = links_ifrom[i]
                ito = links_ito[i]

                if ifrom == home and ito == commute:
                    index = i
                    break

    if index == -1:
        return (PersonType.WORKER, -1, -1)
    else:
        return (PersonType.WORKER, index, index + 1)
