
from array import array
from sys import platform

__all__ = ["guess_num_threads_and_procs",
           "get_available_num_threads",
           "create_thread_generators"]


def guess_num_threads_and_procs(njobs: int,
                                nthreads: int = None,
                                nprocs: int = None,
                                ncores: int = None,
                                parallel_scheme: str = None):
    """Guess the number of processes and threads per process
       to use to make most-efficient processing of
       'njobs' jobs.

       Parameters
       ----------
       njobs: int
         The number of jobs (model runs) that must be performed
       nthreads: int
         The number of threads requested - if None then this this will be
         guessed
       nprocs: int
         The number of processes requested - if None then this will be
         guessed
       ncores: int
         The number of available cores on each node (or this computer).
         This will be obtained from the OS if it is not supplied
       parallel_scheme: str
         The parallelisation scheme that is being used to parallelise
         over processes

       Returns
       -------
       (nthreads, nprocs): Tuple[int, int]
         Tuple of the best-guessed 'nthreads' and 'nprocs' values to use
    """
    if nthreads is None:
        nthreads = 0

    if nprocs is None:
        nprocs = 0

    if njobs is None or njobs < 0:
        return (1, 1)

    if parallel_scheme is None:
        parallel_scheme = "multiprocessing"

    if nprocs < 1 and parallel_scheme != "multiprocessing":
        # we have been told the number of processes to use by
        # the scoop or mpi4py scheduler
        from metawards.utils import get_number_of_processes
        nprocs = get_number_of_processes(parallel_scheme, nprocs)

    if ncores is None:
        ncores = get_available_num_threads()

    if nthreads < 1 and nprocs < 1:
        # we will need to calculate the best values of nprocs and
        # nthreads to use to divide the work most efficiently. The
        # goal should be to run as many model runs in parallel as
        # possible

        if njobs >= 0.8 * ncores:   # not worth going parallel for <80%
            nthreads = 1
            nprocs = ncores
        else:
            import math
            nthreads = int(math.floor(ncores/njobs))
            if nthreads < 1:
                nthreads = 1
            nprocs = int(math.floor(ncores/nthreads))
            if nprocs < 1:
                nprocs = 1
    elif nthreads < 1:
        import math
        nthreads = int(math.floor(ncores/nprocs))

        if nthreads < 1:
            nthreads = 1
    elif nprocs < 1:
        import math
        max_nprocs = int(math.floor(ncores/nthreads))
        if max_nprocs < njobs:
            nprocs = max_nprocs
        else:
            nprocs = max_nprocs

    return (nthreads, nprocs)


def get_available_num_threads():
    """Return the maximum number of threads that are recommended
       for this computer (the OMP_NUM_THREADS value)
    """
    import os

    # try OMP_NUM_THREADS as this is the accepted way to
    # override the number in a queueing system
    omp_num_threads = os.getenv("OMP_NUM_THREADS", None)

    if omp_num_threads is not None:
        try:
            return int(omp_num_threads)
        except Exception:
            pass

    # ok, get this from 'os'
    return os.cpu_count()


def create_thread_generators(rng, nthreads):
    """Return a set of random number generators, one for each
       thread - these are seeded using the next 'nthreads'
       random numbers drawn from the passed generator

       If 'nthreads' is 1, 0 or None, then then just
       returns the passed 'rng'
    """
    rngs = []

    if nthreads is None or nthreads <= 1:
        rngs.append(rng)
    else:
        from ._ran_binomial import seed_ran_binomial, ran_int

        from ._console import Console

        for i in range(0, nthreads):
            seed = ran_int(rng)
            Console.print(f"Random seed for thread {i} equals **{seed}**",
                          markdown=True)
            rngs.append(seed_ran_binomial(seed))

    # need to return these as an array so that they are more easily
    # accessible from the OpenMP loops - rng is a unsigned 64-bit integer
    # as a uintptr_t - this best corresponds to unsigned long ("L")
    if platform == "win32":
        # Use unsigned long long ("Q") on Windows since it has a 32-bit long.
        return array("Q", rngs)
    else:
        return array("L", rngs)
