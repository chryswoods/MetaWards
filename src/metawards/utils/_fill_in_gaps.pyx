
from .._network import Network

__all__ = ["fill_in_gaps"]


def fill_in_gaps(network: Network, max_nodes: int):
    """Fills in gaps in the network"""
    nodes = network.nodes
    links = network.to_links

    cdef int added = 0
    cdef int i = 0
    cdef int link_to = 0
    cdef int [::1] links_ito = links.ito
    cdef int [::1] nodes_label = nodes.label

    cdef int nnodes = network.nnodes
    cdef int MAX_NODES = max_nodes

    for i in range(1, network.nlinks+1):  # careful of 1-indexing
        link_to = links_ito[i]
        if link_to >= MAX_NODES:
            raise MemoryError(f"Adding a link {link_to} that implies we will "
                              f"have more nodes than are preallocated "
                              f"{MAX_NODES}. Increase max_nodes and try "
                              f"again.")

        if nodes_label[link_to] != link_to:
            print(f"ADDING LINK {i} {link_to} {network.nnodes}")
            nodes_label[link_to] = link_to

            if link_to > nnodes:
                added += (link_to - nnodes)
                nnodes = link_to


    print(f"Number of added nodes equals {added}")

    network.nnodes = nnodes
