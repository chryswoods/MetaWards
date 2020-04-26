
def iterate_lockdown(network, population, **kwargs):
    from metawards.iterators import iterate_default

    advance_funcs = iterate_default(network=network,
                                    population=population, 
                                    **kwargs)

    # read parameters from custom user parameters
    params = network.params
    nstages = int(params.user_params["nstages"])

    start_day = int(params.user_params["start_day"])
    R0 = params.user_params["R0"]

    duration = params.user_params["duration"]
    scale_uv = params.user_params["scale_uv"]
    cutoff = params.user_params["cutoff"]

    day = population.day

    if day >= start_day:
        # in lockdown

        # which stage are we in?
        stage = 0
        scl = scale_uv[0] / R0
        cut = cutoff[0]

        end_day = start_day + int(duration[0])

        if day <= end_day:
            stage = 0
        else:
            for i in range(1,nstages):
                end_day += int(duration[i])
                scl = scale_uv[i] / R0
                cut = cutoff[i]

                if day <= end_day:
                    stage = i
                    break

            if day > end_day:
                print("Lockdown ended")
                scl = 1.0
                cut = 1000   # 1000 km

        population.scale_uv = scl
        params.dyn_dist_cutoff = cut
        print(f"\nLOCKDOWN {stage+1}: scale_uv = {scl}, cutoff = {cut} km")

    return advance_funcs
