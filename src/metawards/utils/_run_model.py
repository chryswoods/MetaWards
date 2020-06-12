
from typing import Union as _Union

from .._network import Network
from .._networks import Networks
from .._infections import Infections
from .._outputfiles import OutputFiles
from .._workspace import Workspace
from .._population import Population, Populations
from ._profiler import Profiler
from ._get_functions import get_initialise_functions, \
    get_model_loop_functions, \
    get_finalise_functions, \
    MetaFunction, \
    accepts_stage

__all__ = ["run_model"]


def run_model(network: _Union[Network, Networks],
              infections: Infections,
              rngs,
              output_dir: OutputFiles,
              population: Population = Population(initial=57104043),
              nsteps: int = None,
              profiler: Profiler = None,
              nthreads: int = None,
              iterator: _Union[str, MetaFunction] = None,
              extractor: _Union[str, MetaFunction] = None,
              mixer: _Union[str, MetaFunction] = None,
              mover: _Union[str, MetaFunction] = None) -> Populations:
    """Actually run the model... Real work happens here. The model
       will run until completion or until 'nsteps' have been
       completed, whichever happens first.

       Parameters
       ----------
       network: Network or Networks
            The network(s) on which to run the model
       infections: Infections
            The space used to record the infections
       rngs: list
            The list of random number generators to use, one per thread
       population: Population
            The initial population at the start of the model outbreak.
            This is also used to set the date and day of the start of
            the model outbreak
       seed: int
            The random number seed used for this model run. If this is
            None then a very random random number seed will be used
       output_dir: OutputFiles
            The directory to write all of the output into
       nsteps: int
            The maximum number of steps to run in the outbreak. If None
            then run until the outbreak has finished
       profiler: Profiler
            The profiler to use to profile - a new one is created if
            one isn't passed
       nthreads: int
            Number of threads over which to parallelise this model run
       iterator: MetaFunction or string
            Function that will be used to dynamically get the functions
            that will be used at each iteration to advance the
            model. Any additional files or parameters needed by these
            functions should be included in the `network.params` object.
       extractor: MetaFunction or string
            Function that will be used to dynamically get the functions
            that will be used at each iteration to extract data from
            the model run
       mixer: MetaFunction or string
            Function that will mix data from multiple demographics
            so that this is shared during a model run
       mover: MetaFunction or string
            Function that can move the population between different
            demographics

       Returns
       -------
       trajectory: Populations
            The trajectory of the population for every day of the model run
    """
    if iterator is None:
        from ..iterators._iterate_default import iterate_default
        iterator = iterate_default
    elif isinstance(iterator, str) or not accepts_stage(iterator):
        from ..iterators._iterate_custom import build_custom_iterator
        iterator = build_custom_iterator(iterator, __name__)

    if extractor is None:
        from ..extractors._extract_default import extract_default
        extractor = extract_default
    elif isinstance(extractor, str) or not accepts_stage(extractor):
        from ..extractors._extract_custom import build_custom_extractor
        extractor = build_custom_extractor(extractor, __name__)

    if mixer is None:
        from ..mixers._mix_default import mix_default
        mixer = mix_default
    elif isinstance(mixer, str) or not accepts_stage(mixer):
        from ..mixers._mix_custom import build_custom_mixer
        mixer = build_custom_mixer(mixer, __name__)

    if mover is None:
        from ..movers._move_default import move_default
        mover = move_default
    elif isinstance(mover, str) or not accepts_stage(mover):
        from ..movers._move_custom import build_custom_mover
        mover = build_custom_mover(mover, __name__)

    if profiler is None:
        from ._profiler import NullProfiler
        profiler = NullProfiler()

    p = profiler.start("run_model")

    params = network.params

    if params is None:
        return population

    from copy import deepcopy
    population = deepcopy(population)

    # create space to hold the population trajectory
    trajectory = Populations()

    p = p.start("clear_all_infections")
    infections.clear(nthreads=nthreads)
    p = p.stop()

    # create a workspace that is used as part of the "analyse" stage to
    # provide a scratch-pad while extracting data from the model
    workspace = Workspace.build(network=network)

    # get and call all of the functions that need to be called to
    # initialise the model run
    p = p.start("initialise_funcs")
    funcs = get_initialise_functions(network=network, population=population,
                                     infections=infections,
                                     output_dir=output_dir,
                                     workspace=workspace, rngs=rngs,
                                     iterator=iterator, extractor=extractor,
                                     mixer=mixer, mover=mover,
                                     nthreads=nthreads, profiler=p)

    # setup takes place on "day 0"
    from ._console import Console
    Console.rule(f"Day {population.day}", style="iteration")

    for func in funcs:
        p = p.start(str(func))
        func(network=network, population=population,
             infections=infections, output_dir=output_dir,
             workspace=workspace, rngs=rngs, nthreads=nthreads,
             profiler=p)
        p = p.stop()

    p = p.stop()

    infecteds = population.infecteds

    # save the initial population
    trajectory.append(population)

    p = p.start("run_model_loop")
    iteration_count = 0

    # keep looping until the outbreak is over or until we have completed
    # at least 5 loop iterations
    while (infecteds != 0) or (iteration_count < 5):
        # construct a new profiler of the same type as 'profiler'
        p2 = profiler.__class__()

        # increment the day at the beginning, before anything happens.
        # This way, the statistics for "day 1" are everything that
        # happened since the end of day 0 and the end of day 1
        population.increment_day()

        p2 = p2.start(f"timing for day {population.day}")

        Console.rule(f"Day {population.day}", style="iteration")

        start_population = population.population

        funcs = get_model_loop_functions(
            network=network, population=population,
            infections=infections,
            output_dir=output_dir,
            workspace=workspace, rngs=rngs,
            iterator=iterator, extractor=extractor,
            mixer=mixer, mover=mover,
            nthreads=nthreads, profiler=p)

        should_finish_early = False

        for func in funcs:
            p2 = p2.start(str(func))
            try:
                func(network=network, population=population,
                     infections=infections, output_dir=output_dir,
                     workspace=workspace, rngs=rngs, nthreads=nthreads,
                     profiler=p2)
            except StopIteration:
                # this function has signalled that the simulation
                # should now stop - we record this request but will
                # still let the other functions complete this
                # iteration
                Console.print(f"{func} has indicated that the model run "
                              f"should stop early. Will finish the run "
                              f"at the end of this iteration")
                should_finish_early = True

            p2 = p2.stop()

        if population.population != start_population:
            # something went wrong as the population should be conserved
            # during the day
            raise AssertionError(
                f"The total population changed during the day. This "
                f"should not happen and indicates a program bug. "
                f"The starting population was {start_population}, "
                f"while the end population is {population.population}. "
                f"Detail is {population}")

        infecteds = population.infecteds

        Console.print(f"Number of infections: {infecteds}")

        iteration_count += 1

        p2 = p2.stop()

        if not p2.is_null():
            Console.print_profiler(p2)

        # save the population trajectory
        trajectory.append(population)

        if should_finish_early:
            Console.print(f"Exiting model run early due to function request")
            break

        elif nsteps is not None:
            if iteration_count >= nsteps:
                Console.print(
                    f"Exiting model run early as number of steps ({nsteps}) "
                    f"reached.")
                break

    # end of while loop
    p = p.stop()

    # finally get and call all of the functions needed to finalise
    # the model run, e.g. closing files, performing overall analyses,
    # writing summary files etc
    p = p.start("finalise_funcs")

    funcs = get_finalise_functions(network=network, population=population,
                                   infections=infections,
                                   output_dir=output_dir,
                                   workspace=workspace, rngs=rngs,
                                   iterator=iterator, extractor=extractor,
                                   mixer=mixer, mover=mover,
                                   nthreads=nthreads, trajectory=trajectory,
                                   profiler=p)

    for func in funcs:
        p = p.start(str(func))
        func(network=network, population=population,
             infections=infections, output_dir=output_dir,
             workspace=workspace, rngs=rngs, nthreads=nthreads,
             trajectory=trajectory, profiler=p)
        p = p.stop()

    p = p.stop()

    p.stop()

    if not p.is_null():
        Console.rule("Overall model timing")
        Console.print_profiler(p)

    Console.print(f"Infection died ... Ending on day {population.day}")

    # only send back the overall statistics
    return trajectory.strip_demographics()
