
from libc.stdio cimport FILE, fopen, fscanf, fclose, feof

from .._network import Network
from ._profiler import Profiler

from ._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["assert_sane_network"]


def assert_sane_network(network: Network, profiler: Profiler):
    """This function runs through and checks that the passed network
       is sane. If it is not, it prints some information and raises
       an AssertionError
    """
    params = network.params
    nodes = network.nodes

    # read in the "work_size" file - this details the expected
    # population in each ward. This should match what has
    # been calculated via the links and play links files
    import os

    filename = params.input_files.work_size

    from ._console import Console

    if filename is None:
        Console.warning(f"Skipping network validation as work_size is null")

    elif not os.path.exists(filename):
        Console.warning(
                f"Skipping network validation as {filename} is unreadable")

    cdef char* fname
    cdef FILE* cfile

    p = profiler.start("read_and_validate")

    filename = filename.encode("UTF-8")
    fname = filename
    cfile = fopen(fname, "r")

    if cfile == NULL:
        raise FileNotFoundError(f"No such file or directory: {filename}")

    cdef int i = 0
    cdef nnodes = network.nnodes
    cdef double * nodes_denominator_n = get_double_array_ptr(
                                                    nodes.denominator_n)
    cdef double * nodes_denominator_p = get_double_array_ptr(
                                                    nodes.denominator_p)
    cdef double * nodes_play_suscept = get_double_array_ptr(
                                                    nodes.play_suscept)

    cdef int node_id = 0
    cdef double weight = 0.0
    cdef double node_weight = 0.0
    cdef int nfailed = 0

    while not feof(cfile):
        fscanf(cfile, "%d %lf\n", &node_id, &weight)

        if node_id < 0 or node_id > nnodes:
            Console.print(f"Corrupt index in work_size file: {node_id}")
            nfailed += 1
            continue

        node_weight = nodes_denominator_n[node_id]

        if weight != node_weight:
            Console.print(f"Incorrect weight for node {node_id}. Should be "
                          f"{weight}, but is instead {node_weight}.")
            nfailed += 1

        if nodes_denominator_p[node_id] != nodes_play_suscept[node_id]:
            Console.print(
                f"Disagreement in play_suscept for node {node_id}, "
                f"{nodes_denominator_p[node_id]} versus "
                f"{nodes_play_suscept[node_id]}")
            nfailed += 1

    if nfailed > 0:
        raise AssertionError(
            f"Invalid Network. Number of failures equals {nfailed}")

    p = p.stop()

