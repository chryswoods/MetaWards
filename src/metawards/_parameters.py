
from dataclasses import dataclass as _dataclass
from typing import List as _List, Dict as _Dict
from copy import deepcopy as _deepcopy
import pathlib as _pathlib
import os as _os
import json as _json

from ._inputfiles import InputFiles
from ._disease import Disease
from ._variableset import VariableSets, VariableSet


__all__ = ["Parameters", "get_repository_version"]

_default_parameters_path = _os.path.join(_pathlib.Path.home(),
                                         "GitHub", "MetaWardsData")

_default_folder_name = "parameters"


_repositories = {}


def generate_repository_version(repository):
    """Try to run the './version' script within the passed repository,
       to generate the required 'version.txt' file
    """
    import subprocess
    script = _os.path.join(repository, "version")
    print(f"Regenerating version information using {script}")
    subprocess.run(script, cwd=repository)


def get_repository_version(repository: str):
    """Read and return the Git version of the passed repository

       Parameters
       ----------
       repository: str
         The full path to the repository whose version should be obtained

       Returns
       -------
       version_data: dict
         A dictionary containing version information for the repository
    """
    global _repositories

    if repository in _repositories:
        return _repositories[repository]

    filename = _os.path.join(repository, "version.txt")

    try:
        with open(filename) as FILE:
            version = _json.load(FILE)
            _repositories[repository] = version
            return version
    except Exception:
        pass

    # could not get the version, so see if we have permission
    # to run the 'version' program
    try:
        generate_repository_version(repository)

        with open(filename) as FILE:
            version = _json.load(FILE)
            _repositories[repository] = version
            return version
    except Exception:
        print(f"Could not find the repository version info in {filename}."
              f"Please make sure that you have run './version' in that "
              f"repository to generate the version info.")
        _repositories[repository] = {"repository": "unknown",
                                     "version": "unknown",
                                     "branch": "unknown"}
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

    def __str__(self):
        return f"Parameters {self._name}\n" \
               f"loaded from {self._filename}\n" \
               f"version: {self._version}\n" \
               f"author(s): {self._authors}\n" \
               f"contact(s): {self._contacts}\n" \
               f"references(s): {self._references}\n" \
               f"repository: {self._repository}\n" \
               f"repository_branch: {self._repository_branch}\n" \
               f"repository_version: {self._repository_version}\n\n" \
               f"length_day = {self.length_day}\n" \
               f"plength_day = {self.plength_day}\n" \
               f"initial_inf = {self.initial_inf}\n" \
               f"static_play_at_home = {self.static_play_at_home}\n" \
               f"dyn_play_at_home = {self.dyn_play_at_home}\n" \
               f"data_dist_cutoff = {self.data_dist_cutoff}\n" \
               f"dyn_dist_cutoff = {self.dyn_dist_cutoff}\n" \
               f"play_to_work = {self.play_to_work}\n" \
               f"work_to_play = {self.work_to_play}\n" \
               f"local_vaccination_thresh = " \
               f"{self.local_vaccination_thresh}\n" \
               f"global_detection_thresh = {self.global_detection_thresh}\n" \
               f"daily_ward_vaccination_capacity = " \
               f"{self.daily_ward_vaccination_capacity}\n" \
               f"neighbour_weight_threshold = " \
               f"{self.neighbour_weight_threshold}\n" \
               f"daily_imports = {self.daily_imports}\n" \
               f"UV = {self.UV}\n" \
               f"additional_seeds = {self.additional_seeds}\n\n"

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
        if repository is None:
            repository = _os.getenv("METAWARDSDATA")
            if repository is None:
                repository = _default_parameters_path

        from pathlib import Path
        import os
        repository = os.path.expanduser(os.path.expandvars(repository))
        repository = Path(repository).absolute().resolve()

        if not os.path.exists(repository):
            raise FileNotFoundError(
                    f"Cannot find the MetaWardsData repository "
                    f"at {repository}")

        if not os.path.isdir(repository):
            raise FileNotFoundError(
                    f"Expected {repository} to be a directory containing "
                    f"the MetaWardsData repository. It isn't?")

        v = get_repository_version(repository)
        return (repository, v)

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
            (repository, v) = Parameters.get_repository(repository)
            filename = _os.path.join(repository, folder, f"{parameters}.json")
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
            print(f"Could not find the parameters file {json_file}")
            print(f"Either it does not exist of was corrupted.")
            print(f"Error was {e.__class__} {e}")
            print(f"To download the parameters type the command:")
            print(f"  git clone https://github.com/metawards/MetaWardsData")
            print(f"and then re-run this function passing in the full")
            print(f"path to where you downloaded this directory")
            raise FileNotFoundError(f"Could not find or read {json_file}: "
                                    f"{e.__class__} {e}")

        par = Parameters(
                length_day=data["length_day"],
                plength_day=data["plength_day"],
                initial_inf=data["initial_inf"],
                static_play_at_home=data["static_play_at_home"],
                dyn_play_at_home=data["dyn_play_at_home"],
                data_dist_cutoff=data["data_dist_cutoff"],
                dyn_dist_cutoff=data["dyn_dist_cutoff"],
                play_to_work=data["play_to_work"],
                work_to_play=data["work_to_play"],
                local_vaccination_thresh=data["local_vaccination_threshold"],
                global_detection_thresh=data["global_detection_threshold"],
                daily_ward_vaccination_capacity=data[
                                "daily_ward_vaccination_capacity"],
                neighbour_weight_threshold=data["neighbour_weight_threshold"],
                daily_imports=data["daily_imports"],
                UV=data["UV"],
                _name=data["name"],
                _authors=data["author(s)"],
                _version=data["version"],
                _contacts=data["contact(s)"],
                _references=data["reference(s)"],
                _filename=json_file,
                _repository=repository,
                _repository_dir=repository_dir,
                _repository_branch=repository_branch,
                _repository_version=repository_version
                )

        print("Using parameters:")
        print(par)

        return par

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

        if not _os.path.exists(filename):
            f = _os.path.join(self._repository_dir, "extra_seeds", filename)

            if _os.path.exists(f):
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

        print("Using input files:")
        print(input_files)

        self.input_files = _deepcopy(input_files)

    def set_disease(self, disease: Disease):
        """"Set the disease that will be modelled

            Parameters:
              disease: The disease to be modelled. If a string is passed
              then the disease will be loaded using that string
        """
        if isinstance(disease, str):
            disease = Disease.load(disease,
                                   repository=self._repository_dir)

        print("Using disease")
        print(disease)

        self.disease_params = _deepcopy(disease)

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
        params = _deepcopy(self)

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
