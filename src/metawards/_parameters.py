
from dataclasses import dataclass as _dataclass
from typing import List as _List, Dict as _Dict

from ._inputfiles import InputFiles
from ._disease import Disease
from ._variableset import VariableSets, VariableSet


__all__ = ["Parameters", "get_repository_version", "get_repository"]

_default_folder_name = "parameters"


_repositories = {}


def get_repository(repository: str = None, error_on_missing=True):
    """Return the full path to the passed MetaWardsData repository.
       This will return the default repository if None is passed

       Returns a tuple of the repository path and version information
    """
    import os
    from pathlib import Path

    if repository is None:
        repository = os.getenv("METAWARDSDATA", None)

        if repository is None:
            repository = os.path.join(Path.home(),
                                      "GitHub", "MetaWardsData")

    repository = os.path.expanduser(os.path.expandvars(repository))
    repository = str(Path(repository).absolute().resolve())

    if not os.path.exists(repository) or not os.path.isdir(repository):
        if error_on_missing:
            raise FileNotFoundError(
                f"Cannot find the MetaWardsData repository "
                f"at {repository}. Please follow the instructions "
                f"at https://metawards.org/model_data.html to download "
                f"and install the model data.")
        else:
            return (None, None)

    v = get_repository_version(repository)
    return (repository, v)


def generate_repository_version(repository):
    """Try to run the './version' script within the passed repository,
       to generate the required 'version.txt' file
    """
    import subprocess
    import os

    if repository is not None:
        script = os.path.join(repository, "version")
        subprocess.run(script, cwd=repository, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)


def get_repository_version(repository: str):
    """Read and return the Git version of the passed repository

       Parameters
       ----------
       repository: str
         The full path to the repository whose version should be obtained.
         If this is 'None' then the default repository will be used
         ($METAWARDSDATA or $HOME/GitHub/MetaWardsData)

       Returns
       -------
       version_data: dict
         A dictionary containing version information for the repository
    """
    global _repositories

    if repository is None:
        return None

    if repository in _repositories:
        return _repositories[repository]

    import os

    filename = os.path.join(repository, "version.txt")

    try:
        with open(filename) as FILE:
            import json
            version = json.load(FILE)
            _repositories[repository] = version
            return version
    except Exception:
        pass

    # could not get the version, so see if we have permission
    # to run the 'version' program
    try:
        generate_repository_version(repository)

        with open(filename) as FILE:
            import json
            version = json.load(FILE)
            version["filepath"] = repository
            _repositories[repository] = version
            return version
    except Exception:
        from .utils._console import Console
        Console.error(f"""
Could not find the repository version info in {filename}. Please make sure
that you have run './version' in that repository to generate the version
info.""")
        _repositories[repository] = {"filepath": repository,
                                     "repository": "unknown",
                                     "version": "unknown",
                                     "branch": "unknown",
                                     "is_dirty": True}
        return _repositories[repository]


@_dataclass
class Parameters:
    """The full set of Parameters that are used to control the model
       outbreak over a Network. The combination of a Network and
       a Parameters defines the model outbreak.

       Load the Parameters using the Parameters.load function, and
       then add extra data using the various "set" and "add" functions,
       e.g.

       Examples
       --------
       >>> params = Parameters.load("march29")
       >>> params.set_disease("ncov")
       >>> params.set_input_files("2011Data")
       >>> params.add_seeds("ExtraSeedsBrighton.dat")
    """
    #: The set of input files that define the model Network
    input_files: InputFiles = None
    #: The name of the UV file
    uv_filename: str = None
    #: The set of parameters that define the disease
    disease_params: Disease = None

    #: The set of files that contain additional seeds that
    #: seed the outbreak during the model run
    additional_seeds: _List[str] = None

    #: The fraction of day considered "day" for work, e.g. 0.7 * 24 hours
    length_day: float = 0.7
    #: The fraction of day considered "day" for play
    plength_day: float = 0.5
    #: The number of initial infections
    initial_inf: int = 5

    static_play_at_home: float = 0.0
    dyn_play_at_home: float = 0.0

    data_dist_cutoff: float = 10000000.0
    dyn_dist_cutoff: float = 10000000.0

    play_to_work: float = 0.0
    work_to_play: float = 0.0

    local_vaccination_thresh: int = 4
    global_detection_thresh: int = 4
    daily_ward_vaccination_capacity: int = 5
    neighbour_weight_threshold: float = 0.0

    #: proportion of daily imports
    daily_imports: float = 0.0

    #: how to treat the * state (stage 0). This should be a string
    #: describing the method. Currently "R", "E" and "disable" are
    #: supported
    stage_0: str = "R"

    #: Seasonality parameter
    UV: float = 0.0

    #: User parameters
    user_params: _Dict[str, float] = None

    _name: str = None
    _version: str = None
    _authors: str = None
    _contacts: str = None
    _references: str = None
    _filename: str = None
    _repository: str = None
    _repository_version: str = None
    _repository_branch: str = None
    _repository_dir: str = None

    #: The parameters for demographic sub-networks. If this is None then
    #: the parameters are the same as the overall parameters
    _subparams = None

    def __str__(self):
        return f"""
* Parameters: {self._name}
* loaded from: {self._filename}
* repository: {self._repository}
* repository_branch: {self._repository_branch}
* repository_version: {self._repository_version}
* length_day: {self.length_day}
* plength_day: {self.plength_day}
* initial_inf: {self.initial_inf}
* static_play_at_home: {self.static_play_at_home}
* dyn_play_at_home: {self.dyn_play_at_home}
* data_dist_cutoff: {self.data_dist_cutoff}
* dyn_dist_cutoff: {self.dyn_dist_cutoff}
* play_to_work: {self.play_to_work}
* work_to_play: {self.work_to_play}
* local_vaccination_thresh: {self.local_vaccination_thresh}
* global_detection_thresh: {self.global_detection_thresh}
* daily_ward_vaccination_capacity: {self.daily_ward_vaccination_capacity}
* neighbour_weight_threshold: {self.neighbour_weight_threshold}
* daily_imports: {self.daily_imports}
* UV: {self.UV}
* stage_0: {self.stage_0}
* additional_seeds: {self.additional_seeds}"""

    @staticmethod
    def get_repository(repository: str = None):
        """Return the repository location and version information
           for the passed repository

           Parameters
           ----------
           repository: str
             Location on the filesystem of the repository. If this
             is None then it will be searched for using first
             the environment variable METAWARDSDATA, then
             $HOME/GitHub/MetaWardsData, then ./METAWARDSDATA

           Returns
           -------
           (repository, version): tuple
             A tuple of the location on disk of the repository,
             plus the version information (git ID etc)
        """
        return get_repository(repository)

    @staticmethod
    def load(parameters: str = "march29",
             repository: str = None,
             folder: str = _default_folder_name,
             filename: str = None):
        """This will return a Parameters object containing all of the
           parameters loaded from the parameters found in file
           f"{repository}/{folder}/{parameters}.json"

           By default this will load the march29 parameters from
           $HOME/GitHub/model_data/2011Data/parameters/march29.json

           Alternatively, you can provide the exact path to the
           filename via the 'filename' argument

           Parameters
           ----------
           parameters: str
             The name of the parameters to load. This is the name that
             will be searched for in the METAWARDSDATA parameters directory
           repository: str
             The location of the cloned METAWARDSDATA repository
           folder: str
             The name of the folder within the METAWARDSDATA repository
             that contains the parameters
           filename: str
             The name of the file to load the parameters from - this directly
             loads this file without searching through the METAWARDSDATA
             repository

           Returns
           -------
           params: Parameters
             The constructed and validated parameters
        """
        repository_version = None
        repository_branch = None
        repository_dir = None

        if filename is None:
            import os
            (repository, v) = Parameters.get_repository(repository)
            filename = os.path.join(repository, folder, f"{parameters}.json")
            repository_dir = repository
            repository = v["repository"]
            repository_branch = v["branch"]
            repository_version = v["version"]

        json_file = filename

        try:
            with open(json_file, "r") as FILE:
                import json
                data = json.load(FILE)

        except Exception as e:
            from .utils._console import Console
            Console.error(f"""
Could not find the parameters file {json_file}. Either it does not exist or
was corrupted. Error was {e.__class__} {e}. "Please see
https://metawards.org/model_data for instructions on how to download and
set the model data.""")
            raise FileNotFoundError(f"Could not find or read {json_file}: "
                                    f"{e.__class__} {e}")

        par = Parameters(
            length_day=data.get("length_day", 0.7),
            plength_day=data.get("plength_day", 0.5),
            initial_inf=data.get("initial_inf", 0),
            static_play_at_home=data.get("static_play_at_home", 0.0),
            dyn_play_at_home=data.get("dyn_play_at_home", 0.0),
            data_dist_cutoff=data.get("data_dist_cutoff", 10000000.0),
            dyn_dist_cutoff=data.get("dyn_dist_cutoff", 10000000.0),
            play_to_work=data.get("play_to_work", 0.0),
            work_to_play=data.get("work_to_play", 0.0),
            local_vaccination_thresh=data.get(
                "local_vaccination_threshold", 4),
            global_detection_thresh=data.get(
                "global_detection_threshold", 4),
            daily_ward_vaccination_capacity=data.get(
                "daily_ward_vaccination_capacity", 5),
            neighbour_weight_threshold=data.get(
                "neighbour_weight_threshold", 0.0),
            daily_imports=data.get("daily_imports", 0),
            UV=data.get("UV", 0.0),
            _name=data.get("name", parameters),
            _authors=data.get("author(s)", "unknown"),
            _version=data.get("version", "unknown"),
            _contacts=data.get("contact(s)", "unknown"),
            _references=data.get("reference(s)", "none"),
            _filename=json_file,
            _repository=repository,
            _repository_dir=repository_dir,
            _repository_branch=repository_branch,
            _repository_version=repository_version
        )

        return par

    def __getitem__(self, demographic: str):
        """Return the parameters that should be used for the demographic
           subnetwork called 'demographic'. If these have not been set
           specifically then the parameters for the overall network
           are used
        """
        if demographic == "overall":
            return self

        if self._subparams is None:
            self._subparams = {}

        if demographic not in self._subparams:
            from copy import deepcopy
            self._subparams[demographic] = deepcopy(self)
            self._subparams[demographic]._subparams = {}

        return self._subparams[demographic]

    def copy(self, include_subparams: bool = False):
        """Return a safe copy of these parameters, which does not
           include any subnetwork parameters if 'include_subparams' is False
        """
        from copy import deepcopy
        params = deepcopy(self)

        if not include_subparams:
            params._subparams = None

        return params

    def specialised_demographics(self) -> _List[str]:
        """Return the names of demographics that have specialised
           parameters that are different to those of the overall
           network
        """
        if self._subparams is None:
            return []
        else:
            return list(self._subparams.keys())

    def add_seeds(self, filename: str):
        """Add an 'additional seeds' file that can be used to
           seed wards with new infections at different times and
           locations. Several additional_seed files can be added

           Parameters
           ----------
           filename: str
             Name of the file containing the additional seeds
        """
        # resolve the filename to the GitHub repo if possible...
        if self.additional_seeds is None:
            self.additional_seeds = []

        import os

        if not os.path.exists(filename):
            f = os.path.join(self._repository_dir, "extra_seeds", filename)

            if os.path.exists(f):
                filename = f
            else:
                raise FileExistsError(
                    f"Unable to find extra seeds file {filename} in "
                    f"the current directory or in {f}")

        self.additional_seeds.append(filename)

    def set_input_files(self, input_files: InputFiles):
        """Set the input files that are used to initialise the
           simulation

           Parameters
           ----------
           input_files: InputFiles
             The set of input files that will be used to load the Network.
             If a string is passed then the InputFiles will be loaded
             based on that string.
        """
        if isinstance(input_files, str):
            input_files = InputFiles.load(input_files,
                                          repository=self._repository_dir)

        from .utils._console import Console
        Console.print(input_files, markdown=True)

        from copy import deepcopy
        self.input_files = deepcopy(input_files)

    def set_disease(self, disease: Disease):
        """"Set the disease that will be modelled

            Parameters:
              disease: The disease to be modelled. If a string is passed
              then the disease will be loaded using that string
        """
        if isinstance(disease, str):
            disease = Disease.load(disease,
                                   repository=self._repository_dir)

        from .utils._console import Console
        Console.print(disease, markdown=True)

        from copy import deepcopy
        self.disease_params = deepcopy(disease)

    def set_variables(self, variables: VariableSet):
        """This function sets the adjustable variable values to those
           specified in 'variables' in A COPY OF THIS PARAMETERS OBJECT.
           This returns the copy. It does not change this object

           Parameters
           ----------
           variables: VariableSet
             The variables that will be adjusted before the model run.
             This adjusts the parameters and returns them in a deep copy

           Returns
           -------
           params: Parameters
             A copy of this set of parameters with the variables adjusted
        """
        from copy import deepcopy
        params = deepcopy(self)

        if isinstance(variables, dict):
            variables = VariableSet(variables)

        variables.adjust(params)

        return params

    @staticmethod
    def read_variables(filename: str, line_numbers: _List[int]):
        """Read in extra variable parameters from the specified line number(s)
           of the specified file, returning the list
           of the dictionaries of variables that have been
           read. You can then apply those variable parameters
           using the 'set_variables' function

           Parameters
           ----------
           filename: str
             The file from which to read the adjustable variables
           line_numbers: List[int]
             All of the line numbers from which to read. If this is
             None then all lines will be read.

           Returns
           -------
           variables: VariableSets
             The VariableSets containing all of the adjustable variables
        """
        return VariableSets.read(filename, line_numbers)
