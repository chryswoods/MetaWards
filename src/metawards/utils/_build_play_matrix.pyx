#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

from libc.stdio cimport FILE, fopen, fscanf, fclose, feof

from .._network import Network
from .._links import Links
from ._profiler import Profiler, NullProfiler

from ._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["build_play_matrix"]

def build_play_matrix(network: Network,
                      max_nodes: int, max_links: int,
                      profiler: Profiler=None):
    """Build the play matrix for the passed network"""
    if profiler is None:
        profiler = NullProfiler()

    p = profiler.start("build_play_matrix")

    params = network.params

    if params is None:
        return

    nodes = network.nodes

    p = p.start("allocate_memory")
    links = Links(network.max_links + 1)
    p = p.stop()

    cdef int nnodes_plus_one = network.nnodes + 1

    cdef int nlinks = 0
    cdef int j = 0
    cdef int from_id = 0
    cdef int to_id = 0
    cdef double weight = 0.0

    cdef int * nodes_label = get_int_array_ptr(nodes.label)
    cdef int * nodes_begin_p = get_int_array_ptr(nodes.begin_p)
    cdef int * nodes_end_p = get_int_array_ptr(nodes.end_p)
    cdef int * nodes_self_p = get_int_array_ptr(nodes.self_p)

    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)
    cdef int * links_ito = get_int_array_ptr(links.ito)
    cdef double * links_weight = get_double_array_ptr(links.weight)
    cdef double * links_suscept = get_double_array_ptr(links.suscept)

    cdef double * nodes_denominator_p = get_double_array_ptr(
                                                    nodes.denominator_p)
    cdef double * nodes_play_suscept = get_double_array_ptr(
                                                    nodes.play_suscept)

    cdef int error_from = -1
    cdef int error_to = -1

    cdef int MAX_LINKS = max_links
    cdef int MAX_NODES = max_nodes

    cdef char* fname
    cdef FILE* cfile

    # need to use C file reading as too slow in python
    if params.input_files.play is None:
        print("No play links file to read")
    else:
        p = p.start("read_play_file")
        filename = params.input_files.play.encode("UTF-8")
        fname = filename
        cfile = fopen(fname, "r")

        if cfile == NULL:
            raise FileNotFoundError(f"No such file or directory: {filename}")

        # resets the node label as a flag to check progress?
        with nogil:
            for j in range(1, nnodes_plus_one):
                nodes_label[j] = -1

            while not feof(cfile):
                fscanf(cfile, "%d %d %lf\n", &from_id, &to_id, &weight)

                nlinks += 1

                if nlinks >= MAX_LINKS:
                    break

                if from_id == 0 or to_id == 0:
                    error_from = from_id
                    error_to = to_id
                    break

                if nodes_label[from_id] == -1:
                    nodes_label[from_id] = from_id
                    nodes_begin_p[from_id] = nlinks
                    nodes_end_p[from_id] = nlinks

                if from_id == to_id:
                    nodes_self_p[from_id] = nlinks

                nodes_end_p[from_id] += 1

                links_ifrom[nlinks] = from_id
                links_ito[nlinks] = to_id
                links_weight[nlinks] = weight

                nodes_denominator_p[from_id] += weight
                nodes_play_suscept[from_id] += weight

            fclose(cfile)

        if nlinks >= MAX_LINKS:
            raise MemoryError(f"There are too many links (>{nlinks}) to fit "
                              f"into pre-allocated memory (max_links = "
                              f"{max_links}). Increase this and try again.")

        if error_from != -1 or error_to != -1:
            raise ValueError(f"{params.input_files.play} is corrupted. "
                             f"Zero in link list: ${error_from}-${error_to}! "
                             f"Renumber files and start again")

        p = p.stop()
    # end of if have playfile

    p = p.start("renormalise?")
    renormalise = (params.input_files.play == params.input_files.work)
    p = p.stop()

    if renormalise:
        print("Identical work and play links, so renormalising...")

    p = p.start("renormalise_loop")
    for j in range(1, nlinks+1):   # careful 1-indexed
        if renormalise:
            links_weight[j] /= nodes_denominator_p[links_ifrom[j]]

        links_suscept[j] = links_weight[j]
    p = p.stop()

    from . import fill_in_gaps
    p = p.start("fill_in_gaps")
    fill_in_gaps(network, max_nodes=max_nodes)
    p = p.stop()

    cdef int i1 = 0
    cdef int i2 = 0
    cdef double [::1] nodes_save_play_suscept = nodes.save_play_suscept

    cdef int max_node_id = network.nnodes

    if params.input_files.play_size is None:
        print("No play_size file to read")
    else:
        # need to use C file reading as too slow in python
        p = p.start("read_play_size_file")
        filename = params.input_files.play_size.encode("UTF-8")
        fname = filename
        cfile = fopen(fname, "r")

        if cfile == NULL:
            raise FileNotFoundError(f"No such file or directory: {filename}")

        try:
            while not feof(cfile):
                fscanf(cfile, "%d %d\n", &i1, &i2)

                if i1 > max_node_id:
                    max_node_id = i1

                nodes_play_suscept[i1] = i2
                nodes_denominator_p[i1] = i2
                nodes_save_play_suscept[i1] = i2

            fclose(cfile)
        except Exception as e:
            fclose(cfile)
            raise ValueError(f"{params.input_files.play_size} is corrupted or "
                            f"unreadable? Error = {e.__class__}: {e}")

        # we now need to fill in the missing nodes that are defined
        # in the play_size file, but were not linked to in the node
        # links file
        old_nnodes = network.nnodes

        if max_node_id >= max_nodes:
            raise MemoryError(f"Link ID {max_node_id} implies we have more "
                              f"nodes than are pre-allocated ({max_nodes}). "
                              f"Increase this and try again.")

        print(f"Adding missing nodes from {old_nnodes+1} to {max_node_id}")

        network.nnodes = max_node_id

        for i in range(old_nnodes, max_node_id+1):
            network.nodes.label[i] = i

        p = p.stop()
    # end of if play_size file

    print(f"Number of play links equals {nlinks}")

    network.nplay = nlinks
    network.play = links

    p.stop()
