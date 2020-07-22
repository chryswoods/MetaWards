
from dataclasses import dataclass as _dataclass
from typing import Dict as _Dict
from typing import List as _List

__all__ = ["InputFiles"]

_inputfiles = {}

_default_folder_name = "model_data"


def _expand_path(json_file):
    from pathlib import Path
    return str(Path(json_file).expanduser().absolute())


def _is_description_json(json_file):
    """Return whether or not this json file contains description data"""
    import os
    if not (os.path.exists(json_file) and os.path.isfile(json_file)):
        return False

    try:
        import bz2
        with bz2.open(json_file, "rt") as FILE:
            while True:
                line = FILE.readline().strip()
                if len(line) > 0:
                    if line.startswith("["):
                        return False
                    elif line.startswith("{"):
                        return True

        return False
    except Exception:
        pass

    with open(json_file, "r") as FILE:
        while True:
            line = FILE.readline().strip()
            if len(line) > 0:
                if line.startswith("["):
                    return False
                elif line.startswith("{"):
                    return True

    return False


@_dataclass
class InputFiles:
    """This class holds all of the input files that must be loaded
       from METAWARDSDATA to construct the network of wards
       and links between them

       Load using the InputFiles.load function e.g.

       Examples
       --------
       >>> infiles = InputFiles.load("2011Data")
       >>> print(infiles)
       Model 2011Data version March 29 2020
       repository: https://github.com/metawards/MetaWardsData
       repository_branch: main
       repository_version: 0.2.0
       etc.
    """
    #: File from which to read the work matrix of links
    work: str = None
    #: File from which to read the play matrix of links
    play: str = None
    #: File from which to read all of the ward names
    identifier: str = None
    #: File from which to read all of the secondary
    #: ward IDs, (Communities, Counties, Districts, UA's etc)
    identifier2: str = None
    #: File from which to read the weekend matrix of links
    weekend: str = None
    #: File from which to read the size of the population in the work file
    work_size: str = None
    #: File from which to read the size of the population in the play file
    play_size: str = None
    #: File from which to read the positions (locations) of the wards
    #: (the centre of the bounding boxes)
    position: str = None
    #: Coordinates-system used for the positions. Should be 'x/y' or 'lat/long'
    coordinates: str = None
    #: File to look up metadata about the wards (e.g. their names)
    lookup: str = None
    #: Which columns in this file have the data
    lookup_columns: _Dict[str, int] = None
    #: File from which to read the values to seed the wards
    seed: str = None
    #: File from which to read the list of nodes to track
    nodes_to_track: str = None
    #: UV file
    uv: str = None
    #: Whether or not this is the special "single" ward model
    is_single: bool = False
    #: The json file containing the wards data if this is a ward_json
    wards_data: str = None

    _filename: str = None            # Full path of the description.json file
    _model_name: str = None          # Name of the model
    _model_path: str = None          # Directory containing the input files
    _model_version: str = None       # Version loaded from the data
    _authors: str = None             # Author(s) of this data
    _contacts: str = None            # Contact(s) for this data
    _references: str = None          # References for this data
    _repository: str = None          # GitHub repository for this data
    _repository_version: str = None  # Git version of the data
    _repository_branch: str = None   # Git branch for the data

    @property
    def is_model_dir(self) -> bool:
        return self._model_name is not None

    @property
    def is_wards_data(self) -> bool:
        return self.wards_data is not None

    def model_name(self):
        """Return the name of this model"""
        if self.is_wards_data:
            return "custom"
        elif self.is_single:
            return "single"
        else:
            return self._model_name

    def model_path(self):
        """Return the path to the directory containing this model"""
        if self.is_wards_data or self.is_single:
            return None
        else:
            return self._model_path

    def model_version(self):
        """Return the version of the data in this model"""
        if self.is_wards_data or self.is_single:
            return None
        else:
            return self._model_version

    def __str__(self):
        if self.is_single:
            return "Model: single ward"
        elif self.is_wards_data:
            import os
            filename = os.path.basename(self.wards_data)
            return f"Model: {filename}"
        else:
            return f"""* Model: {self._model_name}
* loaded from: {self._filename}
* repository: {self._repository}
* repository_branch: {self._repository_branch}
* repository_version: {self._repository_version}
* work: {self.work}
* play: {self.play}
* identifier: {self.identifier}
* identifier2: {self.identifier2}
* weekend: {self.weekend}
* work_size: {self.work_size}
* play_size: {self.play_size}
* position: {self.position}
* coordinates: {self.coordinates}
* lookup: {self.lookup}
* lookup_columns: {self.lookup_columns}
* seed: {self.seed}
* nodes_to_track: {self.nodes_to_track}"""

    def __repr__(self):
        if self.is_single:
            return f"InputFiles::single"
        elif self.is_wards_data:
            import os
            filename = os.path.basename(self.wards_data)
            return f"InputFiles(wards_data='{filename}')"
        else:
            return f"InputFiles(model='{self._model_name}')"

    def __hash__(self):
        return self._filename.__hash__()

    def _localise(self):
        """Localise the filenames in this input files set. This will
           prepend model_path/model to every filename and will also
           double-check that all files exist and are readable
        """
        if self.is_single or self.is_wards_data:
            return

        members = [attr for attr in dir(self)
                   if not callable(getattr(self, attr))
                   and not attr.startswith("_")]

        for member in members:
            if member in ["coordinates", "lookup_columns", "is_model_dir",
                          "is_wards_data", "wards_data", "is_single"]:
                continue

            filename = getattr(self, member)
            if filename:
                import os
                filename = os.path.join(self._model_path, filename)

                if not (os.path.exists(filename) and
                        os.path.isfile(filename)):
                    raise FileNotFoundError(
                        f"Cannot find input file {member} = {filename}")

                setattr(self, member, filename)

    @staticmethod
    def load(model: str = "2011Data",
             repository: str = None,
             folder: str = None,
             description: str = "description.json",
             filename: str = None):
        """Load the parameters associated with the passed model.
           This will look for the parameters specified in
           the json file called f"{repository}/{folder}/{model}/{description}"

           By default this will load the 2011Data parameters
           from $HOME/GitHub/model_data/2011Data/description.json

           Alternatively you can provide the full path to the
           description json file usng the 'filename' argument.
           All files within this description will be searched
           for using the directory that contains that file
           as a base

           Parameters
           ----------
           model: str
             The name of the model data to load. This is the name that
             will be searched for in the METAWARDSDATA model_data directory
           repository: str
             The location of the cloned METAWARDSDATA repository
           folder: str
             The name of the folder within the METAWARDSDATA repository
             that contains the model data
           filename: str
             The name of the file to load the model data from - this directly
             loads this file without searching through the METAWARDSDATA
             repository

           Returns
           -------
           input_files: InputFiles
             The constructed and validated set of input files
        """
        repository_version = None
        repository_branch = None

        if model == "single":
            # This is the special 'single-ward' model - just return
            # a basic InputFiles
            return InputFiles(is_single=True)

        if filename is None:
            from ._parameters import get_repository
            import os

            if folder is None or os.path.isabs(model):
                filename = model
            else:
                filename = os.path.join(folder, model)

            if os.path.exists(filename) and os.path.isfile(filename):
                filename = _expand_path(filename)
            else:
                repository, v = get_repository(repository)

                if folder is None:
                    folder = _default_folder_name

                filename = os.path.join(repository, folder,
                                        model, description)

                filename = _expand_path(filename)

                repository = v["repository"]
                repository_version = v["version"]
                repository_branch = v["branch"]

        json_file = filename
        import os
        model_path = os.path.dirname(filename)

        if not (os.path.exists(json_file) and os.path.isfile(json_file)):
            from .utils._console import Console
            Console.error(f"Cannot read file {json_file} as it doesn't exist")
            raise IOError(
                f"Cannot load inputfiles as {json_file} doesn't exist")

        if not _is_description_json(json_file):
            # this must be wards data...
            json_file = _expand_path(json_file)
            return InputFiles(wards_data=json_file,
                              _filename=json_file)

        try:
            import json
            try:
                import bz2
                with bz2.open(json_file, "rt") as FILE:
                    files = json.load(FILE)
            except Exception:
                files = None

            if files is None:
                with open(json_file, "r") as FILE:
                    files = json.load(FILE)

        except Exception as e:
            from .utils._console import Console
            Console.error(f"""Could not find the model file {json_file}.
Either it does not exist or was corrupted.
Error was {e.__class__} {e}.
Please see https://metawards.org/model_data for instructions on how
to download and set the model data.""")
            raise FileNotFoundError(f"Could not find or read {json_file}: "
                                    f"{e.__class__} {e}")

        model = InputFiles(work=files.get("work", None),
                           play=files.get("play", None),
                           identifier=files.get("identifier", None),
                           identifier2=files.get("identifier2", None),
                           weekend=files.get("weekend", None),
                           work_size=files.get("work_size", None),
                           play_size=files.get("play_size", None),
                           position=files.get("position", None),
                           coordinates=files.get("coordinates", "x/y"),
                           lookup=files.get("lookup", None),
                           lookup_columns=files.get("lookup_columns", None),
                           seed=files.get("seed", None),
                           nodes_to_track=files.get("nodes_to_track", None),
                           uv=files.get("uv", None),
                           _filename=json_file,
                           _model_path=model_path,
                           _model_name=files.get("name", model),
                           _model_version=files.get("version", "unknown"),
                           _references=files.get("reference(s)", "none"),
                           _authors=files.get("author(s)", "unknown"),
                           _contacts=files.get("contact(s)", "unknown"),
                           _repository=repository,
                           _repository_version=repository_version,
                           _repository_branch=repository_branch)

        model._localise()

        return model
