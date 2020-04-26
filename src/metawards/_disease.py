
from dataclasses import dataclass as _dataclass
from typing import List as _List
import pathlib as _pathlib
import os as _os

__all__ = ["Disease"]

_default_disease_path = _os.path.join(_pathlib.Path.home(),
                                      "GitHub", "MetaWardsData")

_default_folder_name = "diseases"


def _safe_eval_float(s):
    """Convert 's' to a float. This supports normal floats,
       but also simple maths expressions like 1/1.2
    """
    try:
        return float(s)
    except Exception:
        pass

    try:
        # this is about as save as eval gets in python
        return float(eval(s, {"__builtins__":None},{}))
    except Exception:
        pass

    raise ValueError(f"Cannot interpret '{s}' as a float")


@_dataclass
class Disease:
    """This class holds the parameters about a single disease

       A disease is characterised as a serious of stages, each
       with their own values of the beta, progress, too_ill_to_move
       and contrib_foi parameters. To load a disease use
       the Disease.load function, e.g.

       Examples
       --------
       >>> disease = Disease.load("ncov")
       >>> print(disease)
       Disease ncov
       repository: https://github.com/metawards/MetaWardsData
       repository_branch: master
       repository_version: 0.2.0
       beta = [0.0, 0.0, 0.95, 0.95, 0.0]
       progress = [1.0, 0.1923, 0.909091, 0.909091, 0.0]
       too_ill_to_move = [0.0, 0.0, 0.0, 0.0, 0.0]
       contrib_foi = [1.0, 1.0, 1.0, 1.0, 0.0]
    """
    #: Beta parameter for each stage of the disease
    beta: _List[float] = None
    #: Progress parameter for each stage of the disease
    progress: _List[float] = None
    #: TooIllToMove parameter for each stage of the disease
    too_ill_to_move: _List[float] = None
    #: Contribution to the Force of Infection (FOI) parameter for each
    #: stage of the disease
    contrib_foi: _List[float] = None
    #: Index of the first symptomatic stage
    start_symptom: int = None

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
        return f"Disease {self._name}\n" \
               f"loaded from {self._filename}\n" \
               f"version: {self._version}\n" \
               f"author(s): {self._authors}\n" \
               f"contact(s): {self._contacts}\n" \
               f"references(s): {self._references}\n" \
               f"repository: {self._repository}\n" \
               f"repository_branch: {self._repository_branch}\n" \
               f"repository_version: {self._repository_version}\n\n" \
               f"beta = {self.beta}\n" \
               f"progress = {self.progress}\n" \
               f"too_ill_to_move = {self.too_ill_to_move}\n" \
               f"contrib_foi = {self.contrib_foi}\n" \
               f"start_symptom = {self.start_symptom}\n\n"

    def __eq__(self, other):
        return self.beta == other.beta and \
               self.progress == other.progress and \
               self.too_ill_to_move == other.too_ill_to_move and \
               self.contrib_foi == other.contrib_foi and \
               self.start_symptom == other.start_symptom

    def __len__(self):
        if self.beta:
            return len(self.beta)
        else:
            return 0

    def N_INF_CLASSES(self):
        """Return the number of stages of the disease"""
        return len(self.beta)

    def _validate(self):
        """Check that the loaded parameters make sense"""
        try:
            n = len(self.beta)

            assert len(self.progress) == n
            assert len(self.too_ill_to_move) == n
            assert len(self.contrib_foi) == n
        except Exception as e:
            raise AssertionError(f"Data read for disease {self._name} "
                                 f"is corrupted! {e.__class__}: {e}")

        if self.start_symptom is None or self.start_symptom < 0 or \
           self.start_symptom >= n:
            raise AssertionError(f"start_symptom {self.start_symptom} is "
                                 f"invalid for a disease with {n} stages")

        self.start_symptom = int(self.start_symptom)

        for i in range(0, n):
            try:
                self.progress[i] = _safe_eval_float(self.progress[i])
                self.too_ill_to_move[i] = _safe_eval_float(
                                                self.too_ill_to_move[i])
                self.beta[i] = _safe_eval_float(self.beta[i])
                self.contrib_foi[i] = _safe_eval_float(self.contrib_foi[i])
            except Exception as e:
                raise AssertionError(
                    f"Invalid disease parameter at index {i}: "
                    f"{e.__class__} {e}")

    @staticmethod
    def load(disease: str = "ncov",
             repository: str = None,
             folder: str = _default_folder_name,
             filename: str = None):
        """Load the disease parameters for the specified disease.
           This will look for a file called f"{disease}.json"
           in the directory f"{repository}/{disease}/{disease}.ncon"

           By default this will load the ncov (SARS-Cov-2)
           parameters from
           $HOME/GitHub/model_data/2011Data/diseases/ncov.json

           Alternatively you can provide the full path to the
           json file via the "filename" argument

           Parameters
           ----------
           disease: str
             The name of the disease to load. This is the name that
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
           disease: Disease
             The constructed and validated disease
        """
        repository_version = None
        repository_branch = None

        if filename is None:
            import os
            if os.path.exists(disease):
                filename = disease
            elif os.path.exists(f"{disease}.json"):
                filename = f"{disease}.json"

        if filename is None:
            if repository is None:
                repository = _os.getenv("METAWARDSDATA")
                if repository is None:
                    repository = _default_disease_path

            filename = _os.path.join(repository, folder,
                                     f"{disease}.json")

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
            print(f"Could not find the disease file {json_file}")
            print(f"Either it does not exist of was corrupted.")
            print(f"Error was {e.__class__} {e}")
            print(f"To download the disease data type the command:")
            print(f"  git clone https://github.com/metawards/MetaWardsData")
            print(f"and then re-run this function passing in the full")
            print(f"path to where you downloaded this directory")
            raise FileNotFoundError(f"Could not find or read {json_file}: "
                                    f"{e.__class__} {e}")

        disease = Disease(beta=data["beta"],
                          progress=data["progress"],
                          too_ill_to_move=data["too_ill_to_move"],
                          contrib_foi=data["contrib_foi"],
                          start_symptom=data["start_symptom"],
                          _name=disease,
                          _authors=data["author(s)"],
                          _contacts=data["contact(s)"],
                          _references=data["reference(s)"],
                          _filename=json_file,
                          _repository=repository,
                          _repository_branch=repository_branch,
                          _repository_version=repository_version)

        disease._validate()

        return disease
