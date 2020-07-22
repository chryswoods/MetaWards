from __future__ import annotations

from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import List as _List
from typing import Dict as _Dict
from typing import Union as _Union
import os as _os
import pathlib as _pathlib

from ._demographic import Demographic
from ._network import Network

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .utils._profiler import Profiler
    from .utils._profiler import Networks
    from ._population import Population
    from ._parameters import Parameters

__all__ = ["Demographics", "DemographicID", "DemographicIDs"]

_default_demographics_path = _os.path.join(_pathlib.Path.home(),
                                           "GitHub", "MetaWardsData")

_default_folder_name = "demographics"

DemographicID = _Union[str, int]
DemographicIDs = _List[DemographicID]


def _get_value(value):
    """Extract a numeric value from the passed value - this is used
       to allow the demographics.json file to store numbers is
       a variety of formats
    """
    from ._interpret import Interpret

    if value is None:
        return 0.0

    elif isinstance(value, list):
        lst = []
        for v in value:
            lst.append(Interpret.number(v))
        return lst

    elif isinstance(value, dict):
        d = []
        for k, v in value.items():
            d[k] = Interpret.number(v)

        return d
    else:
        return Interpret.number(value)


@_dataclass(eq=False)
class Demographics:
    """This class holds metadata about all of the demographics
       being modelled
    """
    #: The list of individual Demographic objects, one for each
    #: demographic being modelled
    demographics: _List[Demographic] = _field(default_factory=list)

    #: The random seed to used when using any random number generator
    #: to resolve decisions needed when allocating individuals to
    #: demographics. This is set here so that the Demographics
    #: are uniquely determined and reproducible across runs
    random_seed: int = None

    #: The interaction matrix between demographics. This should
    #: be a list of lists that shows how demographic 'i' affects
    #: demographic 'j'
    interaction_matrix: _List[_List[int]] = None

    #: Map from index to names of demographics - enables lookup by name
    _names: _Dict[str, int] = _field(default_factory=dict)

    _name: str = None
    _version: str = None
    _authors: str = None
    _contacts: str = None
    _references: str = None
    _filename: str = None
    _repository: str = None
    _repository_version: str = None
    _repository_branch: str = None

    def __str__(self):
        d = "\n  ".join([str(x) for x in self.demographics])
        return f"[\n  {d}\n]"

    def __len__(self):
        return len(self.demographics)

    def __eq__(self, other):
        if not isinstance(other, Demographics):
            return False

        elif len(self) != len(other):
            return False

        else:
            for name, index in self._names.items():
                if other._names.get(name, None) != index:
                    return False

                if self.demographics[index] != other.demographics[index]:
                    return False

            return True

    def __getitem__(self, item):
        if isinstance(item, str):
            # Lookup by name
            return self.demographics[self.get_index(item)]
        else:
            # Lookup by index
            return self.demographics[item]

    def copy(self):
        """Return a copy of this demographics object that should
           allow a safe reset between runs. This deepcopies things
           that may change, while shallow copying things that won't
        """
        from copy import copy, deepcopy
        demographics = copy(self)

        demographics.interaction_matrix = deepcopy(self.interaction_matrix)
        demographics.demographics = copy(self.demographics)

        return demographics

    def add(self, demographic: Demographic):
        """Add a demographic to the set to be modelled"""
        if demographic.name is None:
            raise ValueError(
                f"You can only add named demographics to the set.")

        if demographic.name in self._names:
            raise ValueError(
                f"There is already a demographic called "
                f"{demographic.name} in this set. Please rename "
                f"and try again.")

        self.demographics.append(demographic)
        self._names[demographic.name] = len(self.demographics) - 1

    def get_name(self, item):
        """Return the name of the demographic at 'item'"""
        return self.demographics[self.get_index(item)].name

    def get_index(self, item):
        """Return the index of the passed item"""
        try:
            item = int(item)
        except Exception:
            pass

        if isinstance(item, str):
            try:
                return self._names[item]
            except Exception:
                pass

        elif isinstance(item, int):
            try:
                if self.demographics[item] is not None:
                    return item
            except Exception:
                pass

        elif isinstance(item, Demographic):
            for i, d in enumerate(self.demographics):
                if item == d:
                    return i

        # haven't found the item
        raise KeyError(f"There is no demographic is this set that "
                       f"matches {item}. Available names are "
                       f"{self._names}. Available indexes are "
                       f"0 -> {len(self._names)}")

    def uses_named_network(self):
        """Return whether or not at least one of these demographics
           specifies the use of a named network model
        """
        for demographic in self.demographics:
            if demographic.network is not None:
                return True

        return False

    def is_multi_network(self):
        """Return whether or not these demographics need to use multiple
           custom networks (e.g. refer to different network models)
        """
        if len(self) <= 1:
            return False
        else:
            first_network = self.demographics[0].network

            for demographic in self.demographics[1:]:
                if first_network != demographic.network:
                    return True

            return False

    @staticmethod
    def load(name: str = None,
             repository: str = None,
             folder: str = _default_folder_name,
             filename: str = None):
        """Load the parameters for the specified set of demographics.
           This will look for a file called f"{name}.json"
           in the directory f"{repository}/{folder}/{name}.json"

           By default this will load nothing.

           Alternatively you can provide the full path to the
           json file via the "filename" argument

           Parameters
           ----------
           name: str
             The name of the demographics to load. This is the name that
             will be searched for in the METAWARDSDATA diseases directory
           repository: str
             The location of the cloned METAWARDSDATA repository
           folder: str
             The name of the folder within the METAWARDSDATA repository
             that contains the diseases
           filename: str
             The name of the file to load the disease from - this directly
             loads this file without searching through the METAWARDSDATA
             repository

           Returns
           -------
           demographics: Demographics
             The constructed and validated demographics
        """

        repository_version = None
        repository_branch = None

        if filename is None:
            import os
            if os.path.exists(name):
                filename = name
            elif os.path.exists(f"{name}.json"):
                filename = f"{name}.json"

        import os

        if filename is None:
            if repository is None:
                repository = os.getenv("METAWARDSDATA")
                if repository is None:
                    repository = _default_demographics_path

            filename = os.path.join(repository, folder,
                                    f"{name}.json")

            from ._parameters import get_repository_version
            v = get_repository_version(repository)
            repository = v["repository"]
            repository_version = v["version"]
            repository_branch = v["branch"]

        json_file = filename

        try:
            demographics = Demographics.from_json(json_file)
        except Exception as e:
            from .utils._console import Console
            Console.error(f"""
Could not find the demographics file {json_file}. "Either it does not exist
or was corrupted. Error was {e.__class__} {e}. To download the disease data
follow the instructions at
[https://metawards.org/model_data](https://metawards.org/model_data).""")

            raise FileNotFoundError(f"Could not find or read {json_file}: "
                                    f"{e.__class__} {e}")

        demographics._name = name
        demographics._filename = json_file
        demographics._repository = repository
        demographics._repository_branch = repository_branch
        demographics._repository_version = repository_version

        return demographics

    def to_data(self):
        """Return a data dictionary for this object that can
           be serialised to json
        """
        data = {}

        if self.demographics is None:
            return data

        default = [1.0] * len(self.demographics)
        all_none = [None] * len(self.demographics)

        def _get_filename(x):
            if x is None:
                return None
            elif isinstance(x, str):
                import os
                if os.path.exists(x):
                    from pathlib import Path
                    return str(Path(x).expanduser().absolute())
                else:
                    return x
            else:
                if x._filename is None:
                    raise IOError(f"Cannot locate file for {x}")

                return _get_filename(x._filename)

        demographics = [str(x.name) for x in self.demographics]
        work_ratios = [float(x.work_ratio) for x in self.demographics]
        play_ratios = [float(x.play_ratio) for x in self.demographics]
        diseases = [_get_filename(x.disease) for x in self.demographics]
        networks = [_get_filename(x.network) for x in self.demographics]

        data["demographics"] = demographics

        if work_ratios != default:
            data["work_ratios"] = work_ratios

        if play_ratios != default:
            data["play_ratios"] = play_ratios

        if self.random_seed is not None:
            data["random_seed"] = int(self.random_seed)

        if diseases != all_none:
            data["diseases"] = diseases

        if networks != all_none:
            data["networks"] = networks

        return data

    def to_json(self, filename: str = None, indent: int = None,
                auto_bzip: bool = True) -> str:
        """Serialise the Demographics to JSON. This will write to a file
           if filename is set, otherwise it will return a JSON string.

           Parameters
           ----------
           filename: str
             The name of the file to write the JSON to. The absolute
             path to the written file will be returned. If filename is None
             then this will serialise to a JSON string which will be
             returned.
           indent: int
             The number of spaces of indent to use when writing the json
           auto_bzip: bool
             Whether or not to automatically bzip2 the written json file

           Returns
           -------
           str
             Returns either the absolute path to the written file, or
             the json-serialised string
        """
        import json

        if indent is not None:
            indent = int(indent)

        if filename is None:
            return json.dumps(self.to_data(), indent=indent)
        else:
            from pathlib import Path
            filename = str(Path(filename).expanduser().resolve().absolute())

            if auto_bzip:
                if not filename.endswith(".bz2"):
                    filename += ".bz2"

                import bz2
                with bz2.open(filename, "wt") as FILE:
                    try:
                        json.dump(self.to_data(), FILE, indent=indent)
                    except Exception:
                        import os
                        FILE.close()
                        os.unlink(filename)
                        raise
            else:
                with open(filename, "w") as FILE:
                    try:
                        json.dump(self.to_data(), FILE, indent=indent)
                    except Exception:
                        import os
                        FILE.close()
                        os.unlink(filename)
                        raise

            return filename

    @staticmethod
    def from_data(data, json_dir=None) -> Demographics:
        """Construct and return a Demographics object constructed
           from a (json-deserialised) data dictionary
        """
        demographics = data.get("demographics", [])
        work_ratios = data.get("work_ratios", [1.0] * len(demographics))
        play_ratios = data.get("play_ratios", [1.0] * len(demographics))
        random_seed = data.get("random_seed", None)
        diseases = data.get("diseases", None)
        networks = data.get("networks", None)

        if diseases is None:
            diseases = len(demographics) * [None]
        else:
            from ._disease import Disease
            diseases = [Disease.load(x, folder=json_dir) if x is not None
                        else None for x in diseases]

        if networks is None:
            networks = len(demographics) * [None]
        else:
            from ._inputfiles import InputFiles
            networks = [InputFiles.load(x, folder=json_dir) if x is not None
                        else None for x in networks]

        if (len(demographics) != len(work_ratios) or
                len(demographics) != len(play_ratios) or
                len(demographics) != len(diseases) or
                len(demographics) != len(networks)):
            raise ValueError(
                f"The number of work_ratios ({len(work_ratios)}) must "
                f"equal to number of play_ratios "
                f"({len(play_ratios)}) which must equal the number "
                f"of diseases ({len(diseases)}) which must equal "
                f"the number of demographics ({len(demographics)}), "
                f"which must equal the number of networks ({len(networks)}).")

        demos = Demographics(random_seed=random_seed,
                             _authors=data.get("author(s)", None),
                             _contacts=data.get("contact(s)", None),
                             _references=data.get("reference(s)", None))

        for i in range(0, len(demographics)):
            demographic = Demographic(name=demographics[i],
                                      work_ratio=_get_value(work_ratios[i]),
                                      play_ratio=_get_value(play_ratios[i]),
                                      disease=diseases[i],
                                      network=networks[i])
            demos.add(demographic)

        return demos

    @staticmethod
    def from_json(s: str):
        """Construct and return Demographics loaded from the passed
           json file
        """
        import os
        import json

        json_dir = None

        if os.path.exists(s):
            json_dir = os.path.split(os.path.abspath(s))[0]

            try:
                import bz2
                with bz2.open(s, "rt") as FILE:
                    data = json.load(FILE)
            except Exception:
                data = None

            if data is None:
                with open(s, "rt") as FILE:
                    data = json.load(FILE)
        else:
            try:
                data = json.loads(s)
            except Exception:
                data = None

        if data is None:
            from .utils._console import Console
            Console.error(f"Unable to load Demographics from '{s}'. Check that "
                          f"this is valid JSON or that the file exists.")

            raise IOError(f"Cannot load Disease from '{s}'")

        return Demographics.from_data(data, json_dir=json_dir)

    def build(self, params: Parameters, population: Population = None,
              max_nodes: int = 16384,
              max_links: int = 4194304,
              nthreads: int = 1,
              profiler: Profiler = None) -> _Union[Network, Networks]:
        """Build the set of networks described by these demographics
           and the passed parameters

           Parameters
           ----------
           params: Parameters
             Parameters used to help build the model networks
           max_nodes: int
             Initial guess for the maximum number of nodes(wards)
           max_links: int
             Initial guess for the maximum number of links between wards
           profiler: Profiler
             Profiler used to profile the specialisation
           nthreads: int
             Number of threads over which to parallelise the work

           Returns
           -------
           Network or Networks
             The set of Networks that represent the model run over the
             full set of different demographics(or Network if there is
             just a single demographic)
        """
        from .utils._console import Console

        if len(self) == 0:
            return Network.build(params=params, population=population,
                                 max_nodes=max_nodes, max_links=max_links,
                                 nthreads=nthreads, profiler=profiler)

        if len(self) == 1:
            demographic = self[0]

            if demographic.adjustment is not None:
                demographic.adjustment.adjust(params)

            if demographic.disease is not None:
                params.disease_params = demographic.disease

            if demographic.network is not None:
                params.input_files = demographic.network

            network = Network.build(params=params, population=population,
                                    max_nodes=max_nodes, max_links=max_links,
                                    nthreads=nthreads, profiler=profiler)

            if demographic.work_ratio != 1.0 or demographic.play_ratio != 1.0:
                network.scale_susceptibles(work_ratio=demographic.work_ratio,
                                           play_ratio=demographic.play_ratio)

            network.name = demographic.name
            return network

        if not self.uses_named_network():
            # build a single network that is then specialised
            network = Network.build(params=params, population=population,
                                    max_nodes=max_nodes, max_links=max_links,
                                    nthreads=nthreads, profiler=profiler)

            Console.rule("Specialising into demographics")
            return self.specialise(network=network, profiler=profiler,
                                   nthreads=nthreads)

        # need to load each network separately, and then merge
        wards = {}
        shared_wards = {}

        from ._wards import Wards
        from copy import deepcopy

        for i, demographic in enumerate(self.demographics):
            if demographic.network is None:
                input_files = params.input_files
            else:
                input_files = demographic.network

            if input_files not in shared_wards:
                if input_files.is_wards_data:
                    wards[input_files] = Wards.from_json(
                        input_files.wards_data)
                else:
                    network_params = deepcopy(params)
                    network_params.input_files = input_files
                    network = Network.build(params=network_params,
                                            population=population,
                                            max_nodes=max_nodes,
                                            max_links=max_links,
                                            nthreads=nthreads,
                                            profiler=profiler)
                    wards[input_files] = network.to_wards()

                shared_wards[input_files] = [i]
            else:
                shared_wards[input_files].append(i)

        wardss = [None] * len(self)
        input_files = [None] * len(self)

        for key, value in shared_wards.items():
            if len(value) > 1:
                # this is a combined network - need to divide the population
                # between multiple demographics. First create the network
                # and then use specialise to divide the population
                # between the demographics
                w = wards[key]
                network = Network.from_wards(w, params=params,
                                             nthreads=nthreads)

                ds = Demographics(
                    demographics=[deepcopy(self.demographics[x])
                                  for x in value])

                for d in ds:
                    d.network = None

                network = ds.specialise(network=network, nthreads=nthreads)

                for i, idx in enumerate(value):
                    wardss[idx] = network.subnets[i].to_wards(
                        nthreads=nthreads)
                    input_files[idx] = key
            else:
                i = value[0]
                demographic = self.demographics[i]
                w = wards[key]

                if demographic.work_ratio != 1.0 or \
                        demographic.play_ratio != 1.0:
                    w = w.scale(work_ratio=demographic.work_ratio,
                                play_ratio=demographic.play_ratio)

                wardss[i] = w
                input_files[i] = key

        total_pop = worker_pop = player_pop = 0

        for wards in wardss:
            total_pop += wards.population()
            worker_pop += wards.num_workers()
            player_pop += wards.num_players()

        overall, wardss = Wards.harmonise(wardss)

        assert overall.population() == total_pop
        assert overall.num_workers() == worker_pop
        assert overall.num_players() == player_pop

        overall = Network.from_wards(overall, params=params,
                                     nthreads=nthreads)

        subnets = [None] * len(self)

        total_pop = worker_pop = player_pop = 0

        for i, demographic in enumerate(self.demographics):
            subparams = deepcopy(params)
            subparams.input_files = input_files[i]

            if demographic.adjustment is not None:
                demographic.adjustment.adjust(subparams)

            subnets[i] = Network.from_wards(wardss[i],
                                            params=subparams,
                                            nthreads=nthreads)
            subnets[i].name = demographic.name
            total_pop += subnets[i].population
            worker_pop += subnets[i].work_population
            player_pop += subnets[i].play_population

        assert total_pop == overall.population
        assert worker_pop == overall.work_population
        assert player_pop == overall.play_population

        from ._networks import Networks

        networks = Networks()
        networks.overall = overall
        networks.subnets = subnets
        networks.demographics = deepcopy(self)

        return networks

    def specialise(self, network: Network, profiler: Profiler = None,
                   nthreads: int = 1):
        """Build the set of networks that will model this set
           of demographics applied to the passed Network.

           Parameters
           ----------
           network: Network
             The overall population model - this contains the base
             parameters, wards, work and play links that define
             the model outbreak
           profiler: Profiler
             Profiler used to profile the specialisation
           nthreads: int
             Number of threads over which to parallelise the work

           Returns
           -------
           networks: Networks
             The set of Networks that represent the model run over the
             full set of different demographics
        """
        if len(self) == 0:
            return network
        else:
            from ._networks import Networks
            return Networks.build(network=network, demographics=self,
                                  profiler=profiler, nthreads=nthreads)
