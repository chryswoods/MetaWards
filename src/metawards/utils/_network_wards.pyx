
from .._network import Network
from .._parameters import Parameters
from .._disease import Disease
from .._wards import Wards
from .._ward import Ward
from .._nodes import Nodes
from .._links import Links

from ._console import Console
from ._profiler import Profiler
from ._get_array_ptr cimport get_int_array_ptr, get_double_array_ptr

__all__ = ["load_from_wards", "save_to_wards"]


def load_from_wards(wards: Wards, params: Parameters = None,
                    disease: Disease = None,
                    profiler: Profiler = None,
                    nthreads: int = 1) -> Network:
    """Build and return a Network from the passed set of Wards"""
    if profiler is None:
        from ._profiler import NullProfiler
        profiler = NullProfiler()

    if params is None:
        params = Parameters.load()

        if disease is None:
            disease = Disease.load()

        params.set_disease(disease, silent=True)
    else:
        if not isinstance(params, Parameters):
            raise TypeError(f"The parameters must be Parameters!")

        from copy import deepcopy
        params = deepcopy(params)

        if disease is not None:
            params.set_disease(disease, silent=True)

    from .._inputfiles import InputFiles
    params.input_files = InputFiles()

    cdef int i = 0
    cdef int node_id = 0
    cdef int nnodes_plus_one = len(wards)

    if nnodes_plus_one == 0:
        return Network()

    p = profiler.start("load_from_wards")

    nodes = Nodes(nnodes_plus_one)
    info = [None] * nnodes_plus_one
    worker_lists = [None] * nnodes_plus_one
    player_lists = [None] * nnodes_plus_one

    cdef int nlinks = 0
    cdef int nplay = 0

    cdef int * nodes_label = get_int_array_ptr(nodes.label)

    cdef int * nodes_begin_to = get_int_array_ptr(nodes.begin_to)
    cdef int * nodes_end_to = get_int_array_ptr(nodes.end_to)
    cdef int * nodes_self_w = get_int_array_ptr(nodes.self_w)

    cdef double * nodes_play_suscept = get_double_array_ptr(nodes.play_suscept)
    cdef double * nodes_save_play_suscept = get_double_array_ptr(
                                                nodes.save_play_suscept)

    cdef int * nodes_begin_p = get_int_array_ptr(nodes.begin_p)
    cdef int * nodes_end_p = get_int_array_ptr(nodes.end_p)
    cdef int * nodes_self_p = get_int_array_ptr(nodes.self_p)

    cdef double * nodes_x = get_double_array_ptr(nodes.x)
    cdef double * nodes_y = get_double_array_ptr(nodes.y)

    coords_type = None

    p = p.start("convert nodes")
    with Console.progress() as progress:
        task = progress.add_task("Constructing nodes", total=nnodes_plus_one)

        for i, ward in enumerate(wards._wards):
            if ward is None or ward.is_null():
                continue

            node_id = ward.id()

            if node_id <= 0 or node_id >= nnodes_plus_one:
                raise ValueError(f"Invalid ward.id() = {node_id}")

            pos = ward.position()

            if "x" in pos:
                if coords_type is None:
                    coords_type = "x/y"
                elif coords_type != "x/y":
                    raise ValueError(
                        "Cannot mix wards with X/Y and lat/long coordinates")

                nodes_x[node_id] = pos.get("x", 0.0)
                nodes_y[node_id] = pos.get("y", 0.0)

            elif "lat" in pos:
                if coords_type is None:
                    coords_type = "lat/long"
                elif coords_type != "lat/long":
                    raise ValueError(
                        "Cannot mix wards with X/Y and lat/long coordinates")

                nodes_x[node_id] = pos.get("lat", 0.0)
                nodes_y[node_id] = pos.get("long", 0.0)

            nodes_label[node_id] = ward.id()

            nodes_play_suscept[node_id] = <double>(ward.num_players())
            nodes_save_play_suscept[node_id] = nodes_play_suscept[node_id]

            info[node_id] = ward.info()

            l = ward.get_worker_lists()
            nlinks += len(l[0])

            worker_lists[node_id] = l

            l = ward.get_player_lists()
            nplay += len(l[0])

            player_lists[node_id] = l

            if i % 250 == 0:
                progress.update(task, completed=i)

        progress.update(task, completed=nnodes_plus_one, force_update=True)

    nodes.coordinates = coords_type

    p = p.stop()

    p = p.start("convert work links")

    links = Links(nlinks+1)

    cdef int ilink = 0

    cdef int * links_ito = get_int_array_ptr(links.ito)
    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)
    cdef double * links_suscept = get_double_array_ptr(links.suscept)
    cdef double * links_weight = get_double_array_ptr(links.weight)

    cdef int * dest
    cdef int * pop

    with Console.progress() as progress:
        task = progress.add_task("Constructing work links",
                                 total=nnodes_plus_one)

        for i, worker_list in enumerate(worker_lists):
            if worker_list is None or len(worker_list[0]) == 0:
                continue

            nodes_begin_to[i] = ilink + 1
            nodes_end_to[i] = nodes_begin_to[i] + len(worker_list[0])

            dest = get_int_array_ptr(worker_list[0])
            pop = get_int_array_ptr(worker_list[1])

            for j in range(0, len(worker_list[0])):
                ilink += 1
                links_ifrom[ilink] = i
                links_ito[ilink] = dest[j]
                links_weight[ilink] = <double>(pop[j])
                links_suscept[ilink] = links_weight[ilink]

                if i == dest[j]:
                    # this is the self-link
                    nodes_self_w[i] = ilink

            if i % 250 == 0:
                progress.update(task, completed=i)

        progress.update(task, completed=nnodes_plus_one, force_update=True)

    assert nlinks == ilink

    p = p.stop()

    p = p.start("convert play links")

    play = Links(nplay+1)

    cdef double * weight
    cdef int * play_ifrom = get_int_array_ptr(play.ifrom)
    cdef int * play_ito = get_int_array_ptr(play.ito)
    cdef double * play_suscept = get_double_array_ptr(play.suscept)
    cdef double * play_weight = get_double_array_ptr(play.weight)

    ilink = 0

    with Console.progress() as progress:
        task = progress.add_task("Constructing play links",
                                 total=nnodes_plus_one)

        for i, player_list in enumerate(player_lists):
            if player_list is None or len(player_list[0]) == 0:
                continue

            nodes_begin_p[i] = ilink + 1
            nodes_end_p[i] = nodes_begin_p[i] + len(player_list[0])

            dest = get_int_array_ptr(player_list[0])
            weight = get_double_array_ptr(player_list[1])

            for j in range(0, len(player_list[0])):
                ilink += 1
                play_ifrom[ilink] = i
                play_ito[ilink] = dest[j]
                play_weight[ilink] = weight[j]
                play_suscept[ilink] = play_weight[ilink]

                if i == dest[j]:
                    # this is the self-link
                    nodes_self_p[i] = ilink

            if i % 250 == 0:
                progress.update(task, completed=i)

        progress.update(task, completed=nnodes_plus_one, force_update=True)

    assert nplay == ilink

    p = p.stop()

    network = Network()
    network.params = params
    network.nodes = nodes
    network.nnodes = nnodes_plus_one - 1

    if network.nnodes >= network.max_nodes:
        network.max_nodes = network.nnodes + 1

    network.links = links
    network.nlinks = nlinks

    if network.nlinks >= network.max_links:
        network.max_links = network.nlinks + 1

    network.play = play
    network.nplay = nplay

    if network.nplay >= network.max_links:
        network.max_links = network.nplay + 1

    from .._wardinfo import WardInfos
    network.info = WardInfos(info)

    p = p.start("move_from_play_to_work")
    network.move_from_play_to_work(nthreads=nthreads, profiler=p)
    p = p.stop()

    from ._add_wards_network_distance import calc_network_distance
    calc_network_distance(network=network, nthreads=nthreads)

    (_mindist, maxdist) = network.get_min_max_distances(profiler=p,
                                                        nthreads=nthreads)

    network.params.dyn_dist_cutoff = maxdist + 1

    # By default, we initialise the network ready for a run,
    # namely make sure everything is reset and the population
    # is at work
    p = p.start("reset_everything")
    network.reset_everything(nthreads=nthreads, profiler=p)
    p = p.stop()

    p = p.start("rescale_play_matrix")
    network.rescale_play_matrix(nthreads=nthreads, profiler=p)
    p = p.stop()

    Console.print(f"**Network loaded. Population: {network.population}, "
                    f"Workers: {network.work_population}, Players: "
                    f"{network.play_population}**",
                    markdown=True)

    if network.work_population != wards.num_workers() or \
       network.play_population != wards.num_players():
        Console.error(
            f"Program bug: Disagreement between the number of "
            f"workers ({network.work_population} vs {wards.num_workers()}) "
            f"or players ({network.play_population} vs {wards.num_players()}) "
            f"which means that there is a data corruption somewhere...")

        raise AssertionError("Disagreement in population sizes")

    p = p.stop()

    return network


def save_to_wards(network: Network, profiler: Profiler = None,
                  nthreads: int = 1) -> Wards:
    """Build a return a set of Wards constructed from the passed Network"""
    if profiler is None:
        from ._profiler import NullProfiler
        profiler = NullProfiler()

    p = profiler.start("save_to_wards")

    nodes = network.nodes
    links = network.links
    play = network.play
    info = network.info

    cdef int * nodes_label = get_int_array_ptr(nodes.label)
    cdef double * nodes_save_play_suscept = get_double_array_ptr(
                                                    nodes.save_play_suscept)

    cdef double * nodes_x = get_double_array_ptr(nodes.x)
    cdef double * nodes_y = get_double_array_ptr(nodes.y)

    cdef int * links_ifrom = get_int_array_ptr(links.ifrom)
    cdef int * links_ito = get_int_array_ptr(links.ito)
    cdef double * links_weight = get_double_array_ptr(links.weight)

    cdef int * play_ifrom = get_int_array_ptr(play.ifrom)
    cdef int * play_ito = get_int_array_ptr(play.ito)
    cdef double * play_weight = get_double_array_ptr(play.weight)

    cdef int nnodes = network.nnodes
    cdef int nnodes_plus_one = nnodes + 1
    cdef int nlinks = len(links)
    cdef int nplay = len(play)

    cdef int have_info = 1 if (len(info) > 1) else 0
    cdef int have_coords = 0 if nodes.coordinates is None else 1
    cdef int xy_coords = 1 if nodes.coordinates == "x/y" else 0

    wards = [None]

    self_weight = [None] * nnodes_plus_one

    cdef int i = 0
    cdef int update_freq = 250
    cdef int ifrom, ito
    cdef double weight
    cdef double diff

    p = p.start("Convert wards")
    with Console.progress() as progress:
        task = progress.add_task("Extracting wards", total=nnodes_plus_one)

        for i in range(1, nnodes_plus_one):
            ward = Ward(id=nodes_label[i], auto_assign_players=False)

            if have_info:
                ward.set_info(info[i])

            if have_coords:
                if xy_coords:
                    ward.set_position(x=nodes_x[i], y=nodes_y[i], units="km")
                else:
                    ward.set_position(lat=nodes_x[i], long=nodes_y[i])

            ward.set_num_players(nodes_save_play_suscept[i])

            wards.append(ward)

            if i % update_freq == 0:
                progress.update(task, completed=i)

        progress.update(task, completed=nnodes_plus_one, force_update=True)
    p = p.stop()

    p = p.start("Convert work links")
    with Console.progress() as progress:
        task = progress.add_task("Extracting work links", total=nlinks)

        for i in range(0, nlinks):
            ifrom = links_ifrom[i]
            ito = links_ito[i]
            weight = links_weight[i]

            if ifrom == -1 or ito == -1:
                # null link
                continue

            if ito <= 0 or ito > nnodes or ifrom <=0 or ifrom > nnodes:
                Console.error(f"Invalid link? {ifrom}=>{ito}")

            if ifrom == ito and ifrom == 38:
                Console.print(f"ward {ifrom} {ito} => {weight}")

            wards[ifrom].add_workers(destination=ito, number=weight)

            if i % update_freq == 0:
                progress.update(task, completed=i+1)

        progress.update(task, completed=nlinks, force_update=True)
    p = p.stop()

    p = p.start("Convert play links")
    with Console.progress() as progress:
        task = progress.add_task("Extracting play links", total=nplay)

        for i in range(0, nplay):
            ifrom = play_ifrom[i]
            ito = play_ito[i]
            weight = play_weight[i]

            if ifrom == -1 or ito == -1:
                # null link
                continue

            if ito <= 0 or ito > nnodes or ifrom <=0 or ifrom > nnodes:
                Console.error(f"Invalid play link? {ifrom}=>{ito}")

            if ifrom == ito:
                self_weight[ifrom] = weight

            wards[ifrom].add_player_weight(destination=ito, weight=weight)

            if i % update_freq == 0:
                progress.update(task, completed=i+1)

        errors = []

        for i in range(1, nnodes_plus_one):
            weight = wards[i].get_players(destination=i)

            if self_weight[i] is None:
                # the weight should either be zero or one
                if weight > 0.5:
                    self_weight[i] = 1.0
                else:
                    self_weight[i] = 0.0

            diff = abs(self_weight[i] - weight)

            if diff > 1e-6:
                errors.append(
                    f"Ward {i} weight disagreement? {self_weight[i]} "
                    f"versus {weight}")

                if len(errors) > 10:
                    Console.error("Lots of errors! Exiting early!")
                    break

        if len(errors) > 0:
            Console.error("\n".join(errors))
            raise AssertionError("Disagreement in player weights")

        progress.update(task, completed=nlinks, force_update=True)
    p = p.stop()

    p = p.start("Create Wards")
    w = Wards()
    w.insert(wards, _need_deep_copy = False)
    wards = w

    p = p.stop()

    p = p.start("Assert sane")
    wards.assert_sane()

    if wards.num_workers() != network.work_population:
        errors.append(
            f"Disagreement in the number of workers: "
            f"{network.work_population} versus "
            f"{wards.num_workers()}")

    if wards.num_players() != network.play_population:
        errors.append(
            f"Disagreement in the number of players: "
            f"{network.play_population} versus "
            f"{wards.num_players()}")

    if len(errors) > 0:
        Console.error("\n".join(errors))
        raise AssertionError("Disagreement in size of the population")

    p = p.stop()

    p = p.stop()

    return wards

