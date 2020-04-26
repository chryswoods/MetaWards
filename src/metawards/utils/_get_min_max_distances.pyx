
from .._network import Network

from ._profiler import Profiler

__all__ = ["get_min_max_distances"]


def get_min_max_distances(network: Network, nthreads: int = 1,
                          profiler: Profiler = None):
    """Return the minimum and maximum distances recorded in the network"""
    links = network.to_links

    cdef double mindist = -1.0
    cdef double maxdist = -1.0

    cdef int i = 0
    cdef double dist = 0.0
    cdef double [::1] links_distance = links.distance

    for i in range(1, network.nlinks+1):
        dist = links_distance[i]

        if dist:
            if mindist < 0.0:
                mindist = dist
                maxdist = dist
            elif dist > maxdist:
                maxdist = dist
            elif dist < mindist:
                mindist = dist

    print(f"maxdist {maxdist} mindist {mindist}")

    return (mindist, maxdist)
