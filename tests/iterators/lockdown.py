
def iterate_lockdown(network, population, **kwargs):
    from metawards.iterators import iterate_default

    advance_funcs = iterate_default(network=network,
                                    population=population, 
                                    **kwargs)

    start_day = 15+7      # (23rd March)
    duration = 184
    scale_uv = 0.2 / 2.8
    cutoff = 1.0          # 1.0 km
    end_day = start_day + duration

    if population.day > 22 and population.day <= end_day:
        # lockdown phase 1
        population.scale_uv = scale_uv
        network.params.dyn_dist_cutoff = cutoff
        print(f"\nLOCKDOWN: scale_uv = {scale_uv}, cutoff = {cutoff} km")

    return advance_funcs
