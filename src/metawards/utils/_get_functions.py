
from typing import Union as _Union
from typing import Callable as _Callable
from typing import List as _List

from .._network import Network
from .._networks import Networks
from .._population import Population
from .._population import Populations
from .._infections import Infections
from .._outputfiles import OutputFiles
from .._workspace import Workspace
from ._profiler import Profiler

__all__ = ["get_functions", "get_model_loop_functions",
           "get_initialise_functions", "get_finalise_functions",
           "get_summary_functions",
           "accepts_stage", "MetaFunction",
           "call_function_on_network"]


MetaFunction = _Callable[..., None]


def accepts_stage(func: MetaFunction) -> bool:
    """Return whether the passed function accepts the "stage" argument,
       meaning that it can do different things for different day stages

       Parameters
       ----------
       func: function
         The function to be queries

       Returns
       -------
       result: bool
         Whether or not the function accepts the "stage" argument
    """
    import inspect
    return "stage" in inspect.signature(func).parameters


def get_functions(stage: str,
                  network: _Union[Network, Networks],
                  population: Population,
                  infections: Infections,
                  output_dir: OutputFiles,
                  workspace: Workspace,
                  iterator: MetaFunction,
                  extractor: MetaFunction,
                  mixer: MetaFunction,
                  mover: MetaFunction,
                  rngs, nthreads, profiler: Profiler,
                  trajectory: Populations = None,
                  results=None) -> _List[MetaFunction]:
    """Return the functions that must be called for the specified
       stage of the day;

       * "initialise": model initialisation. Called once before the
                       whole model run is performed
       * "setup": day setup. Called once at the start of the day.
                  Should be used to import new seeds, move populations
                  between demographics, move infected individuals
                  through disease stages etc. There is no calculation
                  performed at this stage.
       * "foi": foi calculation. Called to recalculate the force of infection
                (foi) for each ward in the network (and subnetworks).
                This is calculated based on the populations in each state
                in each ward in each demographic
       * "infect": Called to advance the outbreak by calculating
                   the number of new infections
       * "analyse": Called at the end of the day to analyse
                    the data and extract the results
       * "finalise": Called at the end of the model run to finalise
                     any outputs or produce overall summary files
       * "summary": Called at the end of lots of model runs, to write
                    overview summary files. Only the extractor has
                    a summary stage

       Parameters
       ----------
       stage: str
         The stage of the day/model for which to get the functions
       network: Network or Networks
         The network(s) to be modelled
       population: Population
         The population experiencing the outbreak
       infections: Infections
         Space to record the infections through the day
       iterator: function
         Iterator used to obtain the function used to advance
         the outbreak
       extractor: function
         Extractor used to analyse the data and output results
       mixer: function
         Mixer used to mix and merge data between different demographics
       mover: function
         Mover used to move populations between demographics
       rngs: list[random number generate pointers]
         Pointers to the random number generators to use for each thread
       nthreads: int
         The number of threads to use to run the model
       profiler: Profiler
         The profiler used to profile the calculation

       Returns
       -------
       functions: List[MetaFunction]
         The list of all functions that should be called for this
         stage of the day
    """

    stages = ["initialise", "setup", "foi", "infect",
              "analyse", "finalise", "summary"]

    if stage not in stages:
        raise ValueError(
            f"Cannot recognise the stage {stage}. Available stages "
            f"are {stages}")

    kwargs = {"stage": stage,
              "network": network,
              "population": population,
              "infections": infections,
              "rngs": rngs,
              "nthreads": nthreads,
              "profiler": profiler,
              "trajectory": trajectory,
              "results": results}

    if stage == "summary":
        funcs = extractor(**kwargs)
    else:
        funcs = mover(**kwargs) + iterator(**kwargs) + \
            mixer(**kwargs) + extractor(**kwargs)

    return funcs


def get_model_loop_functions(**kwargs) -> _List[MetaFunction]:
    """Convenience function that returns all of the functions
       that should be called during the model loop
       (i.e. the "setup", "foi", "infect" and "analyse" stages)

       Parameters
       ----------
       network: Network or Networks
         The network(s) to be modelled
       population: Population
         The population experiencing the outbreak
       infections: Infections
         Space to record the infections through the day
       iterator: function
         Iterator used to obtain the function used to advance
         the outbreak
       extractor: function
         Extractor used to analyse the data and output results
       mixer: function
         Mixer used to mix and merge data between different demographics
       mover: function
         Mover used to move populations between demographics
       rngs: list[random number generate pointers]
         Pointers to the random number generators to use for each thread
       nthreads: int
         The number of threads to use to run the model
       profiler: Profiler
         The profiler used to profile the calculation

       Returns
       -------
       functions: List[MetaFunction]
         The list of all functions that should be called for this
         stage of the day
    """

    funcs = get_functions(stage="setup", **kwargs)
    funcs += get_functions(stage="foi", **kwargs)
    funcs += get_functions(stage="infect", **kwargs)
    funcs += get_functions(stage="analyse", **kwargs)

    return funcs


def get_initialise_functions(**kwargs) -> _List[MetaFunction]:
    """Convenience function that returns all of the functions
       that should be called during the initialisation step
       of the model (e.g. the "initialise" stage)

       Parameters
       ----------
       network: Network or Networks
         The network(s) to be modelled
       population: Population
         The population experiencing the outbreak
       infections: Infections
         Space to record the infections through the day
       iterator: function
         Iterator used to obtain the function used to advance
         the outbreak
       extractor: function
         Extractor used to analyse the data and output results
       mixer: function
         Mixer used to mix and merge data between different demographics
       mover: function
         Mover used to move populations between demographics
       rngs: list[random number generate pointers]
         Pointers to the random number generators to use for each thread
       nthreads: int
         The number of threads to use to run the model
       profiler: Profiler
         The profiler used to profile the calculation

       Returns
       -------
       functions: List[MetaFunction]
         The list of all functions that should be called for this
         stage of the day
    """
    return get_functions(stage="initialise", **kwargs)


def get_finalise_functions(trajectory: Populations,
                           **kwargs) -> _List[MetaFunction]:
    """Convenience function that returns all of the functions
       that should be called during the finalisation step
       of the model (e.g. the "finalise" stage)

       Parameters
       ----------
       network: Network or Networks
         The network(s) to be modelled
       population: Population
         The population experiencing the outbreak
       trajectory: Populations
         The trajectory of populations over time
       infections: Infections
         Space to record the infections through the day
       iterator: function
         Iterator used to obtain the function used to advance
         the outbreak
       extractor: function
         Extractor used to analyse the data and output results
       mixer: function
         Mixer used to mix and merge data between different demographics
       mover: function
         Mover used to move populations between demographics
       rngs: list[random number generate pointers]
         Pointers to the random number generators to use for each thread
       nthreads: int
         The number of threads to use to run the model
       profiler: Profiler
         The profiler used to profile the calculation

       Returns
       -------
       functions: List[MetaFunction]
         The list of all functions that should be called for this
         stage of the day
    """
    return get_functions(stage="finalise", **kwargs)


def get_summary_functions(network: _Union[Network, Networks],
                          results, output_dir: OutputFiles,
                          extractor: MetaFunction,
                          nthreads: int = 1, **kwargs
                          ):
    """Convenience function that returns all of the functions
       that should be called during the summary report
       stage of the simulation
    """
    kwargs["workspace"] = Workspace()
    kwargs["infections"] = Infections()
    kwargs["population"] = Population()
    kwargs["iterator"] = None
    kwargs["mixer"] = None
    kwargs["mover"] = None
    kwargs["rngs"] = None
    kwargs["profiler"] = None

    return get_functions(stage="summary", network=network,
                         output_dir=output_dir, results=results,
                         extractor=extractor, nthreads=nthreads, **kwargs)


def call_function_on_network(network: _Union[Network, Networks],
                             infections: Infections,
                             workspace: Workspace,
                             population: Population,
                             func: MetaFunction = None,
                             parallel: MetaFunction = None,
                             nthreads: int = 1,
                             switch_to_parallel: int = 2,
                             call_on_overall: bool = False,
                             **kwargs):
    """Call either 'func' or 'parallel' (depending on the
       number of threads, nthreads) on the passed Network,
       or on all demographic subnetworks

       Parameters
       ----------
       network: Network or Networks
         The network that is being modelled
       nthreads: int
         The number of threads to use to perform the work
       func: MetaFunction
         Function that performs the work in serial
       parallel: MetaFunction
         Function that performs the work in parallel
       switch_to_parallel: int
         Use the parallel function when nthreads is greater or equal
         to this value
    """
    if parallel is not None:
        if func is None or nthreads >= switch_to_parallel:
            kwargs["nthreads"] = nthreads
            func = parallel

    if isinstance(network, Networks):
        # call the function on all of the demographic sub-networks
        for i, subnet in enumerate(network.subnets):
            subinf = infections.subinfs[i]
            subwork = workspace.subspaces[i]
            subpop = population.subpops[i]

            func(network=subnet, infections=subinf,
                 population=subpop, workspace=subwork,
                 **kwargs)

        if call_on_overall:
            func(network=network.overall, infections=infections,
                 population=population, workspace=workspace,
                 **kwargs)
    else:
        func(network=network, infections=infections,
             population=population, workspace=workspace,
             **kwargs)
