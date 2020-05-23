
from typing import Union as _Union
from typing import List as _List
from typing import Tuple as _Tuple

from .._network import Network
from .._networks import Networks
from .._population import Population
from .._variableset import VariableSets, VariableSet
from .._outputfiles import OutputFiles

from ._profiler import Profiler
from ._get_functions import MetaFunction

import os as _os

__all__ = ["get_number_of_processes", "run_models"]


def get_number_of_processes(parallel_scheme: str, nprocs: int = None):
    """This function works out how many processes have been set
       by the paralellisation system called 'parallel_scheme'
    """
    if nprocs is None:
        if parallel_scheme == "multiprocessing":
            return 1
        elif parallel_scheme == "mpi4py":
            from mpi4py import MPI
            comm = MPI.COMM_WORLD
            nprocs = comm.Get_size()
            return nprocs
        elif parallel_scheme == "scoop":
            raise ValueError(
                f"You must specify the number of processes for "
                f"scoop to parallelise over")
        else:
            raise ValueError(
                f"You must specify the number of processes to "
                f"use for parallel scheme '{parallel_scheme}'")

    if parallel_scheme == "mpi4py":
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        n = comm.Get_size()

        if n < nprocs:
            return n
        else:
            return nprocs
    elif parallel_scheme == "scoop":
        return 4
    elif parallel_scheme == "multiprocessing":
        return nprocs
    else:
        raise ValueError(
            f"Unrecognised parallelisation scheme {parallel_scheme}")


def run_models(network: _Union[Network, Networks],
               variables: VariableSets,
               population: Population,
               nprocs: int, nthreads: int, seed: int,
               nsteps: int, output_dir: OutputFiles,
               iterator: MetaFunction = None,
               extractor: MetaFunction = None,
               mixer: MetaFunction = None,
               mover: MetaFunction = None,
               profiler: Profiler = None,
               parallel_scheme: str = "multiprocessing",
               debug_seeds=False) \
        -> _List[_Tuple[VariableSet, Population]]:
    """Run all of the models on the passed Network that are described
       by the passed VariableSets

       Parameters
       ----------
       network: Network or Networks
         The network(s) to model
       variables: VariableSets
         The sets of VariableSet that represent all of the model
         runs to perform
       population: Population
         The initial population for all of the model runs. This also
         contains the starting date and day for the model outbreak
       nprocs: int
         The number of model runs to perform in parallel
       nthreads: int
         The number of threads to parallelise each model run over
       seed: int
         Random number seed which is used to generate random seeds
         for all model runs
       nsteps: int
         The maximum number of steps to perform for each model - this
         will run until the outbreak is over if this is None
       output_dir: OutputFiles
         The OutputFiles that represents the directory in which all
         output should be placed
       iterator: str
         Iterator to load that will be used to iterate the outbreak
       extractor: str
         Extractor to load that will be used to extract information
       mixer: str
         Mixer to load that will be used to mix demographic data
       mover: str
         Mover to load that will be used to move the population between
         different demographics
       profiler: Profiler
         Profiler used to profile the model run
       parallel_scheme: str
         Which parallel scheme (multiprocessing, mpi4py or scoop) to use
         to run multiple model runs in parallel
       debug_seeds: bool (False)
         Set this parameter to force all runs to use the same seed
         (seed) - this is used for debugging and should never be set
         in production runs

       Returns
       -------
       results: List[ tuple(VariableSet, Population)]
         The set of adjustable variables and final population at the
         end of each run
    """

    if len(variables) == 1:
        # no need to do anything complex - just a single run
        params = network.params.set_variables(variables[0])

        network.update(params, profiler=profiler)

        trajectory = network.run(population=population, seed=seed,
                                 nsteps=nsteps,
                                 output_dir=output_dir,
                                 iterator=iterator,
                                 extractor=extractor,
                                 mixer=mixer,
                                 mover=mover,
                                 profiler=profiler,
                                 nthreads=nthreads)

        results = [(variables[0], trajectory)]

        # perform the final summary
        from ._get_functions import get_summary_functions

        if extractor is None:
            from ..extractors._extract_default import extract_default
            extractor = extract_default
        else:
            from ..extractors._extract_custom import build_custom_extractor
            extractor = build_custom_extractor(extractor)

        funcs = get_summary_functions(network=network, results=results,
                                      output_dir=output_dir,
                                      extractor=extractor,
                                      nthreads=nthreads)

        for func in funcs:
            func(network=network, output_dir=output_dir, results=results)

        return results

    # generate the random number seeds for all of the jobs
    # (for testing, we will use the same seed so that I can check
    #  that they are all working)
    seeds = []

    from ._console import Console

    if seed == 0:
        # this is a special mode that a developer can use to force
        # all jobs to use the same random number seed (15324) that
        # is used for comparing outputs. This should NEVER be used
        # for production code
        Console.warning("Using special mode to fix all random number "
                        "seeds to 15324. DO NOT USE IN PRODUCTION!!!")

        for i in range(0, len(variables)):
            seeds.append(15324)

    elif debug_seeds:
        Console.warning(f"Using special model to make all jobs use the "
                        f"Same random number seed {seed}. "
                        f"DO NOT USE IN PRODUCTION!")

        for i in range(0, len(variables)):
            seeds.append(seed)

    else:
        from ._ran_binomial import seed_ran_binomial, ran_int
        rng = seed_ran_binomial(seed)

        # seed the rngs used for the sub-processes using this rng
        for i in range(0, len(variables)):
            seeds.append(ran_int(rng, 10000, 99999999))

    # set the output directories for all of the jobs - this is based
    # on the fingerprint, so should be unique for each job
    outdirs = []

    for v in variables:
        f = v.output_dir()
        d = _os.path.join(output_dir.get_path(), f)

        i = 1
        base = d

        while d in outdirs:
            i += 1
            d = base + "x%03d" % i

        outdirs.append(d)

    outputs = []

    Console.print(
        f"Running **{len(variables)}** jobs using **{nprocs}** process(es)",
        markdown=True)

    if nprocs == 1:
        # no need to use a pool, as we will repeat this calculation
        # several times
        save_network = network.copy()

        for i, variable in enumerate(variables):
            seed = seeds[i]
            outdir = outdirs[i]

            with output_dir.open_subdir(outdir) as subdir:
                Console.print(
                    f"Running parameter set {i+1} of {len(variables)} "
                    f"using seed {seed}")
                Console.print(f"All output written to {subdir.get_path()}")

                with Console.redirect_output(subdir.get_path(),
                                             auto_bzip=output_dir.auto_bzip()):
                    Console.print(f"Running variable set {i+1}")
                    Console.print(f"Variables: {variable}")
                    Console.print(f"Random seed: {seed}")
                    Console.print(f"nthreads: {nthreads}")

                    # no need to do anything complex - just a single run
                    params = network.params.set_variables(variable)

                    network.update(params, profiler=profiler)

                    with Console.spinner("Computing model run") as spinner:
                        try:
                            output = network.run(population=population,
                                                 seed=seed,
                                                 nsteps=nsteps,
                                                 output_dir=subdir,
                                                 iterator=iterator,
                                                 extractor=extractor,
                                                 mixer=mixer,
                                                 mover=mover,
                                                 profiler=profiler,
                                                 nthreads=nthreads)
                            spinner.success()
                        except Exception as e:
                            spinner.failure()
                            error = f"FAILED: {e.__class__} {e}"
                            Console.error(error)
                            output = None

                    if output is not None:
                        outputs.append((variable, output))
                    else:
                        outputs.append((variable, []))

                if output is not None:
                    Console.panel(f"Completed job {i+1} of {len(variables)}\n"
                                  f"{variable}\n"
                                  f"{output[-1]}",
                                  style="alternate")
                else:
                    Console.error(f"Job {i+1} of {len(variables)}\n"
                                  f"{variable}\n"
                                  f"{error}")
            # end of OutputDirs context manager

            if i != len(variables) - 1:
                # still another run to perform, restore the network
                # to the original state
                network = save_network.copy()
        # end of loop over variable sets
    else:
        from ._worker import run_worker

        # create all of the parameters and options to run
        arguments = []

        if isinstance(network, Networks):
            max_nodes = network.overall.nnodes + 1
            max_links = max(network.overall.nlinks, network.overall.nplay) + 1
        else:
            max_nodes = network.nnodes + 1
            max_links = max(network.nlinks, network.nplay) + 1

        try:
            demographics = network.demographics
        except Exception:
            demographics = None

        # give the workers a clean copy of the profiler
        if profiler is None:
            worker_profiler = None
        else:
            worker_profiler = profiler.__class__()

        for i, variable in enumerate(variables):
            seed = seeds[i]
            outdir = outdirs[i]

            arguments.append({
                "params": network.params.set_variables(variable),
                "demographics": demographics,
                "options": {"seed": seed,
                            "output_dir": outdir,
                            "auto_bzip": output_dir.auto_bzip(),
                            "population": population,
                            "nsteps": nsteps,
                            "iterator": iterator,
                            "extractor": extractor,
                            "mixer": mixer,
                            "mover": mover,
                            "profiler": worker_profiler,
                            "nthreads": nthreads,
                            "max_nodes": max_nodes,
                            "max_links": max_links}
            })

        if parallel_scheme == "multiprocessing":
            # run jobs using a multiprocessing pool
            Console.rule("MULTIPROCESSING")
            from multiprocessing import Pool

            results = []

            with Pool(processes=nprocs) as pool:
                for argument in arguments:
                    results.append(pool.apply_async(run_worker, (argument,)))

                for i, result in enumerate(results):
                    with Console.spinner(
                            "Computing model run") as spinner:
                        try:
                            result.wait()
                            output = result.get()
                            spinner.success()
                        except Exception as e:
                            spinner.failure()
                            error = f"FAILED: {e.__class__} {e}"
                            Console.error(error)
                            output = None

                        if output is not None:
                            Console.panel(
                                f"Completed job {i+1} of {len(variables)}\n"
                                f"{variables[i]}\n"
                                f"{output[-1]}",
                                style="alternate")

                            outputs.append((variables[i], output))
                        else:
                            Console.error(f"Job {i+1} of {len(variables)}\n"
                                          f"{variable}\n"
                                          f"{error}")
                            outputs.append((variables[i], []))

        elif parallel_scheme == "mpi4py":
            # run jobs using a mpi4py pool
            Console.rule("MPI")
            Console.print("Running jobs in parallel using a mpi4py pool")
            from mpi4py import futures
            with futures.MPIPoolExecutor(max_workers=nprocs) as pool:
                results = pool.map(run_worker, arguments)

                for i in range(0, len(variables)):
                    with Console.spinner("Computing model run") as spinner:
                        try:
                            output = next(results)
                            spinner.success()
                        except Exception as e:
                            spinner.failure()
                            error = f"FAILED: {e.__class__} {e}"
                            Console.error(error)
                            output = None

                        if output is not None:
                            Console.panel(
                                f"Completed job {i+1} of {len(variables)}\n"
                                f"{variables[i]}\n"
                                f"{output[-1]}",
                                style="alternate")

                            outputs.append((variables[i], output))
                        else:
                            Console.error(f"Job {i+1} of {len(variables)}\n"
                                          f"{variable}\n"
                                          f"{error}")
                            outputs.append((variables[i], []))

        elif parallel_scheme == "scoop":
            # run jobs using a scoop pool
            Console.rule("SCOOP")
            Console.print("Running jobs in parallel using a scoop pool")
            from scoop import futures

            results = []

            for argument in arguments:
                try:
                    results.append(futures.submit(run_worker, argument))
                except Exception as e:
                    Console.error(
                        f"Error submitting calculation: {e.__class__} {e}\n"
                        f"Trying to submit again...")

                    # try again
                    try:
                        results.append(futures.submit(run_worker, argument))
                    except Exception as e:
                        Console.error(
                            f"No - another error: {e.__class__} {e}\n"
                            f"Skipping this job")
                        results.append(None)

            for i in range(0, len(results)):
                with Console.spinner("Computing model run") as spinner:
                    try:
                        output = results[i].result()
                        spinner.success()
                    except Exception as e:
                        spinner.failure()
                        error = f"FAILED: {e.__class__} {e}"
                        Console.error(error)
                        output = None

                    if output is not None:
                        Console.panel(
                            f"Completed job {i+1} of {len(variables)}\n"
                            f"{variables[i]}\n"
                            f"{output[-1]}",
                            style="alternate")

                        outputs.append((variables[i], output))
                    else:
                        Console.error(f"Job {i+1} of {len(variables)}\n"
                                      f"{variable}\n"
                                      f"{error}")
                        outputs.append((variables[i], []))
        else:
            raise ValueError(f"Unrecognised parallelisation scheme "
                             f"{parallel_scheme}.")

    # perform the final summary
    from ._get_functions import get_summary_functions

    if extractor is None:
        from ..extractors._extract_default import extract_default
        extractor = extract_default
    else:
        from ..extractors._extract_custom import build_custom_extractor
        extractor = build_custom_extractor(extractor)

    funcs = get_summary_functions(network=network, results=outputs,
                                  output_dir=output_dir, extractor=extractor,
                                  nthreads=nthreads)

    for func in funcs:
        try:
            func(network=network, output_dir=output_dir,
                 results=outputs, nthreads=nthreads)
        except Exception as e:
            Console.error(f"Error calling {func}: {e.__class__} {e}")

    return outputs
