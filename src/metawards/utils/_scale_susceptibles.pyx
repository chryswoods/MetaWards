#!/bin/env/python3
#cython: linetrace=False
# MUST ALWAYS DISABLE AS WAY TOO SLOW FOR ITERATE

from typing import List as _List

from libc.math cimport floor
from libc.stdint cimport uintptr_t

from .._nodes import Nodes
from .._links import Links
from .._network import Network
from .._demographics import Demographics
from ._profiler import Profiler

from ._get_array_ptr cimport get_double_array_ptr, get_int_array_ptr
from ._array import create_double_array, create_int_array

from ._ran_binomial cimport _ran_binomial, _ran_integer, \
                            _get_binomial_ptr, binomial_rng

__all__ = ["scale_node_susceptibles", "scale_link_susceptibles",
           "distribute_remainders"]


cdef inline double scale_and_round(double value, double scale) nogil:
    if scale > 0.5:
        # round up for large scales, as smaller scales will always
        # round down
        return floor((value * scale) + 0.5)
    else:
        # rounding down - hopefully this will minimise the number
        # of values that need to be redistributed
        return floor(value * scale)


def scale_node_susceptibles(nodes: Nodes, ratio: any = None,
                            work_ratio: any = None, play_ratio: any = None):
    """Scale the number of susceptibles in the passed Nodes
        by the passed scale ratios. These can be values, e.g.
        ratio = 2.0 will scale the total number of susceptibles
        in each ward by 2.0. They can also be lists of values,
        where ward[i] will be scaled by ratio[i]. They can also
        be dictionaries, e.g. ward[i] scaled by ratio[i]

        Parameters
        ----------
        nodes: Nodes
            The nodes whose susceptible population will be scaled
        ratio: None, float, list or dict
            The amount by which to scale the total population of
            susceptibles - evenly scales the work and play populations
        work_ratio: None, float, list or dict
            Scale only the work population of susceptibles
        play_ratio: None, float, list or dict
            Scale only the play population of susceptibles

        Returns
        -------
        None
    """

    if ratio is not None:
        work_ratio = ratio
        play_ratio = ratio

    if play_ratio is None:
        return

    if nodes is None or len(nodes) == 0:
        return

    try:
        play_ratio = float(play_ratio)
    except Exception:
        pass

    cdef double * nodes_play_suscept = get_double_array_ptr(
                                                nodes.play_suscept)
    cdef double * nodes_save_play_suscept = get_double_array_ptr(
                                                nodes.save_play_suscept)

    cdef int i = 0
    cdef int nnodes_plus_one = len(nodes)   # this will already
                                            # be the 1-indexed size

    cdef double v = 0.0
    cdef double val = 0.0

    if isinstance(play_ratio, float):
        if play_ratio == 1.0:
            return

        # scale all equally
        v = play_ratio

        for i in range(1, nnodes_plus_one):
            val = scale_and_round(nodes_save_play_suscept[i], v)
            nodes_play_suscept[i] = val
            nodes_save_play_suscept[i] = val

    elif isinstance(play_ratio, dict):
        # scale only the specified nodes
        for key, value in play_ratio.items():
            v = value
            val = scale_and_round(nodes_save_play_suscept[key], v)
            nodes_play_suscept[key] = val
            nodes_save_play_suscept[key] = val

    elif isinstance(play_ratio, list):
        if len(play_ratio) != len(nodes) - 1:
            raise ValueError(
                f"The list of play_ratio scale factors ({len(play_ratio)}) "
                f"must equal the number of nodes ({len(nodes)-1})")

        for i in range(1, nnodes_plus_one):
            v = play_ratio[i]
            val = scale_and_round(nodes_save_play_suscept[i], v)
            nodes_play_suscept[i] = val
            nodes_save_play_suscept[i] = val

    else:
        raise NotImplementedError(
                f"Cannot scale the nodes by a {play_ratio.__class__}")


def scale_link_susceptibles(links: Links, ratio: any):
    """Scale the number of susceptibles in the passed Links
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

    if ratio is None:
        return

    if links is None or len(links) == 0:
        return

    try:
        ratio = float(ratio)
    except Exception:
        pass

    cdef double * links_weight = get_double_array_ptr(links.weight)
    cdef double * links_suscept = get_double_array_ptr(links.suscept)
    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)

    cdef int i = 0
    cdef int nlinks_plus_one = len(links)  # already 1-indexed size
    cdef int ifrom = 0
    cdef double v = 0.0
    cdef double val = 0

    if isinstance(ratio, float):
        if ratio == 1.0:
            return

        # scale all equally
        v = ratio

        for i in range(1, nlinks_plus_one):
            val = scale_and_round(links_weight[i], v)
            links_weight[i] = val
            links_suscept[i] = val

    elif isinstance(ratio, dict):
        # scale only links originating from specific nodes
        for i in range(1, nlinks_plus_one):
            ifrom = links_ifrom[i]

            v = ratio.get(ifrom, 1.0)

            if v != 1.0:
                val = scale_and_round(links_weight[i], v)
                links_weight[i] = val
                links_suscept[i] = val

    elif isinstance(ratio, list):
        # scale the links originating from the specified nodes
        # (the size of this list has already been checked in
        # the nodes equivalent of this function)
        for i in range(1, nlinks_plus_one):
            ifrom = links_ifrom[i]

            v = ratio[ifrom]

            if v != 1.0:
                val = scale_and_round(links_weight[i], v)
                links_weight[i] = val
                links_suscept[i] = val


cdef double redistribute(double target, double *values,
                         int nvalues, binomial_rng *rng,
                         int *allow_extras) nogil:
    """This will add or subtract numbers from 'values' until their sum
       equals 'target'
    """
    cdef double diff = target

    cdef int i = 0

    for i in range(0, nvalues):
        diff = diff - values[i]

    if diff > 0:
        while diff > 0:
            i = _ran_integer(rng, 0, nvalues)
            if allow_extras[i]:
                values[i] += 1
                diff -= 1
    elif diff < 0:
        while diff < 0:
            i = _ran_integer(rng, 0, nvalues)
            if allow_extras[i]:
                values[i] -= 1
                diff += 1

    return diff


def distribute_remainders(network: Network,
                          subnets: _List[Network],
                          demographics: Demographics,
                          random_seed: int = None,
                          nthreads: int = 1,
                          profiler: Profiler=None) -> None:
    """Distribute the remainder of the population in each ward and link from
       'network' who are not represented in any of the demographic
       sub-networks in subnets. This uses a completely random algorithm
       that adds to random demographics one by one until all of the
       population is assigned

       Parameters
       ----------
       network: Network
         The overall network
       subnets: List[Network]
         The demographic sub-networks
       random_seed: int
         Random seed to use to seed the random number generator that
         decides where to allocate rounded individuals
    """

    from cython.parallel import parallel, prange

    if profiler is None:
        from ._profiler import NullProfiler
        profiler = NullProfiler()

    nodes = network.nodes
    links = network.links

    cdef int i = 0
    cdef int nnodes_plus_one = network.nnodes + 1
    cdef int nlinks_plus_one = network.nlinks + 1

    cdef int nsubnets = len(subnets)

    cdef int n = 0
    cdef int sub_n = 0
    cdef int diff = 0

    cdef int num_threads = nthreads

    cdef double * nodes_play_suscept = get_double_array_ptr(
                                                nodes.play_suscept)
    cdef double * nodes_save_play_suscept = get_double_array_ptr(
                                                nodes.save_play_suscept)

    cdef double * sub_nodes_play_suscept
    cdef double * sub_nodes_save_play_suscept

    cdef double * links_weight = get_double_array_ptr(links.weight)
    cdef double * links_suscept = get_double_array_ptr(links.suscept)

    cdef double * sub_links_weight
    cdef double * sub_links_suscept

    diff_nodes = create_double_array(nnodes_plus_one)
    diff_links = create_double_array(nlinks_plus_one)

    cdef double * diff_nodes_array = get_double_array_ptr(diff_nodes)
    cdef double * diff_links_array = get_double_array_ptr(diff_links)

    cdef double target = 0.0
    values = create_double_array(nsubnets)
    cdef double * values_array = get_double_array_ptr(values)

    # calculate the number of remainders in each ward and link
    p = profiler.start("initialise")
    with nogil, parallel(num_threads=num_threads):
        for i in prange(1, nnodes_plus_one, schedule="static"):
            diff_nodes_array[i] = nodes_save_play_suscept[i]

        for i in prange(1, nlinks_plus_one, schedule="static"):
            diff_links_array[i] = links_weight[i]
    p = p.stop()

    p = p.start("calc_differences")
    for subnet in subnets:
        sub_nodes_save_play_suscept = get_double_array_ptr(
                                        subnet.nodes.save_play_suscept)
        sub_links_weight = get_double_array_ptr(subnet.links.weight)

        with nogil, parallel(num_threads=num_threads):
            for i in prange(1, nnodes_plus_one, schedule="static"):
                diff_nodes_array[i] = diff_nodes_array[i] - \
                                      sub_nodes_save_play_suscept[i]

            for i in prange(1, nlinks_plus_one, schedule="static"):
                diff_links_array[i] = diff_links_array[i] - \
                                      sub_links_weight[i]
    p = p.stop()

    # go through and take action on all of the differences. These differences
    # are rounding issues, e.g. dividing 5 people evenly between 2
    # demographics is not possible - we will assign 2 people to each
    # demographic, and would have 1 remainder. To solve this we could
    # either

    # 1. assign the person to the first demographic, or
    # 2. assign the person to the largest demographic, or
    # 3. assign the person to the smallest demographic, or
    # 4. assign the person to a random demographic

    # Solutions 1-3 have major issues that, because this happens for each
    # of the 1 million+ wards, we get massive biases to the first, or
    # largest, or smallest demographics (e.g. if this happens in all wards
    # then the "chosen" demographic has >1m more members than would be
    # expected). The solution appears to be that we assign randomly,
    # as, on average, the additions will occur to demographics evenly,
    # and so shouldn't affect their relative sizes.

    # HOWEVER, when we run multiple runs, we need the initial assignment
    # of population to demographics to be the same, otherwise this can
    # be a major confounding factor. What we need is for every time
    # MetaWards is run, that the same decision is taken about how to
    # round, and thus the same distribution of population amongst
    # demographics is each ward is made. The only way to achieve this
    # is to use a semi-random algorithm, i.e. we use random number
    # generator with a fixed random number seed to make the decisions.

    # While I don't like this, in most production use there will be
    # real data on the demographic splits, and so real, rather than
    # rounded values will be used and this algorithm will not be needed.

    from ._ran_binomial import seed_ran_binomial
    if random_seed is None:
        random_seed = 4751828

    from ._console import Console

    Console.print(
        f"Seeding generator used for demographics with seed {random_seed}")
    bin_rng = seed_ran_binomial(random_seed)

    cdef binomial_rng* rng = _get_binomial_ptr(bin_rng)

    allow_workers = create_int_array(len(demographics))
    allow_players = create_int_array(len(demographics))

    cdef int * allow_workers_ptr = get_int_array_ptr(allow_workers)
    cdef int * allow_players_ptr = get_int_array_ptr(allow_players)

    for i, demographic in enumerate(demographics):
        allow_workers[i] = int(demographic.work_ratio != 0)
        allow_players[i] = int(demographic.play_ratio != 0)

    p = p.start("distribute_nodes")
    with nogil:
        for i in range(1, nnodes_plus_one):
            if diff_nodes_array[i] != 0.0:
                target = nodes_save_play_suscept[i]

                for j in range(0, nsubnets):
                    with gil:
                        sub_nodes_save_play_suscept = get_double_array_ptr(
                                            subnets[j].nodes.save_play_suscept)

                    values_array[j] = sub_nodes_save_play_suscept[i]

                diff_nodes_array[i] = redistribute(target, values_array,
                                                   nsubnets, rng,
                                                   allow_players_ptr)

                for j in range(0, nsubnets):
                    with gil:
                        sub_nodes_save_play_suscept = get_double_array_ptr(
                                            subnets[j].nodes.save_play_suscept)
                        sub_nodes_play_suscept = get_double_array_ptr(
                                            subnets[j].nodes.play_suscept)

                    sub_nodes_save_play_suscept[i] = values_array[j]
                    sub_nodes_play_suscept[i] = values_array[j]
    p = p.stop()

    p = p.start("distribute_links")
    with nogil:
        for i in range(1, nlinks_plus_one):
            if diff_links_array[i] != 0.0:
                target = links_weight[i]

                for j in range(0, nsubnets):
                    with gil:
                        sub_links_weight = get_double_array_ptr(
                                                    subnets[j].links.weight)

                    values_array[j] = sub_links_weight[i]

                diff_links_array[i] = redistribute(target, values_array,
                                                   nsubnets, rng,
                                                   allow_workers_ptr)

                for j in range(0, nsubnets):
                    with gil:
                        sub_links_weight = get_double_array_ptr(
                                                    subnets[j].links.weight)
                        sub_links_suscept = get_double_array_ptr(
                                                    subnets[j].links.suscept)

                    sub_links_weight[i] = values_array[j]
                    sub_links_suscept[i] = values_array[j]
    p = p.stop()

    Console.print(
        f"Number of differences is {sum(diff_nodes)} + {sum(diff_links)}")
