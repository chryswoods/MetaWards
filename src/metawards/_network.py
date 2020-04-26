
from dataclasses import dataclass as _dataclass
from typing import List as _List

from ._parameters import Parameters
from ._nodes import Nodes
from ._links import Links
from ._population import Population
from ._outputfiles import OutputFiles

__all__ = ["Network"]


@_dataclass
class Network:
    """This class represents a network of wards. The network comprises
       nodes (representing wards), connected with links which represent
       work (predictable) links. There are also additional links for
       play (unpredictable/random) and weekend
    """

    #: The list of nodes (wards) in the network
    nodes: Nodes = None
    #: The links between nodes (work)
    to_links: Links = None
    #: The links between nodes (play)
    play: Links = None
    #: The links between nodes (weekend)
    weekend: Links = None

    #: The number of nodes in the network
    nnodes: int = 0
    #: The number of links in the network
    nlinks: int = 0
    #: The number of play links in the network
    plinks: int = 0

    #: The maximum allowable number of nodes in the network
    max_nodes: int = 16384
    #: The maximum allowable number of links in the network
    max_links: int = 4194304

    #: To seed provides additional seeding information
    to_seed: _List[int] = None

    #: The parameters used to generate this network
    params: Parameters = None

    @staticmethod
    def build(params: Parameters,
              calculate_distances: bool = True,
              build_function=None,
              distance_function=None,
              max_nodes: int = 16384,
              max_links: int = 4194304,
              nthreads: int = 1,
              profile: bool = True,
              profiler=None):
        """Builds and returns a new Network that is described by the
           passed parameters. If 'calculate_distances' is True, then
           this will also read in the ward positions and add
           the distances between the links.

           Optionally you can supply your own function to build the network,
           by supplying 'build_function'. By default, this is
           metawards.utils.build_wards_network.

           Optionally you can supply your own function to read and
           calculate the distances by supplying 'build_function'.
           By default this is metawards.add_wards_network_distance

           The network is built in allocated memory, so you need to specify
           the maximum possible number of nodes and links. The memory buffers
           will be shrunk back after building.
        """
        if profile:
            if profiler is None:
                from .utils import Profiler
                p = Profiler()
            else:
                p = profiler
        else:
            from .utils import NullProfiler
            p = NullProfiler()

        p = p.start("Network.build")

        if build_function is None:
            from .utils import build_wards_network
            build_function = build_wards_network

        p = p.start("build_function")
        network = build_function(params=params,
                                 profiler=p,
                                 max_nodes=max_nodes,
                                 max_links=max_links,
                                 nthreads=nthreads)
        p = p.stop()

        # sanity-check that the network makes sense - there are specific
        # requirements for the data layout
        network.assert_sane(profiler=p)

        if calculate_distances:
            p = p.start("add_distances")
            network.add_distances(distance_function=distance_function,
                                  nthreads=nthreads, profiler=p)
            p = p.stop()

        if params.input_files.seed:
            from .utils import read_done_file
            p = p.start("read_done_file")
            to_seed = read_done_file(params.input_files.seed)
            nseeds = len(to_seed)

            print(to_seed)
            print(f"Number of seeds equals {nseeds}")
            network.to_seed = to_seed
            p = p.stop()

        # By default, we initialise the network ready for a run,
        # namely make sure everything is reset and the population
        # is at work
        print("Reset everything...")
        p = p.start("reset_everything")
        network.reset_everything(nthreads=nthreads, profiler=p)
        p = p.stop()

        print("Rescale play matrix...")
        p = p.start("rescale_play_matrix")
        network.rescale_play_matrix(nthreads=nthreads, profiler=p)
        p = p.stop()

        print("Move population from play to work...")
        p = p.start("move_from_play_to_work")
        network.move_from_play_to_work(nthreads=nthreads, profiler=p)
        p = p.stop()

        if not p.is_null():
            p = p.stop()
            print(p)

        return network

    def assert_sane(self, profiler: None):
        """Assert that this network is sane. This checks that the network
           is laid out correctly in memory and that it doesn't have
           anything unexpected. Checking here will prevent us from having
           to check every time the network is accessed
        """
        from .utils import assert_sane_network
        if profiler is None:
            from .profiler import NullProfiler
            profiler = NullProfiler()

        assert_sane_network(network=self, profiler=profiler)

    def add_distances(self, distance_function=None, nthreads: int = 1,
                      profiler=None):
        """Read in the positions of all of the nodes (wards) and calculate
           the distances of the links.

           Optionally you can specify the function to use to
           read the positions and calculate the distances.
           By default this is mw.utils.add_wards_network_distance
        """
        if distance_function is None:
            from .utils import add_wards_network_distance
            distance_function = add_wards_network_distance

        distance_function(self, nthreads=nthreads)

        # now need to update the dynamic distance cutoff based on the
        # maximum distance between nodes
        print("Get min/max distances...")
        (_mindist, maxdist) = self.get_min_max_distances(nthreads=nthreads)

        self.params.dyn_dist_cutoff = maxdist + 1

    def initialise_infections(self, nthreads: int = 1):
        """Initialise and return the space that will be used
           to track infections
        """
        from ._infections import Infections
        return Infections.build(network=self)

    def get_min_max_distances(self, nthreads: int = 1,
                              profiler=None):
        """Calculate and return the minimum and maximum distances
           between nodes in the network
        """
        try:
            return self._min_max_distances
        except Exception:
            pass

        from .utils import get_min_max_distances
        self._min_max_distances = get_min_max_distances(network=self,
                                                        nthreads=nthreads)

        return self._min_max_distances

    def reset_everything(self, nthreads: int = 1,
                         profiler=None):
        """Resets the network ready for a new run of the model"""
        from .utils import reset_everything
        reset_everything(network=self, nthreads=nthreads, profiler=profiler)

    def update(self, params: Parameters,
               nthreads: int = 1, profile: bool = False):
        """Update this network with a new set of parameters.
           This is used to update the parameters for the network
           for a new run. The network will be reset
           and ready for a new run.
        """
        if profile:
            from .utils import Profiler
            p = Profiler()
        else:
            from .utils import NullProfiler
            p = NullProfiler()

        p = p.start("Network.update")

        self.params = params

        p = p.start("reset_everything")
        self.reset_everything(nthreads=nthreads, profiler=p)
        p = p.stop()

        p = p.start("rescale_play_matrix")
        self.rescale_play_matrix(nthreads=nthreads, profiler=p)
        p = p.stop()

        p = p.start("move_from_play_to_work")
        self.move_from_play_to_work(nthreads=nthreads, profiler=p)
        p = p.stop()

        p = p.stop()

        if profile:
            print(p)

    def rescale_play_matrix(self, nthreads: int = 1,
                            profiler=None):
        """Rescale the play matrix"""
        from .utils import rescale_play_matrix
        rescale_play_matrix(network=self, nthreads=nthreads, profiler=profiler)

    def move_from_play_to_work(self, nthreads: int = 1,
                               profiler=None):
        """Move the population from play to work"""
        from .utils import move_population_from_play_to_work
        move_population_from_play_to_work(network=self, nthreads=nthreads,
                                          profiler=profiler)

    def run(self, population: Population,
            output_dir: OutputFiles,
            seed: int = None,
            nsteps: int = None,
            profile: bool = True,
            s: int = None,
            nthreads: int = None,
            iterator=None,
            extractor=None,
            profiler=None):
        """Run the model simulation for the passed population.
           The random number seed is given in 'seed'. If this
           is None, then a random seed is used.

           All output files are written to 'output_dir'

           The simulation will continue until the infection has
           died out or until 'nsteps' has passed (keep as 'None'
           to prevent exiting early).

           s is used to select the 'to_seed' entry to seed
           the nodes

           Parameters
           ----------
           population: Population
             The initial population at the start of the model outbreak.
             This is also used to set start date and day of the model
             outbreak
           output_dir: OutputFiles
             The directory to write all of the output into
           seed: int
             The random number seed used for this model run. If this is
             None then a very random random number seed will be used
           nsteps: int
             The maximum number of steps to run in the outbreak. If None
             then run until the outbreak has finished
           profile: bool
             Whether or not to profile the model run and print out the
             results
           profiler: Profiler
             The profiler to use - a new one is created if one isn't passed
           s: int
             Index of the seeding parameter to use
           nthreads: int
             Number of threads over which to parallelise this model run
           iterator: function
             Function that is called at each iteration to get the functions
             that are used to advance the model
           extractor: function
             Function that is called at each iteration to get the functions
             that are used to extract data for analysis or writing to files
        """
        # Create the random number generator
        from .utils._ran_binomial import seed_ran_binomial, ran_binomial

        rng = seed_ran_binomial(seed=seed)

        # Print the first five random numbers so that we can
        # compare to other codes/runs, and be sure that we are
        # generating the same random sequence
        randnums = []
        for i in range(0, 5):
            randnums.append(str(ran_binomial(rng, 0.5, 100)))

        print(f"First five random numbers equal {', '.join(randnums)}")
        randnums = None

        if nthreads is None:
            from .utils._parallel import get_available_num_threads
            nthreads = get_available_num_threads()

        print(f"Number of threads used equals {nthreads}")

        from .utils._parallel import create_thread_generators
        rngs = create_thread_generators(rng, nthreads)

        # Create space to hold the results of the simulation
        print("Initialise infections...")
        infections = self.initialise_infections()

        from .utils import run_model
        population = run_model(network=self,
                               population=population,
                               infections=infections,
                               rngs=rngs, s=s, output_dir=output_dir,
                               nsteps=nsteps,
                               profile=profile, nthreads=nthreads,
                               profiler=profiler,
                               iterator=iterator, extractor=extractor)

        return population
