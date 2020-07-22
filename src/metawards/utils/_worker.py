
from typing import Union as _Union
from typing import Dict as _Dict

from .._network import Network
from .._networks import Networks
from .._demographics import Demographics
from .._parameters import Parameters
from .._outputfiles import OutputFiles

__all__ = ["run_worker", "prepare_worker", "must_rebuild_network"]

global_network = None


def must_rebuild_network(network: _Union[Network, Networks],
                         params: Parameters,
                         demographics: Demographics) -> bool:
    """Return whether a change in parameters or demographics
       would force a rebuild of the passed network
    """
    if network is None or params is None:
        return True
    elif demographics is None and isinstance(network, Networks):
        return True
    elif demographics is not None:
        if len(demographics) <= 1 and isinstance(network, Networks):
            return True
        elif len(demographics) > 1 and isinstance(network, Network):
            return True

    if network.params.input_files != params.input_files:
        return True

    if demographics is None:
        return False

    if len(demographics) != len(network.demographics):
        return True

    if demographics.is_multi_network():
        # check if any of the networks has changed
        if not network.demographics.is_multi_network():
            return True

        for d1, d2 in zip(demographics, network.demographics):
            if d1.network != d2.network:
                return True

    return False


def prepare_worker(params: Parameters, demographics: Demographics,
                   options: _Dict[str, any]) -> _Union[Network, Networks]:
    """Prepare a worker to receive work to run a model using the passed
       parameters. This will build the network specified by the
       parameters and will store it in global memory ready to
       be used for a model run. Note that these are
       silent, printing nothing to stdout or stderr

       Parameters
       ----------
       params: Parameters
         Parameters used to build the network
       demographics: Demographics
         If not None, then demographics used to specialise the Network
         into Networks
    """
    global global_network

    max_nodes = options["max_nodes"]
    max_links = options["max_links"]
    nthreads = options["nthreads"]

    del options["max_nodes"]
    del options["max_links"]

    profiler = options["profiler"]

    from ._console import Console

    if must_rebuild_network(network=global_network, params=params,
                            demographics=demographics):

        Console.print("Must rebuild network...")

        if demographics is not None:
            network = demographics.build(params=params,
                                         population=options.get("population",
                                                                None),
                                         max_nodes=max_nodes,
                                         max_links=max_links,
                                         nthreads=nthreads,
                                         profiler=profiler)
        else:
            network = Network.build(params=params,
                                    population=options.get("population", None),
                                    profiler=profiler,
                                    nthreads=nthreads,
                                    max_nodes=max_nodes,
                                    max_links=max_links)

        global_network = network

    # always work in a copy
    network = global_network.copy()

    if params.adjustments is not None:
        Console.rule("Adjustable parameters to scan")
        Console.print("\n".join([f"* {x}" for x in params.adjustments]),
                      markdown=True)
        Console.rule()

    network.update(params=params, demographics=demographics,
                   nthreads=nthreads, profiler=profiler)

    return network


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
    demographics = arguments["demographics"]
    options = arguments["options"]

    # next, run the job, writing to output
    outdir = options["output_dir"]
    auto_bzip = options["auto_bzip"]
    del options["auto_bzip"]

    from ._console import Console

    with OutputFiles(outdir, check_empty=False, force_empty=False,
                     prompt=None, auto_bzip=auto_bzip) as output_dir:
        with Console.redirect_output(outdir=outdir, auto_bzip=auto_bzip):
            try:
                # first, build and prepare the Network(s). This is built once
                # from the parameters and demographics by loading files from
                # the filesystem, as sending this over the physical network
                # would be too expensive. Subsequent calls to this function
                # after the Network(s) has been built will call
                # network.update(params, demographics)
                network = prepare_worker(params=params,
                                         demographics=demographics,
                                         options=options)

                # if the user wanted to remove this directory then they would
                # have done so in the main process - no need to check again
                options["output_dir"] = output_dir

                output = network.run(**options)

                return output
            except Exception:
                Console.print_exception()
                raise
