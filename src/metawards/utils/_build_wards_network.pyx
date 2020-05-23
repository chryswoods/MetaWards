#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

from libc.stdio cimport FILE, fopen, fscanf, fclose, feof

from .._parameters import Parameters
from .._network import Network
from .._nodes import Nodes
from .._links import Links

from ._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

from ._profiler import Profiler, NullProfiler

__all__ = ["build_wards_network"]


def _read_network(filename: str, max_nodes: int, max_links: int):
    """This function reads in the network of nodes and links
       from the passed file, returning a tuple of (Nodes, Links)
    """
    nodes = Nodes(max_nodes + 1)     # need to pre-allocate nodes and links
    links = Links(max_links + 1)   # both of these use 1-indexing

    cdef int MAX_LINKS = max_links
    cdef int MAX_NODES = max_nodes

    cdef int nlinks = 0
    cdef int nnodes = 0

    cdef int from_id = 0
    cdef int to_id = 0
    cdef double weight = 0.0
    cdef int iweight = 0

    cdef int * nodes_begin_to = get_int_array_ptr(nodes.begin_to)
    cdef int * nodes_end_to = get_int_array_ptr(nodes.end_to)
    cdef int * nodes_self_w = get_int_array_ptr(nodes.self_w)
    cdef int * nodes_label = get_int_array_ptr(nodes.label)

    cdef int * links_ito = get_int_array_ptr(links.ito)
    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)
    cdef double * links_weight = get_double_array_ptr(links.weight)
    cdef double * links_suscept = get_double_array_ptr(links.suscept)

    cdef double * nodes_denominator_d = get_double_array_ptr(
                                                    nodes.denominator_d)
    cdef double * nodes_denominator_n = get_double_array_ptr(
                                                    nodes.denominator_n)

    # need to use C file reading as too slow in python
    f = filename.encode("UTF-8")
    cdef char* fname = f

    cdef FILE* cfile
    cfile = fopen(fname, "r")

    cdef int error_from = -1
    cdef int error_to = -1

    if cfile == NULL:
        raise FileNotFoundError(f"No such file or directory: {filename}")

    with nogil:
        while not feof(cfile):
            fscanf(cfile, "%d %d %lf\n", &from_id, &to_id, &weight)

            iweight = <int>weight

            if from_id == 0 or to_id == 0:
                error_from = from_id
                error_to = to_id
                break

            nlinks += 1

            if nlinks >= MAX_LINKS:
                break

            if from_id > nnodes:
                nnodes = from_id

            if to_id > nnodes:
                nnodes = to_id

            if nnodes >= MAX_NODES:
                break

            if nodes_label[from_id] == -1:
                nodes_label[from_id] = from_id
                nodes_begin_to[from_id] = nlinks
                nodes_end_to[from_id] = nlinks

            if from_id == to_id:
                nodes_self_w[from_id] = nlinks

            nodes_end_to[from_id] += 1

            links_ifrom[nlinks] = from_id
            links_ito[nlinks] = to_id
            links_weight[nlinks] = weight
            links_suscept[nlinks] = weight

            nodes_denominator_n[from_id] += weight
            nodes_denominator_d[to_id] += weight

        fclose(cfile)

    if nlinks >= MAX_LINKS or nnodes >= MAX_NODES:
        raise MemoryError(
            f"There are either too many links (>{nlinks}) or too many "
            f"wards (>{nnodes}) to fit into pre-allocated memory "
            f"(max_nodes = {MAX_NODES}, max_links = {MAX_LINKS}). "
            f"Increase these values and try to run again.")

    if error_from != -1 or error_to != -1:
        raise ValueError(f"{filename} is corrupted! "
                         f"Zero in link list: ${error_from}-${error_to}! "
                         f"Renumber files and start again")

    return (nodes, links, nnodes, nlinks)


_data_cache = {}


def build_wards_network(params: Parameters,
                        profiler: Profiler = None,
                        nthreads: int = 1,
                        max_nodes:int = 16384,
                        max_links:int = 4194304):
    """Creates a network of wards using the information provided in
       the file specified in parameters.input_files.work.

       The format of this should be:

        * Node_1 Node_2 weight 1-2
        * Node_3 Node_4 weight 3-4
        * Node_4 Node_1 weight 4-1
        * Node_2 Node_1 weight 2-1
        * ...

         BE CAREFUL!! Weights may not be symmetric, network is built with
         asymmetric links
    """
    global _data_cache

    # the network is solely determined by the work and play files
    work_and_play = f"{params.input_files.work}:{params.input_files.play}"

    from ._console import Console

    if work_and_play in _data_cache:
        Console.print("Using pre-loaded cached network...")
        network = _data_cache[work_and_play].copy()
        network.params = params
        return network

    if profiler is None:
        profiler = NullProfiler()

    p = profiler.start("build_wards_network")

    workfile = params.input_files.work


    p = p.start("read_work_file")
    if workfile in _data_cache:
        Console.print("Using pre-loaded cached work matrix...")
        (nodes, links, nnodes, nlinks) = _data_cache[workfile]
        nodes = nodes.copy()
        links = links.copy()

    else:
        try:
            (nodes, links,
             nnodes, nlinks) = _read_network(filename=workfile,
                                             max_nodes=max_nodes,
                                             max_links=max_links)
        except MemoryError as e:
            Console.print(f"Increasing max_nodes to {max_nodes*2} and "
                          f"max_links to {max_links*2}")
            return build_wards_network(params=params,
                                       profiler=profiler,
                                       nthreads=nthreads,
                                       max_nodes=max_nodes*2,
                                       max_links=max_links*2)

        _data_cache[workfile] = (nodes.copy(), links.copy(), nnodes, nlinks)
    p = p.stop()

    network = Network(nnodes=nnodes, nlinks=nlinks)

    network.nodes = nodes
    network.links = links

    Console.print(f"Number of nodes equals {nnodes}")
    Console.print(f"Number of links equals {nlinks}")

    # save the parameters used to build the network
    # within the network - this will save having to pass
    # them separately, which is error-prone
    network.params = params
    network.max_links = max_links
    network.max_nodes = max_nodes

    from . import fill_in_gaps
    p = p.start("fill_in_gaps")
    fill_in_gaps(network, max_nodes=max_nodes)
    p = p.stop()

    Console.print(f"Number of nodes after filling equals {network.nnodes}")

    from . import build_play_matrix
    p = p.start("build_play_matrix")
    build_play_matrix(network=network, profiler=p, max_nodes=max_nodes,
                      max_links=max_links)
    p = p.stop()

    # now finally go through all of the nodes and make sure that their
    # label is not -1
    cdef int nnull = 0
    cdef int nnodes_plus_one = network.nnodes + 1
    cdef int * nodes_label = get_int_array_ptr(nodes.label)
    cdef int i

    with nogil:
        for i in range(1, nnodes_plus_one):
            if nodes_label[i] == -1:
                nnull += 1
                nodes_label[i] = i

    if nnull > 0:
        Console.print(f"Number of null nodes equals {nnull}")

    Console.print(f"Number of nodes after build play equals {network.nnodes}")

    Console.print(f"Resize nodes to {network.nnodes + 1}")
    Console.print(f"Resize links to {network.nlinks + 1}")
    Console.print(f"Resize play links to {network.nplay + 1}")

    p = p.start("resize_nodes_and_links")
    network.nodes.resize(network.nnodes + 1)     # remember 1-indexed
    network.links.resize(network.nlinks + 1)  # remember 1-indexed
    network.play.resize(network.nplay + 1)      # remember 1-indexed
    p = p.stop()

    # cache this network for future use
    _data_cache[work_and_play] = network.copy()

    p.stop()

    return network
