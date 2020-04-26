
from .._network import Network
from .._parameters import Parameters
from .._outputfiles import OutputFiles

import os
import sys
from contextlib import contextmanager

__all__ = ["run_worker", "prepare_worker"]

global_network = None


@contextmanager
def silence_output():
    """Nice way to silence stdout and stderr - thanks to
       Emil Stenström in
       https://stackoverflow.com/questions/6735917/redirecting-stdout-to-nothing-in-python
    """
    new_out = open(os.devnull, "w")
    old_out = sys.stdout
    sys.stdout = new_out

    new_err = open(os.devnull, "w")
    old_err = sys.stderr
    sys.stderr = new_err

    try:
        yield new_out
    finally:
        sys.stdout = old_out
        sys.stderr = old_err


def prepare_worker(params: Parameters, options):
    """Prepare a worker to receive work to run a model using the passed
       parameters. This will build the network specified by the
       parameters and will store it in global memory ready to
       be used for a model run. Note that these are
       silent, printing nothing to stdout or stderr
    """
    # switch off printing to stdout and stderr
    with silence_output():
        global global_network

        max_nodes = options["max_nodes"]
        max_links = options["max_links"]

        del options["max_nodes"]
        del options["max_links"]

        if global_network is None:
            global_network = Network.build(params=params,
                                           calculate_distances=True,
                                           profile=False,
                                           max_nodes=max_nodes,
                                           max_links=max_links)

        else:
            global_network.update(params)


def run_worker(arguments):
    """Ask the worker to run a model using the passed variables and
       options. This will write to options['output_dir'] and will
       also return the population object that contains the final
       population data.

       WARNING - the iterator and extractor arguments rely on the
       workers starting in the same directory as the main process,
       so that they can load the same python files (if the user
       is using a custom iterator or extractor)
    """
    params = arguments["params"]
    options = arguments["options"]

    # first, build and prepare the network
    prepare_worker(params, options)

    # next, run the job, writing to output
    from ._runner import redirect_output

    outdir = options["output_dir"]
    auto_bzip = options["auto_bzip"]
    del options["auto_bzip"]

    # if the user wanted to remove this directory then they would
    # have done so in the main process - no need to check again
    with OutputFiles(outdir, check_empty=False, force_empty=False,
                     prompt=None, auto_bzip=auto_bzip) as output_dir:
        options["output_dir"] = output_dir

        with redirect_output(output_dir.get_path()):
            global global_network
            output = global_network.run(**options)

            return output
