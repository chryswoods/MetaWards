
from .._network import Network
from .._population import Population
from .._variableset import VariableSets
from .._outputfiles import OutputFiles

from contextlib import contextmanager as _contextmanager

import os as _os
import sys as _sys

__all__ = ["get_number_of_processes", "run_models", "redirect_output"]


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


@_contextmanager
def redirect_output(outdir):
    """Nice way to redirect stdout and stderr - thanks to
       Emil Stenström in
       https://stackoverflow.com/questions/6735917/redirecting-stdout-to-nothing-in-python
    """
    new_out = open(_os.path.join(outdir, "output.txt"), "w")
    old_out = _sys.stdout
    _sys.stdout = new_out

    new_err = open(_os.path.join(outdir, "output.err"), "w")
    old_err = _sys.stderr
    _sys.stderr = new_err

    try:
        yield new_out
    finally:
        _sys.stdout = old_out
        _sys.stderr = old_err
        new_out.close()
        new_err.close()


def run_models(network: Network, variables: VariableSets,
               population: Population,
               nprocs: int, nthreads: int, seed: int,
               nsteps: int, output_dir: OutputFiles,
               iterator: str, extractor: str,
               profile: bool, parallel_scheme: str):
    """Run all of the models on the passed Network that are described
       by the passed VariableSets

       Parameters
       ----------
       network: Network
         The network to model
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
       profile: bool
         Whether or not to profile the model run and print out live
         timing (useful for performance debugging)
       parallel_scheme: str
         Which parallel scheme (multiprocessing, mpi4py or scoop) to use
         to run multiple model runs in parallel
    """

    # this variable is used to pick out some of the additional seeds?
    s = -1

    if len(variables) == 1:
        # no need to do anything complex - just a single run
        params = network.params.set_variables(variables[0])

        network.update(params, profile=profile)

        trajectory = network.run(population=population, seed=seed,
                                 s=s, nsteps=nsteps,
                                 output_dir=output_dir,
                                 iterator=iterator,
                                 extractor=extractor,
                                 profile=profile,
                                 nthreads=nthreads)

        return [(variables[0], trajectory)]

    # generate the random number seeds for all of the jobs
    # (for testing, we will use the same seed so that I can check
    #  that they are all working)
    seeds = []

    if seed == 0:
        # this is a special mode that a developer can use to force
        # all jobs to use the same random number seed (15324) that
        # is used for comparing outputs. This should NEVER be used
        # for production code
        print("** WARNING: Using special mode to fix all random number")
        print("** WARNING: seeds to 15324. DO NOT USE IN PRODUCTION!!!")

        for i in range(0, len(variables)):
            seeds.append(15324)

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
        f = v.fingerprint(include_index=True)
        d = _os.path.join(output_dir.get_path(), f)
        outdirs.append(d)

    outputs = []

    print(f"\nRunning {len(variables)} jobs using {nprocs} process(es)")

    if nprocs == 1:
        # no need to use a pool, as we will repeat this calculation
        # several times
        for i, variable in enumerate(variables):
            seed = seeds[i]
            outdir = outdirs[i]

            with output_dir.open_subdir(outdir) as subdir:
                print(f"\nRunning parameter set {i+1} of {len(variables)} "
                      f"using seed {seed}")
                print(f"All output written to {subdir.get_path()}")

                with redirect_output(subdir.get_path()):
                    print(f"Running variable set {i+1}")
                    print(f"Variables: {variable}")
                    print(f"Random seed: {seed}")
                    print(f"nthreads: {nthreads}")

                    # no need to do anything complex - just a single run
                    params = network.params.set_variables(variable)

                    network.update(params, profile=profile)

                    output = network.run(population=population, seed=seed,
                                         s=s, nsteps=nsteps,
                                         output_dir=subdir,
                                         iterator=iterator,
                                         extractor=extractor,
                                         profile=profile,
                                         nthreads=nthreads)

                    outputs.append((variable, output))

                print(f"Completed job {i+1} of {len(variables)}")
                print(variable)
                print(output[-1])
            # end of OutputDirs context manager
        # end of loop over variable sets
    else:
        from ._worker import run_worker

        # create all of the parameters and options to run
        arguments = []

        max_nodes = network.nnodes + 1
        max_links = max(network.nlinks, network.plinks) + 1

        for i, variable in enumerate(variables):
            seed = seeds[i]
            outdir = outdirs[i]

            arguments.append({
                "params": network.params.set_variables(variable),
                "options": {"seed": seed,
                            "output_dir": outdir,
                            "auto_bzip": output_dir.auto_bzip(),
                            "population": population,
                            "s": s,
                            "nsteps": nsteps,
                            "iterator": iterator,
                            "extractor": extractor,
                            "profile": profile,
                            "nthreads": nthreads,
                            "max_nodes": max_nodes,
                            "max_links": max_links}
            })

        if parallel_scheme == "multiprocessing":
            # run jobs using a multiprocessing pool
            print("\nRunning jobs in parallel using a multiprocessing pool...")
            from multiprocessing import Pool
            with Pool(processes=nprocs) as pool:
                results = pool.map(run_worker, arguments)

                for i, result in enumerate(results):
                    print(f"\nCompleted job {i+1} of {len(variables)}")
                    print(variables[i])
                    print(result[-1])
                    outputs.append((variables[i], result))

        elif parallel_scheme == "mpi4py":
            # run jobs using a mpi4py pool
            print("\nRunning jobs in parallel using a mpi4py pool...")
            from mpi4py import futures
            with futures.MPIPoolExecutor(max_workers=nprocs) as pool:
                results = pool.map(run_worker, arguments)

                for i, result in enumerate(results):
                    print(f"\nCompleted job {i+1} of {len(variables)}")
                    print(variables[i])
                    print(result[-1])
                    outputs.append((variables[i], result))

        elif parallel_scheme == "scoop":
            # run jobs using a scoop pool
            print("\nRunning jobs in parallel using a scoop pool...")
            from scoop import futures

            results = futures.map(run_worker, arguments)

            for i, result in enumerate(results):
                print(f"\nCompleted job {i+1} of {len(variables)}")
                print(variables[i])
                print(result[-1])
                outputs.append((variables[i], result))

        else:
            raise ValueError(f"Unrecognised parallelisation scheme "
                             f"{parallel_scheme}.")

    return outputs
