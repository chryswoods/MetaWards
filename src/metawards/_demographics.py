
from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import List as _List
from typing import Dict as _Dict
from typing import Union as _Union
import os as _os
import pathlib as _pathlib

from ._demographic import Demographic
from ._network import Network

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
    from metawards.utils import safe_eval_number

    if value is None:
        return 0.0

    elif isinstance(value, list):
        lst = []
        for v in value:
            lst.append(safe_eval_number(v))
        return lst

    elif isinstance(value, dict):
        d = []
        for k, v in value.items():
            d[k] = safe_eval_number(v)

        return d
    else:
        return safe_eval_number(value)


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

        return f"Demographics {self._name}\n" \
               f"loaded from {self._filename}\n" \
               f"version: {self._version}\n" \
               f"author(s): {self._authors}\n" \
               f"contact(s): {self._contacts}\n" \
               f"references(s): {self._references}\n" \
               f"repository: {self._repository}\n" \
               f"repository_branch: {self._repository_branch}\n" \
               f"repository_version: {self._repository_version}\n" \
               f"demographics = [\n  {d}\n]"

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
            with open(json_file, "r") as FILE:
                import json
                data = json.load(FILE)

        except Exception as e:
            from .utils._console import Console
            Console.error(f"""
Could not find the demographics file {json_file}. "Either it does not exist
or was corrupted. Error was {e.__class__} {e}. To download the disease data
follow the instructions at
[https://metawards.org/model_data](https://metawards.org/model_data).""")

            raise FileNotFoundError(f"Could not find or read {json_file}: "
                                    f"{e.__class__} {e}")

        json_dir = os.path.split(os.path.abspath(json_file))[0]

        demographics = data.get("demographics", [])
        work_ratios = data.get("work_ratios", [])
        play_ratios = data.get("play_ratios", [])
        random_seed = data.get("random_seed", None)
        diseases = data.get("diseases", None)

        if diseases is None:
            diseases = len(demographics) * [None]
        else:
            from ._disease import Disease
            diseases = [Disease.load(x, folder=json_dir) if x is not None
                        else None for x in diseases]

        if (len(demographics) != len(work_ratios) or
                len(demographics) != len(play_ratios) or
                len(demographics) != len(diseases)):
            raise ValueError(
                f"The number of work_ratios ({len(work_ratios)}) must "
                f"equal to number of play_ratios "
                f"({len(play_ratios)}) which must equal the number "
                f"of diseases ({len(diseases)}) which must equal "
                f"the number of demographics ({len(demographics)})")

        demos = Demographics(random_seed=random_seed,
                             _name=name,
                             _authors=data.get("author(s)", "unknown"),
                             _contacts=data.get("contact(s)", "unknown"),
                             _references=data.get("reference(s)", "none"),
                             _filename=json_file,
                             _repository=repository,
                             _repository_branch=repository_branch,
                             _repository_version=repository_version)

        for i in range(0, len(demographics)):
            demographic = Demographic(name=demographics[i],
                                      work_ratio=_get_value(work_ratios[i]),
                                      play_ratio=_get_value(play_ratios[i]),
                                      disease=diseases[i])
            demos.add(demographic)

        return demos

    def specialise(self, network: Network, profiler=None,
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
