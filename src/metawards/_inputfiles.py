
from dataclasses import dataclass as _dataclass
import os as _os
import pathlib as _pathlib

__all__ = ["InputFiles"]

_inputfiles = {}

_default_model_path = _os.path.join(_pathlib.Path.home(),
                                    "GitHub", "MetaWardsData")

_default_folder_name = "model_data"


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
       repository_branch: master
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
    #: File from which to read the values to seed the wards
    seed: str = None
    #: File from which to read the list of nodes to track
    nodes_to_track: str = None
    #: UV file
    uv: str = None

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

    def model_name(self):
        """Return the name of this model"""
        return self._model_name

    def model_path(self):
        """Return the path to the directory containing this model"""
        return self._model_path

    def model_version(self):
        """Return the version of the data in this model"""
        return self._model_version

    def __str__(self):
        return f"Model {self._model_name} version {self._model_version}\n" \
               f"loaded from {self._filename}\n" \
               f"root directory {self._model_path}\n" \
               f"author(s): {self._authors}\n" \
               f"contact(s): {self._contacts}\n" \
               f"references(s): {self._references}\n" \
               f"repository: {self._repository}\n" \
               f"repository_branch: {self._repository_branch}\n" \
               f"repository_version: {self._repository_version}\n\n" \
               f"work = {self.work}\n" \
               f"play = {self.play}\n" \
               f"identifier = {self.identifier}\n" \
               f"identifier2 = {self.identifier2}\n" \
               f"weekend = {self.weekend}\n" \
               f"work_size = {self.work_size}\n" \
               f"play_size = {self.play_size}\n" \
               f"position = {self.position}\n" \
               f"coordinates = {self.coordinates}\n" \
               f"seed = {self.seed}\n" \
               f"nodes_to_track = {self.nodes_to_track}\n\n"

    def _localise(self):
        """Localise the filenames in this input files set. This will
           prepend model_path/model to every filename and will also
           double-check that all files exist and are readable
        """
        members = [attr for attr in dir(self)
                   if not callable(getattr(self, attr))
                   and not attr.startswith("_")]

        for member in members:
            if member == "coordinates":
                continue

            filename = getattr(self, member)
            if filename:
                filename = _os.path.join(self._model_path, filename)

                if not (_os.path.exists(filename) and
                        _os.path.isfile(filename)):
                    raise FileNotFoundError(
                            f"Cannot find input file {member} = {filename}")

                setattr(self, member, filename)

    @staticmethod
    def load(model: str = "2011Data",
             repository: str = _default_model_path,
             folder: str = _default_folder_name,
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

        if filename is None:
            if repository is None:
                repository = _os.getenv("METAWARDSDATA")
                if repository is None:
                    repository = _default_model_path

            filename = _os.path.join(repository, folder,
                                     model, description)

            from ._parameters import get_repository_version
            v = get_repository_version(repository)
            repository = v["repository"]
            repository_version = v["version"]
            repository_branch = v["branch"]

        json_file = filename
        model_path = _os.path.dirname(filename)

        try:
            with open(json_file, "r") as FILE:
                import json
                files = json.load(FILE)

        except Exception as e:
            print(f"Could not find the model file {json_file}")
            print(f"Either it does not exist of was corrupted.")
            print(f"Error was {e.__class__} {e}")
            print(f"To download the model data type the command:")
            print(f"  git clone https://github.com/metawards/MetaWardsData")
            print(f"and then re-run this function passing in the full")
            print(f"path to where you downloaded this directory")
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
                           seed=files.get("seed", None),
                           nodes_to_track=files.get("nodes_to_track", None),
                           uv=files.get("uv", None),
                           _filename=json_file,
                           _model_path=model_path,
                           _model_name=files["name"],
                           _model_version=files["version"],
                           _references=files["reference(s)"],
                           _authors=files["author(s)"],
                           _contacts=files["contact(s)"],
                           _repository=repository,
                           _repository_version=repository_version,
                           _repository_branch=repository_branch)

        model._localise()

        return model
