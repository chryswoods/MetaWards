#!/bin/env python3
"""
The metawards command line program.

Usage:
    To get the help for this program and the list of all of the
    arguments (with defaults) use;

    metawards --help
"""

__all__ = ["get_parallel_scheme", "parse_args", "get_hostfile",
           "get_cores_per_node", "get_threads_per_task",
           "scoop_supervisor", "mpi_supervisor",
           "cli"]


def get_parallel_scheme():
    """This function tries to work out which of the different parallel
       methods we should use to distribute work between multiple processes.

       Detected schemes are "mpi4py", "scoop", and if none of these
       are found, then "multiprocessing"
    """
    import sys

    if "mpi4py" in sys.modules:
        return "mpi4py"
    elif "scoop" in sys.modules:
        return "scoop"
    else:
        return "multiprocessing"


def parse_args():
    """Parse all of the command line arguments"""
    import configargparse
    import sys

    metawards_url = "https://metawards.org"

    configargparse.init_argument_parser(
        name="main",
        description=f"MetaWards epidemic modelling - see "
        f"{metawards_url} for more information.",
        prog="metawards")

    parser = configargparse.get_argument_parser("main")

    parser.add_argument('--version', action="store_true",
                        default=None,
                        help="Print the version information about metawards")

    parser.add_argument('-c', '--config', is_config_file=True,
                        help="Config file that can be used to set some "
                             "or all of these command line options.")

    parser.add_argument('-i', '--input', type=str,
                        help="Input file for the simulation that specifies "
                             "the adjustable parameters to change for each "
                             "run of the model. You must supply some "
                             "input to run a model!")

    parser.add_argument('-l', '--line', type=str, default=None, nargs="*",
                        help="Line number (or line numbers) containing the "
                             "values of adjustable parameters to run for this "
                             "run (or runs) of the model If this isn't "
                             "specified then model runs will be performed "
                             "for adjustable parameters given on all lines "
                             "from the input file. You can specify many "
                             "numbers, and ranges are also accepted, e.g. "
                             "'-l 5 6-10 12,13,14' etc. Note that the line "
                             "numbers are 0-indexed, e.g. the first line of "
                             "the file is line 0. Ranges are inclusive, "
                             "so 3-5 is the same as 3 4 5")

    parser.add_argument("-r", '--repeats', type=int, default=None, nargs="*",
                        help="The number of repeat runs of the model to "
                             "perform for each value of the adjustable "
                             "parameters. By default only a single "
                             "run will be performed for each set of "
                             "adjustable parameters. This complements the "
                             "'repeat' column in the input file (in which "
                             "case the repeats are multipled). Also, "
                             "multiple repeat values can be given, in which "
                             "case each value corresponds to a different "
                             "line in the input file")

    parser.add_argument('-s', '--seed', type=int, default=None,
                        help="Random number seed for this run "
                             "(default is to use a random seed)")

    parser.add_argument('-a', '--additional', type=str, default=None,
                        nargs="*",
                        help="File (or files) containing additional "
                             "seed of outbreak for the model. These are "
                             "used to seed additional infections on "
                             "specific days at different locations "
                             "during a model run")

    parser.add_argument('-o', '--output', type=str, default="output",
                        help="Path to the directory in which to place all "
                             "output files (default 'output'). This "
                             "directory will be subdivided if multiple "
                             "adjustable parameter sets or repeats "
                             "are used.")

    parser.add_argument('-d', '--disease', type=str, default=None,
                        help="Name of the disease to model "
                             "(default is 'ncov')")

    parser.add_argument('-m', '--model', type=str, default=None,
                        help="Name of the input model data set for the "
                             "network (default is '2011Data')")

    parser.add_argument('-D', '--demographics', type=str, default=None,
                        help="Name of the demographics file that provides "
                             "information about how a population is modelled "
                             "as multiple demographics. If this is not "
                             "supplied then the population is modelled "
                             "as a single demographic")

    parser.add_argument('--start-date', type=str, default=None,
                        help="Date of the start of the model outbreak. "
                             "This accepts dates either is iso-format, "
                             "or fuzzy dates such as 'monday', 'tomorrow' "
                             "etc. This is used to work out which days "
                             "are weekends, or to make it easier to specify "
                             "time-based events.")

    parser.add_argument('--start-day', type=int, default=0,
                        help="The start day of the model outbreak. By "
                             "default the model outbreak starts on day "
                             "zero (0), with each step of the model "
                             "representing an additional day. Use this "
                             "to start from a later day, which may be "
                             "useful if you want to more quickly reach "
                             "time based events. Note that the passed "
                             "'--start-date' is always day 0, so day 10 "
                             "has a date which is 10 days after start-date")

    parser.add_argument('-p', '--parameters', type=str, default="march29",
                        help="Name of the input parameter set used to "
                             "control the simulation (default 'march29')")

    parser.add_argument('-R', '--repository', type=str, default=None,
                        help="Path to the MetaWardsData repository. If "
                             "unspecified this defaults to the value "
                             "in the environment variable METAWARDSDATA "
                             "or, if that isn't specified, to "
                             "$HOME/GitHub/MetaWardsData",
                             env_var="METAWARDSDATA")

    parser.add_argument('-P', '--population', type=int, default=57104043,
                        help="Initial population (default 57104043)")

    parser.add_argument('-n', '--nsteps', type=int, default=730,
                        help="Maximum number of steps (days) to run for the "
                             "simulation. Each step represents one day in the "
                             "outbreak (default is to run for a maximum "
                             "of two years - 730 days)")

    parser.add_argument('-u', '--user-variables', type=str, default=None,
                        help="Name of the file containing user-defined "
                             "custom variables. These provide extra "
                             "information that can be read by the "
                             "custom integrators or custom extractors.")

    parser.add_argument('--iterator', type=str, default=None,
                        help=f"Name of the iterator to use to advance the "
                             f"outbreak at each step (day). For a full "
                             f"explanation see the tutorial at "
                             f"{metawards_url}")

    parser.add_argument("--extractor", type=str, default=None,
                        help=f"Name of the extractor to use to extract "
                             f"information during a model run. For a full "
                             f"explanation see the tutorial at "
                             f"{metawards_url}")

    parser.add_argument("--mixer", type=str, default=None,
                        help=f"Name of the mixer to use to mix information "
                             f"from multiple demographics together during "
                             f"a model run. For a full explanation see "
                             f"the tutorial at {metawards_url}")

    parser.add_argument("--mover", type=str, default=None,
                        help=f"Name of the mover to use to move the "
                             f"population between demographics during "
                             f"a model run. For a full explanation see "
                             f"the tutorial at {metawards_url}")

    parser.add_argument("--star-is-E", action="store_true", default=None,
                        help=f"Set the state 0 (* state) as an extra latent "
                             f"state, as opposed to an extra R state")

    parser.add_argument("--star-is-R", action="store_true", default=None,
                        help=f"Set the state 0 (* state) as an extra R "
                             f"state (the default). Individuals in this "
                             f"state are calculated as 'R', even though "
                             f"they will progress on the next day to the "
                             f"E state")

    parser.add_argument("--disable-star", action="store_true", default=None,
                        help=f"Disable the * state. Now state 0 is the first "
                             f"and only latent state. There is no star state.")

    parser.add_argument('--UV', type=float, default=0.0,
                        help="Value for the UV parameter for the model "
                             "(default is 0.0)")

    parser.add_argument('--theme', type=str, default=None,
                        help=f"The theme to use to color the output. "
                             f"Use '--theme simple' if you prefer a "
                             f"simple and colorless output.")

    parser.add_argument('--no-spinner', action="store_true", default=None,
                        help=f"Disable the spinner that spins when little "
                             f"output is being printed to the screen.")

    parser.add_argument("--debug", action="store_true", default=None,
                        help=f"Enable debugging output. This is useful "
                             f"for MetaWards developers or if you are "
                             f"writing your own iterators, extractors etc.")

    parser.add_argument("--debug-level", type=int, default=None,
                        help="Limit debug output to the specified level.")

    parser.add_argument('--nthreads', type=int, default=None,
                        help="Number of threads over which parallelise an "
                             "individual model run. The total number of "
                             "cores used by metawards will be "
                             "nprocesses x nthreads",
                        env_var="OMP_NUM_THREADS")

    parser.add_argument("--nprocs", type=int, default=None,
                        help="The number of processes over which to "
                             "parallelise the different model runs for "
                             "different adjustable parameter sets and "
                             "repeats. By default this will automatically "
                             "work out the number of processes based on "
                             "the way metawards is launched. Use this "
                             "option if you want to specify the number "
                             "of processes manually.")

    parser.add_argument('--hostfile', type=str, default=None,
                        help="The hostfile containing the names of the "
                             "compute nodes over which to run a parallel "
                             "job. If this is not set, the program will "
                             "attempt to automatically get this information "
                             "from the cluster queueing system. Use this "
                             "if the auto-detection fails")

    parser.add_argument('--cores-per-node', type=int, default=None,
                        help="Set the number of processor cores available "
                             "on each of the compute nodes in the cluster "
                             "that will be used to run the models "
                             "(if a cluster is used). If this is not "
                             "set then the program will attempt to "
                             "get this information from the cluster "
                             "queueing system. Use this option if the "
                             "auto-detection fails.")

    parser.add_argument('--auto-bzip', action="store_true",
                        default=None,
                        help="Automatically bz2 compress "
                             "all output files as they are written.")

    parser.add_argument('--no-auto-bzip', action="store_true",
                        default=None,
                        help="Do not automatically bz2 compress "
                             "all output files as they are written.")

    parser.add_argument('--force-overwrite-output', action="store_true",
                        default=False,
                        help="Whether or not to force overwriting of any "
                             "existing output. Using this option will "
                             "tell metawards that it is safe to delete "
                             "the contents of the output directory "
                             "specified in by '--output' if it already "
                             "exists. Dangerous as this can remove "
                             "existing output files")

    parser.add_argument('--max-nodes', type=int, default=16384,
                        help="Maximum number of nodes that can be read")

    parser.add_argument('--max-links', type=int, default=4194304,
                        help="Maximum number of links that can be read")

    parser.add_argument('--profile', action="store_true",
                        default=None, help="Enable profiling of the code")

    parser.add_argument('--no-profile', action="store_true",
                        default=None, help="Disable profiling of the code")

    parser.add_argument('--mpi', action="store_true", default=None,
                        help="Force use of MPI to parallelise across runs")

    parser.add_argument('--scoop', action="store_true", default=None,
                        help="Force use of scoop to parallelise across runs")

    # this hidden option is used to tell the main process started using
    # mpi that it shouldn't try to become a supervisor
    parser.add_argument('--already-supervised', action="store_true",
                        default=None, help=configargparse.SUPPRESS)

    args = parser.parse_args()

    if args.theme:
        from ..utils._console import Console
        Console.set_theme(args.theme)

    if args.no_spinner:
        from ..utils._console import Console
        Console.set_use_spinner(False)

    if args.debug:
        from ..utils._console import Console
        Console.set_debugging_enabled(args.debug, level=args.debug_level)

    if args.version:
        from metawards import print_version_string
        print_version_string()
        sys.exit(0)

    return (args, parser)


def get_hostfile(args):
    """Attempt to find the name of the hostfile used to specify the hosts
       to use in a cluster
    """
    if args.hostfile:
        return args.hostfile

    import os

    # PBS
    hostfile = os.getenv("PBS_NODEFILE")

    if hostfile:
        return hostfile

    # SLURM
    hostfile = os.getenv("SLURM_HOSTFILE")

    if hostfile:
        return hostfile

    return None


def get_cores_per_node(args):
    """Return the number of cores per node in the cluster"""
    if args.cores_per_node:
        return args.cores_per_node

    import os

    try:
        cores_per_node = int(os.getenv("METAWARDS_CORES_PER_NODE"))

        if cores_per_node > 0:
            return cores_per_node

    except Exception:
        pass

    raise ValueError("You must specify the number of cores per node "
                     "using --cores-per-node or by setting the "
                     "environment variable METAWARDS_CORES_PER_NODE")


def get_threads_per_task(args):
    if args.nthreads:
        return args.nthreads

    import os

    try:
        nthreads = int(os.getenv("METAWARDS_THREADS_PER_TASK"))

        if nthreads > 0:
            return nthreads

        nthreads = int(os.getenv("OMP_NUM_THREADS"))

        if nthreads > 0:
            return nthreads
    except Exception:
        pass

    raise ValueError("You must specify the number of threads per task "
                     "using --nthreads or by setting the "
                     "environment variables METAWARDS_THREADS_PER_TASK "
                     "or OMP_NUM_THREADS")


def scoop_supervisor(hostfile, args):
    """Function used by the scoop supervisor to get the information needed to
       form the scoop call to run a scoop version of the program
    """
    import os
    import stat
    import sys
    from metawards.utils import Console

    Console.print("RUNNING A SCOOP PROGRAM")

    cores_per_node = get_cores_per_node(args)

    Console.print(
        f"Will run jobs assuming {cores_per_node} cores per compute node")

    # based on the number of threads requested and the number of cores
    # per node, we can work out the number of scoop processes to start,
    # and can write a hostfile that will create the right layout
    nthreads = get_threads_per_task(args)

    Console.print(f"Will use {nthreads} OpenMP threads per model run...")

    tasks_per_node = int(cores_per_node / nthreads)

    Console.print(f"...meaning that the number of model runs per node will be "
                  f"{tasks_per_node}")

    # Next, read the hostfile to get a unique list of hostnames
    hostnames = {}

    with open(hostfile, "r") as FILE:
        line = FILE.readline()
        while line:
            hostname = line.strip()
            if len(hostname) > 0:
                hostnames[hostname] = 1
            line = FILE.readline()

    hostnames = list(hostnames.keys())
    hostnames.sort()

    Console.print(f"Number of compute nodes equals {len(hostnames)}")
    Console.print(", ".join(hostnames))

    # how many tasks can we perform in parallel?
    nprocs = tasks_per_node * len(hostnames)

    if args.nprocs:
        if nprocs != args.nprocs:
            Console.warning(
                f"You are using a not-recommended number of "
                f"processes {args.nprocs} for the cluster {nprocs}.")

        nprocs = args.nprocs

    Console.print(
        f"Total number of parallel processes to run will be {nprocs}")
    Console.print(f"Total number of cores in use will be {nprocs*nthreads}")

    # Now write a new hostfile that round-robins the MPI tasks over
    # the nodes for 'tasks_per_node' runs
    hostfile = f"_metawards_hostfile_{os.getpid()}"
    Console.print(f"Writing hostfile to {hostfile}")

    with open(hostfile, "w") as FILE:
        i = 0
        while i < nprocs:
            for hostname in hostnames:
                FILE.write(hostname + "\n")
                i += 1

                if i == nprocs:
                    break

    # now craft the scoop command that will use this hostfile to
    # run the job - remember to pass the option to stop the main process
    # attempting to become a supervisor itself...

    import subprocess
    import shlex

    pyexe = sys.executable
    script = os.path.abspath(sys.argv[0])
    args = " ".join(sys.argv[1:])

    # also need to tell the main program the number of processes
    # as it can't work it out itself
    cmd = f"{pyexe} -m scoop --hostfile {hostfile} -n {nprocs} " \
          f"{script} --already-supervised {args} --nprocs {nprocs}"

    Console.print("Executing scoop job using")
    Console.command(cmd)

    try:
        args = shlex.split(cmd)
        subprocess.run(args).check_returncode()
    except Exception as e:
        Console.error("ERROR: Something went wrong!")
        Console.error(f"{e.__class__}: {e}")
        sys.exit(-1)

    # clean up the hostfile afterwards... (we leave it if something
    # went wrong as it may help debugging)
    os.unlink(hostfile)

    Console.print("Scoop processes completed successfully")


def mpi_supervisor(hostfile, args):
    """Function used by the MPI supervisor to get the information needed to
       form the mpiexec call to run an MPI version of the program
    """
    import os
    import stat
    import sys
    from metawards.utils import Console

    Console.print("RUNNING AN MPI PROGRAM")

    cores_per_node = get_cores_per_node(args)

    Console.print(
        f"Will run jobs assuming {cores_per_node} cores per compute node")

    # based on the number of threads requested and the number of cores
    # per node, we can work out the number of mpi processes to start,
    # and can write a hostfile that will create the right layout
    nthreads = get_threads_per_task(args)

    Console.print(f"Will use {nthreads} OpenMP threads per model run...")

    tasks_per_node = int(cores_per_node / nthreads)

    Console.print(f"...meaning that the number of model runs per node will be "
                  f"{tasks_per_node}")

    # Next, read the hostfile to get a unique list of hostnames
    hostnames = {}

    with open(hostfile, "r") as FILE:
        line = FILE.readline()
        while line:
            hostname = line.strip()
            if len(hostname) > 0:
                hostnames[hostname] = 1
            line = FILE.readline()

    hostnames = list(hostnames.keys())
    hostnames.sort()

    Console.print(f"Number of compute nodes equals {len(hostnames)}")
    Console.print(", ".join(hostnames))

    # how many tasks can we perform in parallel?
    nprocs = tasks_per_node * len(hostnames)

    if args.nprocs:
        if nprocs != args.nprocs:
            Console.print(f"WARNING: You are using an unrecommended number of "
                          f"processes {args.nprocs} for the cluster {nprocs}.")

        nprocs = args.nprocs

    Console.print(
        f"Total number of parallel processes to run will be {nprocs}")
    Console.print(f"Total number of cores in use will be {nprocs*nthreads}")

    # Now write a new hostfile that round-robins the MPI tasks over
    # the nodes for 'tasks_per_node' runs
    hostfile = f"_metawards_hostfile_{os.getpid()}"
    Console.print(f"Writing hostfile to {hostfile}")

    with open(hostfile, "w") as FILE:
        i = 0
        while i < nprocs:
            for hostname in hostnames:
                FILE.write(hostname + "\n")
                i += 1

                if i == nprocs:
                    break

    # now craft the mpiexec command that will use this hostfile to
    # run the job - remember to pass the option to stop the main process
    # attempt to become a supervisor itself...
    mpiexec = os.getenv("MPIEXEC")

    if mpiexec is None:
        mpiexec = "mpiexec"

    # check for weird mpiexecs...
    import subprocess
    import shlex

    try:
        args = shlex.split(f"{mpiexec} -v")
        p = subprocess.run(args, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
        v = p.stdout.decode("utf-8").strip()
        Console.print(f"{mpiexec} -v => {v}")

        if v.find("HPE HMPT") != -1:
            raise ValueError(
                "metawards needs a more modern MPI library than HPE's, "
                "so please compile to another MPI and use that.")
    except Exception as e:
        Console.error(f"[ERROR] {e.__class__} {e}")

    pyexe = sys.executable
    script = os.path.abspath(sys.argv[0])
    args = " ".join(sys.argv[1:])

    cmd = f"{mpiexec} -np {nprocs} -hostfile {hostfile} " \
          f"{pyexe} -m mpi4py {script} --already-supervised {args} " \
          f"--nprocs {nprocs}"

    Console.print("Executing MPI job using")
    Console.command(cmd)

    try:
        args = shlex.split(cmd)
        subprocess.run(args).check_returncode()
    except Exception as e:
        Console.error("ERROR: Something went wrong!")
        Console.error(f"{e.__class__}: {e}")
        sys.exit(-1)

    # clean up the hostfile afterwards... (we leave it if something
    # went wrong as it may help debugging)
    os.unlink(hostfile)

    Console.print("MPI processes completed successfully")


def cli():
    """Main function for the command line interface. This does one of three
       things:

       1. If this is the main process, then it parses the arguments and
          runs and manages the jobs

       2. If this is a worker process, then it starts up and waits for work

       3. If this is a supervisor process, then it query the job scheduling
          system for information about the compute nodes to use, and will then
          set up and run a manager (main) process that will use those
          nodes to run the jobs
    """
    from metawards.utils import Console

    # get the parallel scheme now before we import any other modules
    # so that it is clear if mpi4py or scoop (or another parallel module)
    # has been imported via the required "-m module" syntax
    parallel_scheme = get_parallel_scheme()

    if parallel_scheme == "mpi4py":
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        nprocs = comm.Get_size()
        rank = comm.Get_rank()

        if rank != 0:
            # this is a worker process, so should not do anything
            # more until it is given work in the pool
            Console.print(f"Starting worker process {rank+1} of {nprocs-1}...")
            return
        else:
            Console.print("Starting main process...")

    elif parallel_scheme == "scoop":
        Console.print("STARTING SCOOP PROCESS")

    import sys

    args, parser = parse_args()

    if not args.already_supervised:
        hostfile = get_hostfile(args)
        if hostfile:
            # The user has asked to run a parallel job - this means that this
            # process is the parallel supervisor
            if args.mpi:
                mpi_supervisor(hostfile, args)
                return
            elif args.scoop:
                scoop_supervisor(hostfile, args)
                return

            # neither is preferred - if scoop is installed then use that
            try:
                import scoop        # noqa - disable unused warning
                have_scoop = True
            except Exception:
                have_scoop = False

            if have_scoop:
                scoop_supervisor(hostfile, args)
                return

            # do we have MPI?
            try:
                import mpi4py       # noqa - disable unused warning
                have_mpi4py = True
            except Exception:
                have_mpi4py = False

            if have_mpi4py:
                mpi_supervisor(hostfile, args)
                return

            # we don't have any other option, just keep going and
            # use multiprocessing - in this case we don't need a
            # supervisor and this is the main process

    # This is now the code for the main process

    # WE NEED ONE OF these listed options;
    should_run = False

    for arg in [args.input, args.repeats, args.disease, args.additional,
                args.model, args.iterator, args.extractor,
                args.demographics, args.mixer, args.mover]:
        if arg is not None:
            should_run = True
            break

    if not should_run:
        parser.print_help(sys.stdout)
        sys.exit(0)

    if args.repeats is None:
        args.repeats = [1]

    # import the parameters here to speed up the display of help
    from metawards import Parameters, Network, Population, print_version_string

    # print the version information first, so that there is enough
    # information to enable someone to reproduce this run
    print_version_string()

    Console.rule("Initialise")

    if args.input:
        # get the line numbers of the input file to read
        if args.line is None or len(args.line) == 0:
            linenums = None
            Console.print(f"* Using parameters from all lines of {args.input}",
                          markdown=True)
        else:
            from metawards.utils import string_to_ints
            linenums = string_to_ints(args.line)

            if len(linenums) == 0:
                Console.error(f"You cannot read no lines from {args.input}?")
                sys.exit(-1)
            elif len(linenums) == 1:
                Console.print(f"* Using parameters from line {linenums[0]} of "
                              f"{args.input}", markdown=True)
            else:
                Console.print(f"* Using parameters from lines {linenums} of "
                              f"{args.input}", markdown=True)

        from metawards import VariableSets, VariableSet
        variables = VariableSets.read(filename=args.input,
                                      line_numbers=linenums)
    else:
        from metawards import VariableSets, VariableSet
        # create a VariableSets with one null VariableSet
        variables = VariableSets()
        variables.append(VariableSet())

    nrepeats = args.repeats

    if nrepeats is None or len(nrepeats) < 1:
        nrepeats = [1]

    if len(nrepeats) > 1 and len(variables) != len(nrepeats):
        Console.error(f"The number of repeats {len(nrepeats)} must equal the "
                      f"number of adjustable variable lines {len(variables)}")
        raise ValueError("Disagreement in the number of repeats and "
                         "adjustable variables")

    # ensure that all repeats are >= 0
    nrepeats = [0 if int(x) < 0 else int(x) for x in nrepeats]

    if sum(nrepeats) == 0:
        Console.error(f"The number of the number of repeats is 0. Are you "
                      f"sure that you don't want to run anything?")
        raise ValueError("Cannot run nothing")

    if len(nrepeats) == 1 and nrepeats[0] == 1:
        Console.print("* Performing a single run of each set of parameters",
                      markdown=True)
    elif len(nrepeats) == 1:
        Console.print(
            f"* Performing {nrepeats[0]} runs of each set of parameters",
            markdown=True)
    else:
        Console.print(
            f"* Performing {nrepeats} runs applied to the parameters",
            markdown=True)

    variables = variables.repeat(nrepeats)

    # working out the number of processes and threads...
    from metawards.utils import guess_num_threads_and_procs
    (nthreads, nprocs) = guess_num_threads_and_procs(
        njobs=len(variables),
        nthreads=args.nthreads,
        nprocs=args.nprocs,
        parallel_scheme=parallel_scheme)

    Console.print(
        f"\n* Number of threads to use for each model run is {nthreads}",
        markdown=True)

    if nprocs > 1:
        Console.print(f"* Number of processes used to parallelise model "
                      f"runs is {nprocs}", markdown=True)
        Console.print(
            f"* Parallelisation will be achieved using {parallel_scheme}",
            markdown=True)

    # sort out the random number seed
    seed = args.seed

    if seed is None:
        import random
        seed = random.randint(10000, 99999999)

    if seed == 0:
        # this is a special mode that a developer can use to force
        # all jobs to use the same random number seed (15324) that
        # is used for comparing outputs. This should NEVER be used
        # for production code
        Console.warning("Using special mode to fix all random number"
                        "seeds to 15324. DO NOT USE IN PRODUCTION!!!")
    else:
        Console.print(f"* Using random number seed {seed}", markdown=True)

    # get the starting day and date
    start_day = args.start_day

    if start_day < 0:
        raise ValueError(f"You cannot use a start day {start_day} that is "
                         f"less than zero!")

    start_date = None

    if args.start_date:
        try:
            from dateparser import parse
            start_date = parse(args.start_date).date()
        except Exception:
            pass

        if start_date is None:
            from datetime import date
            try:
                start_date = date.fromisoformat(args.start_date)
            except Exception as e:
                raise ValueError(
                    f"Cannot interpret a valid date from "
                    f"'{args.start_date}'. Error is "
                    f"{e.__class__} {e}")

    if start_date is None:
        from datetime import date
        start_date = date.today()

    Console.print(f"* Day zero is {start_date.strftime('%A %B %d %Y')}",
                  markdown=True)

    if start_day != 0:
        from datetime import timedelta
        start_day_date = start_date + timedelta(days=start_day)
        Console.print(f"Starting on day {start_day}, which is "
                      f"{start_day_date.strftime('%A %B %d %Y')}")
    else:
        start_day_date = start_date

    # now find the MetaWardsData repository as this will be needed
    # for the repeat command line too
    (repository, repository_version) = Parameters.get_repository(
        args.repository)

    Console.print(f"* Using MetaWardsData at {repository}", markdown=True)

    if repository_version["is_dirty"]:
        Console.warning("This repository is dirty, meaning that the data"
                        "has not been committed to git. This may make "
                        "this calculation very difficult to reproduce")

    # now work out the minimum command line needed to repeat this job
    args.seed = seed
    args.nprocs = nprocs
    args.nthreads = nthreads
    args.start_date = start_date.isoformat()
    args.repository = repository

    # also print the source of all inputs
    import configargparse
    Console.rule("Souce of inputs")
    p = configargparse.get_argument_parser("main")
    Console.print(p.format_values())

    # print out the command used to repeat this job
    repeat_cmd = "metawards"

    for key, value in vars(args).items():
        if value is not None:
            k = key.replace("_", "-")

            if isinstance(value, bool):
                if value:
                    repeat_cmd += f" --{k}"
            elif isinstance(value, list):
                repeat_cmd += f" --{k}"
                for val in value:
                    v = str(val)
                    if " " in v:
                        repeat_cmd += f" '{v}''"
                    else:
                        repeat_cmd += f" {v}"
            else:
                v = str(value)
                if " " in v:
                    repeat_cmd += f" --{k} '{v}''"
                else:
                    repeat_cmd += f" --{k} {v}"

    Console.rule("Repeating this run")
    Console.print("To repeat this job use the command;")
    Console.command(repeat_cmd)
    Console.print("Or alternatively use the config.yaml file that will be "
                  "written to the output directory and use the command;")
    Console.command("metawards -c config.yaml")

    # load all of the parameters
    try:
        params = Parameters.load(parameters=args.parameters)
    except Exception as e:
        Console.warning(
            f"Unable to load parameter files. Make sure that you have "
            f"cloned the MetaWardsData repository and have set the "
            f"environment variable METAWARDSDATA to point to the "
            f"local directory containing the repository, e.g. the "
            f"default is $HOME/GitHub/MetaWardsData")
        raise e

    # should we profile the code? (default no as it prints a lot)
    profiler = None

    if args.no_profile:
        profiler = None
    elif args.profile:
        from metawards.utils import Profiler
        profiler = Profiler()

    # load the disease and starting-point input files
    Console.rule("Disease")
    if args.disease:
        params.set_disease(args.disease)
    else:
        params.set_disease("ncov")

    Console.rule("Model data")
    if args.model:
        params.set_input_files(args.model)
    else:
        params.set_input_files("2011Data")

    # load the user-defined custom parameters
    Console.rule("Custom parameters and seeds")
    if args.user_variables:
        custom = VariableSet.read(args.user_variables)
        Console.print(f"Adjusting variables to {custom}")
        custom.adjust(params)
    else:
        Console.print("Not adjusting any parameters...")

    # read the additional seeds
    if args.additional is None or len(args.additional) == 0:
        Console.print("Not using any additional seeds...")
    else:
        for additional in args.additional:
            Console.print(f"Loading additional seeds from {additional}")
            params.add_seeds(additional)

    # what to do with the 0 state?
    stage_0 = "R"

    if args.disable_star:
        Console.print("Disabling the * state. Stage 0 is the one and "
                      "only E state.")
        stage_0 = "disable"
    elif args.star_is_E:
        Console.print("Setting the * state as an additional E state.")
        stage_0 = "E"
    else:
        Console.print("Setting the * state as an additional R state.")
        stage_0 = "R"

    params.stage_0 = stage_0

    # extra parameters that are set
    params.UV = args.UV

    # set these extra parameters to 0
    params.static_play_at_home = 0
    params.play_to_work = 0
    params.work_to_play = 0
    params.daily_imports = 0.0

    Console.rule("Parameters")
    Console.print(params, markdown=True)

    # the size of the starting population
    population = Population(initial=args.population,
                            date=start_day_date,
                            day=start_day)

    Console.rule("Building the network")
    network = Network.build(params=params,
                            population=population,
                            max_nodes=args.max_nodes,
                            max_links=args.max_links,
                            profiler=profiler)

    if args.demographics:
        from metawards import Demographics
        Console.rule("Specialising into demographics")
        demographics = Demographics.load(args.demographics)
        Console.print(demographics)

        network = network.specialise(demographics,
                                     profiler=profiler,
                                     nthreads=nthreads)

    Console.rule("Preparing to run")
    from metawards import OutputFiles
    from metawards.utils import run_models

    outdir = args.output

    if outdir is None:
        outdir = "output"

    if args.force_overwrite_output:
        prompt = None
    else:
        from metawards import input
        def prompt(x): return input(x, default="y")

    auto_bzip = True

    if args.auto_bzip:
        auto_bzip = True
    elif args.no_auto_bzip:
        auto_bzip = False

    if args.iterator:
        iterator = args.iterator
    else:
        iterator = None

    if args.extractor:
        extractor = args.extractor
    else:
        extractor = None

    if args.mixer:
        mixer = args.mixer
    else:
        mixer = None

    if args.mover:
        mover = args.mover
    else:
        mover = None

    with OutputFiles(outdir, force_empty=args.force_overwrite_output,
                     auto_bzip=auto_bzip, prompt=prompt) as output_dir:
        # write the config file for this job to output/config.yaml
        Console.rule("Running the model")
        CONSOLE = output_dir.open("console.log")
        Console.save(CONSOLE)

        lines = []
        max_keysize = None

        for key, value in vars(args).items():
            if max_keysize is None:
                max_keysize = len(key)
            elif len(key) > max_keysize:
                max_keysize = len(key)

        for key, value in vars(args).items():
            if value is not None:
                key = key.replace("_", "-")
                spaces = " " * (max_keysize - len(key))

                if isinstance(value, bool):
                    if value:
                        lines.append(f"{key}:{spaces} true")
                    else:
                        lines.append(f"{key}:{spaces} false")
                elif isinstance(value, list):
                    s_value = [str(x) for x in value]
                    lines.append(f"{key}:{spaces} [ {', '.join(s_value)} ]")
                else:
                    lines.append(f"{key}:{spaces} {value}")

        CONFIG = output_dir.open("config.yaml", auto_bzip=False)
        lines.sort(key=str.swapcase)
        CONFIG.write("\n".join(lines))
        CONFIG.write("\n")
        CONFIG.flush()
        CONFIG.close()
        lines = None

        result = run_models(network=network, variables=variables,
                            population=population, nprocs=nprocs,
                            nthreads=nthreads, seed=seed,
                            nsteps=args.nsteps,
                            output_dir=output_dir,
                            iterator=iterator,
                            extractor=extractor,
                            mixer=mixer,
                            mover=mover,
                            profiler=profiler,
                            parallel_scheme=parallel_scheme)

        if result is None or len(result) == 0:
            Console.print("No output - end of run")
            return 0

        Console.rule("End of the run", style="finish")

        Console.save(CONSOLE)

    return 0


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()  # needed to stop fork bombs
    cli()
