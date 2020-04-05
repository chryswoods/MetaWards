
cimport cython
from libc.math cimport cos, pi
from  ._rate_to_prob cimport rate_to_prob

from ._network import Network
from ._parameters import Parameters
from ._profiler import Profiler, NullProfiler
from ._import_infection import import_infection

from ._ran_binomial cimport _ran_binomial, _get_binomial_ptr, binomial_rng

__all__ = ["iterate"]


@cython.boundscheck(False)
@cython.wraparound(False)
def iterate(network: Network, infections, play_infections,
            params: Parameters, rng, timestep: int,
            population: int, profiler: Profiler=None,
            is_dangerous=None,
            SELFISOLATE: bool = False,
            IMPORTS: bool = False):
    """Iterate the model forward one timestep (day) using the supplied
       network and parameters, advancing the supplied infections,
       and using the supplied random number generator (rng)
       to generate random numbers. This iterates for a normal
       (working) day (with predictable movements, mixed
       with random movements)

       If SELFISOLATE is True then you need to pass in
       is_dangerous, which should be an array("i", network.nnodes)
    """
    if profiler is None:
        profiler = NullProfiler()

    p = profiler.start("iterate")

    cdef binomial_rng* r = _get_binomial_ptr(rng)

    cdef double uv = params.UV
    cdef int ts = timestep

    #starting day = 41
    cdef double uvscale = (1.0-uv/2.0 + cos(2.0*pi*ts/365.0)/2.0)

    cdef double cutoff = params.dyn_dist_cutoff

    cdef double thresh = 0.01

    links = network.to_links
    wards = network.nodes
    plinks = network.play

    cdef int i = 0
    cdef double [::1] wards_day_foi = wards.day_foi
    cdef double [::1] wards_night_foi = wards.night_foi

    p = p.start("setup")
    for i in range(1, network.nnodes+1):
        wards_day_foi[i] = 0.0
        wards_night_foi[i] = 0.0

    p = p.stop()

    if IMPORTS:
        p = p.start("imports")
        imported = import_infection(network=network, infections=infections,
                                    play_infections=play_infections,
                                    params=params, rng=rng,
                                    population=population)

        print(f"Day: {timestep} Imports: expected {params.daily_imports} "
              f"actual {imported}")
        p = p.stop()

    cdef int N_INF_CLASSES = len(infections)
    cdef double scl_foi_uv = 0.0
    cdef double contrib_foi = 0.0
    cdef double beta = 0.0
    cdef play_at_home_scl = 0.0

    cdef int j = 0
    cdef int k = 0
    cdef int l = 0
    cdef int inf_ij = 0
    cdef double weight = 0.0
    cdef double distance = 0.0
    cdef double [::1] links_weight = links.weight
    cdef int [::1] links_ifrom = links.ifrom
    cdef int [::1] links_ito = links.ito
    cdef int ifrom = 0
    cdef int ito = 0
    cdef int staying, moving, play_move, end_p
    cdef double [::1] links_distance = links.distance
    cdef double frac = 0.0
    cdef double cumulative_prob, prob_scaled
    cdef double too_ill_to_move

    cdef int [::1] wards_begin_p = wards.begin_p
    cdef int [::1] wards_end_p = wards.end_p

    cdef double [::1] plinks_distance = plinks.distance
    cdef double [::1] plinks_weight = plinks.weight
    cdef int [::1] plinks_ifrom = plinks.ifrom
    cdef int [::1] plinks_ito = plinks.ito

    cdef double [::1] wards_denominator_d = wards.denominator_d
    cdef double [::1] wards_denominator_n = wards.denominator_n
    cdef double [::1] wards_denominator_p = wards.denominator_p
    cdef double [::1] wards_denominator_pd = wards.denominator_pd

    cdef double [::1] links_suscept = links.suscept
    cdef double [::1] wards_play_suscept = wards.play_suscept

    cdef int [::1] wards_label = wards.label

    cdef int [::1] infections_i, play_infections_i

    cdef int [::1] is_dangerous_array

    cdef int cSELFISOLATE = 0

    if SELFISOLATE:
        cSELFISOLATE = 1
        is_dangerous_array = is_dangerous

    p = p.start("loop_over_classes")
    for i in range(0, N_INF_CLASSES):
        contrib_foi = params.disease_params.contrib_foi[i]
        beta = params.disease_params.beta[i]
        scl_foi_uv = contrib_foi * beta * uvscale
        too_ill_to_move = params.disease_params.too_ill_to_move[i]

        # number of people staying gets bigger as
        # PlayAtHome increases
        play_at_home_scl = <double>(params.dyn_play_at_home *
                                    too_ill_to_move)

        infections_i = infections[i]
        play_infections_i = play_infections[i]

        if contrib_foi > 0:
            p = p.start(f"work_{i}")
            for j in range(1, network.nlinks+1):
                # deterministic movements (e.g. to work)
                inf_ij = infections_i[j]
                if inf_ij > 0:
                    weight = links_weight[j]
                    ifrom = links_ifrom[j]
                    ito = links_ito[j]

                    if inf_ij > weight:
                        print(f"inf[{i}][{j}] {inf_ij} > links[j].weight "
                              f"{weight}")

                    if links_distance[j] < cutoff:
                        if cSELFISOLATE:
                            frac = is_dangerous_array[ito] / (
                                                wards_denominator_d[ito] +
                                                wards_denominator_p[ito])

                            if frac > thresh:
                                staying = infections_i[j]
                            else:
                                # number staying - this is G_ij
                                staying = _ran_binomial(r,
                                                        too_ill_to_move,
                                                        inf_ij)
                        else:
                            # number staying - this is G_ij
                            staying = _ran_binomial(r,
                                                    too_ill_to_move,
                                                    inf_ij)

                        if staying < 0:
                            print(f"staying < 0")

                        # number moving, this is I_ij - G_ij
                        moving = inf_ij - staying

                        wards_day_foi[ifrom] += staying * scl_foi_uv

                        # Daytime Force of
                        # Infection is proportional to
                        # number of people staying
                        # in the ward (too ill to work)
                        # this is the sum for all G_ij (including g_ii

                        wards_day_foi[ito] += moving * scl_foi_uv

                        # Daytime FOI for destination is incremented (including self links, I_ii)
                    else:
                        # outside cutoff
                        wards_day_foi[ifrom] += inf_ij * scl_foi_uv

                    wards_night_foi[ifrom] += inf_ij * scl_foi_uv

                    # Nighttime Force of Infection is
                    # prop. to the number of Infected individuals
                    # in the ward
                    # This I_ii in Lambda^N

                # end of if inf_ij (are there any new infections)
            # end of infectious class loop
            p = p.stop()

            p = p.start(f"play_{i}")
            for j in range(1, network.nnodes+1):
                # playmatrix loop FOI loop (random/unpredictable movements)
                inf_ij = play_infections_i[j]
                if inf_ij > 0:
                    wards_night_foi[j] += inf_ij * scl_foi_uv

                    staying = _ran_binomial(r, play_at_home_scl, inf_ij)

                    if staying < 0:
                        print(f"staying < 0")

                    moving = inf_ij - staying

                    cumulative_prob = 0.0
                    k = wards_begin_p[j]

                    end_p = wards_end_p[j]

                    while (moving > 0) and (k < end_p):
                        # distributing people across play wards
                        if plinks_distance[k] < cutoff:
                            weight = plinks_weight[k]
                            ifrom = plinks_ifrom[k]
                            ito = plinks_ito[k]

                            prob_scaled = weight / (1.0 - cumulative_prob)
                            cumulative_prob += weight

                            play_move = _ran_binomial(r, prob_scaled, moving)

                            if cSELFISOLATE:
                                frac = is_dangerous_array[ito] / (
                                                wards_denominator_d[ito] +
                                                wards_denominator_p[ito])

                                if frac > thresh:
                                    staying += play_move
                                else:
                                    wards_day_foi[ito] += play_move * scl_foi_uv
                            else:
                                wards_day_foi[ito] += play_move * scl_foi_uv

                            moving -= play_move
                        # end of if within cutoff

                        k += 1
                    # end of while loop

                    wards_day_foi[j] += (moving + staying) * scl_foi_uv
                # end of if inf_ij (there are new infections)

            # end of loop over all nodes
            p = p.stop()
        # end of params.disease_params.contrib_foi[i] > 0:
    p = p.stop()
    # end of loop over all disease classes

    cdef int [::1] infections_i_plus_one, play_infections_i_plus_one
    cdef double disease_progress = 0.0

    p = p.start("recovery")
    for i in range(N_INF_CLASSES-2, -1, -1):  # loop down to 0
        # recovery, move through classes backwards
        infections_i = infections[i]
        infections_i_plus_one = infections[i+1]
        play_infections_i = play_infections[i]
        play_infections_i_plus_one = play_infections[i+1]
        disease_progress = params.disease_params.progress[i]

        for j in range(1, network.nlinks+1):
            inf_ij = infections_i[j]

            if inf_ij > 0:
                l = _ran_binomial(r, disease_progress, inf_ij)

                if l > 0:
                    infections_i_plus_one[j] += l
                    infections_i[j] -= l

            elif inf_ij != 0:
                print(f"inf_ij problem {i} {j} {inf_ij}")

        for j in range(1, network.nnodes+1):
            inf_ij = play_infections_i[j]

            if inf_ij > 0:
                l = _ran_binomial(r, disease_progress, inf_ij)

                if l > 0:
                    play_infections_i_plus_one[j] += l
                    play_infections_i[j] -= l

            elif inf_ij != 0:
                print(f"play_inf_ij problem {i} {j} {inf_ij}")
    # end of recovery loop
    p = p.stop()

    cdef double length_day = params.length_day
    cdef double rate, inf_prob

    # i is set to 0 now as we are only dealing now with new infections
    i = 0
    infections_i = infections[i]
    play_infections_i = play_infections[i]

    p = p.start("fixed")
    for j in range(1, network.nlinks+1):
        # actual new infections for fixed movements
        inf_prob = 0

        distance = links_distance[j]

        if distance < cutoff:
            # distance is below cutoff (reasonable distance)
            # infect in work ward
            ifrom = links_ifrom[j]
            ito = links_ito[j]

            if wards_day_foi[ito] > 0:
                # daytime infection of link j
                if cSELFISOLATE:
                    frac = is_dangerous_array[ito] / (
                                            wards_denominator_d[ito] +
                                            wards_denominator_p[ito])

                    if frac > thresh:
                        inf_prob = 0.0
                    else:
                        rate = (length_day * wards_day_foi[ito]) / (
                                            wards_denominator_d[ito] +
                                            wards_denominator_pd[ito])

                        inf_prob = rate_to_prob(rate)
                else:
                    rate = (length_day * wards_day_foi[ito]) / (
                                            wards_denominator_d[ito] +
                                            wards_denominator_pd[ito])

                    inf_prob = rate_to_prob(rate)

            # end of if wards.day_foi[ito] > 0
        # end of if distance < cutoff
        elif wards_day_foi[ifrom] > 0:
            # if distance is too large then infect in home ward with day FOI
            rate = (length_day * wards_day_foi[ifrom]) / (
                                            wards_denominator_d[ifrom] +
                                            wards_denominator_pd[ifrom])

            inf_prob = rate_to_prob(rate)

        if inf_prob > 0.0:
            # daytime infection of workers
            l = _ran_binomial(r, inf_prob, <int>(links_suscept[j]))

            if l > 0:
                # actual infection
                #print(f"InfProb {inf_prob}, susc {links.suscept[j]}, l {l}")
                infections_i[j] += l
                links_suscept[j] -= l

        if wards_night_foi[ifrom] > 0:
            # nighttime infection of workers
            rate = (1.0 - length_day) * (wards_night_foi[ifrom]) / (
                                            wards_denominator_n[ifrom] +
                                            wards_denominator_p[ifrom])

            inf_prob = rate_to_prob(rate)

            l = _ran_binomial(r, inf_prob, <int>(links_suscept[j]))

            if l > links_suscept[j]:
                print(f"l > links[{j}].suscept {links_suscept[j]} nighttime")

            if l > 0:
                # actual infection
                # print(f"NIGHT InfProb {inf_prob}, susc {links.suscept[j]}, {l}")
                infections_i[j] += l
                links_suscept[j] -= l
        # end of wards.night_foi[ifrom] > 0  (nighttime infections)
    # end of loop over all network links
    p = p.stop()

    cdef int suscept = 0
    cdef double dyn_play_at_home = params.dyn_play_at_home

    p = p.start("play")
    for j in range(1, network.nnodes+1):
        # playmatrix loop
        inf_prob = 0.0

        suscept = <int>wards_play_suscept[j]

        if suscept < 0:
            print(f"play_suscept is less than 0 ({suscept}) "
                  f"problem {j}, {wards_label[j]}")

        staying = _ran_binomial(r, dyn_play_at_home, suscept)

        moving = suscept - staying

        cumulative_prob = 0.0

        # daytime infection of play matrix moves
        for k in range(wards_begin_p[j], wards_end_p[j]):
            if plinks_distance[k] < cutoff:
                ito = plinks_ito[k]

                if wards_day_foi[ito] > 0.0:
                    weight = plinks_weight[k]
                    prob_scaled = weight / (1.0-cumulative_prob)
                    cumulative_prob += weight

                    if cSELFISOLATE:
                        frac = is_dangerous_array[ito] / (
                                                wards_denominator_p[ito] +
                                                wards_denominator_d[ito])

                        if frac > thresh:
                            inf_prob = 0.0
                            play_move = 0
                        else:
                            play_move = _ran_binomial(r, prob_scaled, moving)
                            frac = (length_day * wards_day_foi[ito]) / (
                                                 wards_denominator_pd[ito] +
                                                 wards_denominator_d[ito])

                            inf_prob = rate_to_prob(frac)
                    else:
                        play_move = _ran_binomial(r, prob_scaled, moving)
                        frac = (length_day * wards_day_foi[ito]) / (
                                                 wards_denominator_pd[ito] +
                                                 wards_denominator_d[ito])

                        inf_prob = rate_to_prob(frac)

                    l = _ran_binomial(r, inf_prob, play_move)

                    moving -= play_move

                    if l > 0:
                        # infection
                        #print(f"PLAY: InfProb {inf_prob}, susc {play_move}, "
                        #      f"l {l}")
                        #print(f"daytime play_infections[{i}][{j}] += {l}")
                        play_infections_i[j] += l
                        wards_play_suscept[j] -= l

                # end of DayFOI if statement
            # end of Dynamics Distance if statement
        # end of loop over links of wards[j]

        if (staying + moving) > 0:
            # infect people staying at home
            frac = (length_day * wards_day_foi[j]) / (
                                        wards_denominator_pd[j] +
                                        wards_denominator_d[j])

            inf_prob = rate_to_prob(frac)

            l = _ran_binomial(r, inf_prob, staying+moving)

            if l > 0:
                # another infections, this time from home
                #print(f"staying home play_infections[{i}][{j}] += {l}")
                play_infections_i[j] += l
                wards_play_suscept[j] -= l

        # nighttime infections of play movements
        night_foi = wards_night_foi[j]
        if night_foi > 0.0:
            frac = ((1.0 - length_day) * night_foi) / (
                            wards_denominator_n[j] + wards_denominator_p[j])

            inf_prob = rate_to_prob(frac)

            l = _ran_binomial(r, inf_prob, <int>(wards_play_suscept[j]))

            if l > 0:
                # another infection
                #print(f"nighttime play_infections[{i}][{j}] += {l}")
                play_infections_i[j] += l
                wards_play_suscept[j] -= l
    # end of loop over wards (nodes)
    p = p.stop()

    p.stop()
