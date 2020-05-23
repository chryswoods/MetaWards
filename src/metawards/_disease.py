
from dataclasses import dataclass as _dataclass
from typing import List as _List

__all__ = ["Disease"]

_default_folder_name = "diseases"


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
        return f"""
* Disease: {self._name}
* loaded from: {self._filename}
* repository: {self._repository}
* repository_branch: {self._repository_branch}
* repository_version: {self._repository_version}
* beta: {self.beta}
* progress: {self.progress}
* too_ill_to_move: {self.too_ill_to_move}
* contrib_foi: {self.contrib_foi}
* start_symptom: {self.start_symptom}
"""

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

        from .utils._safe_eval import safe_eval_number

        for i in range(0, n):
            try:
                self.progress[i] = safe_eval_number(self.progress[i])
                self.too_ill_to_move[i] = safe_eval_number(
                    self.too_ill_to_move[i])
                self.beta[i] = safe_eval_number(self.beta[i])
                self.contrib_foi[i] = safe_eval_number(self.contrib_foi[i])
            except Exception as e:
                raise AssertionError(
                    f"Invalid disease parameter at index {i}: "
                    f"{e.__class__} {e}")

        # for the model to work the different stages have set meanings
        errors = []

        # - stage 0 is newly infected that day, so progress must be 1
        #   and beta must be 0 (not infective)
        # This is not an error - the pox and flu2 diseases have this.
        # I don't think I understand correctly though if that is right,
        # as this means that individuals will stay longer in the
        # post-infect but pre-latent stage and be recorded as "recovered"?
        # if self.progress[0] != 1.0:
        #    errors.append(
        #        f"The progress[0] value must be 1.0 as individuals are "
        #        f"only newly infected for one day, and so must progress "
        #        f"immediately to the 'latent' stage.")

        if self.beta[0] != 0.0:
            errors.append(
                f"The beta[0] value must be 0.0 as newly infected "
                f"individuals should not be infective and cannot "
                f"infect others.")

        # - stage 1 is 'latent', meaning that beta must be 0 (not infective)
        if self.beta[1] != 0.0:
            errors.append(
                f"The beta[1] value must be 0.0 as 'latent' individuals "
                f"are not infectious and should not be able to infect "
                f"others.")

        # - stage -1 is 'recovered', meaning that beta must not be 0
        #   and progress is 0, as once recovered, always recovered
        if self.beta[-1] != 0.0:
            errors.append(
                f"The beta[-1] value must be 0.0 as 'recovered' individuals "
                f"are not infectious and should not be able to infect "
                f"others.")

        if self.progress[-1] != 0.0:
            errors.append(
                f"The progress[-1] value must be 0.0 as 'recovered' "
                f"individuals have no further disease stage to progress to. "
                f"We hope that once recovered, always recovered.")

        if len(errors) > 0:
            from .utils._console import Console
            Console.error("\n".join(errors))
            raise AssertionError("Invalid disease parameters!\n" +
                                 "\n".join(errors))

    @staticmethod
    def load(disease: str = "ncov",
             repository: str = None,
             folder: str = _default_folder_name,
             filename: str = None):
        """Load the disease parameters for the specified disease.
           This will look for a file called f"{disease}.json"
           in the directory f"{repository}/{folder}/{disease}.json"

           By default this will load the ncov (SARS-Cov-2)
           parameters from
           $HOME/GitHub/model_data/diseases/ncov.json

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
            from ._parameters import get_repository
            repository, v = get_repository(repository)

            filename = os.path.join(repository, folder,
                                    f"{disease}.json")

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
Could not find the disease file {json_file}. Either it does not exist of was
corrupted. Error was {e.__class__} {e}. Please see
https://metawards.org/model_data for instructions on how to download and
set the model data.""")
            raise FileNotFoundError(f"Could not find or read {json_file}: "
                                    f"{e.__class__} {e}")

        disease = Disease(beta=data.get("beta", []),
                          progress=data.get("progress", []),
                          too_ill_to_move=data.get("too_ill_to_move", []),
                          contrib_foi=data.get("contrib_foi", []),
                          start_symptom=data.get("start_symptom", 3),
                          _name=disease,
                          _authors=data.get("author(s)", "unknown"),
                          _contacts=data.get("contact(s)", "unknown"),
                          _references=data.get("reference(s)", "none"),
                          _filename=json_file,
                          _repository=repository,
                          _repository_branch=repository_branch,
                          _repository_version=repository_version)

        disease._validate()

        return disease
