from __future__ import annotations

from dataclasses import dataclass as _dataclass
from typing import List as _List
from typing import Dict as _Dict
from typing import Union as _Union

__all__ = ["Disease"]

_default_folder_name = "diseases"


def _infer_mapping(stages):
    """Get the computed mapping names for each stage. This is the
       letter part of the name, e.g. A1 maps to A, I3 maps to I etc.
    """
    import re as _re

    mapping = []

    for stage in stages:
        m = _re.search(r"(.*[^\d^\b^\s])[\b\s]*([\d]*)", stage)

        if m is None:
            raise AssertionError(f"Invalid stage name {stage}")

        mapping.append(str(m.groups()[0]))

    return mapping


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
       repository_branch: main
       repository_version: 0.2.0
       beta = [0.0, 0.0, 0.95, 0.95, 0.0]
       progress = [1.0, 0.1923, 0.909091, 0.909091, 0.0]
       too_ill_to_move = [0.0, 0.0, 0.0, 0.0, 0.0]
       contrib_foi = [1.0, 1.0, 1.0, 1.0, 0.0]
    """
    #: Name of the disease
    name: str = None

    #: Name of the stage, e.g. "H1", "I2", "E1" etc.
    stage: _List[str] = None

    #: Mapping label, e.g. "*", "E", "I" or "R"
    mapping: _List[str] = None

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

    _version: str = None
    _authors: str = None
    _contacts: str = None
    _references: str = None
    _filename: str = None
    _repository: str = None
    _repository_version: str = None
    _repository_branch: str = None

    def __str__(self):
        if self.beta is None:
            return "Disease::null"

        parts = []

        parts.append(f"* Disease: {self.name}")

        if self._filename is not None:
            parts.append(f"* loaded from: {self._filename}")

        if self._repository is not None:
            parts.append(f"* repository: {self._repository}")

        if self._repository_branch is not None:
            parts.append(f"* repository_branch: {self._repository_branch}")

        if self._repository_version is not None:
            parts.append(f"* repository_version: {self._repository_version}")

        parts.append(f"* stage: {self.stage}")
        parts.append(f"* mapping: {self.mapping}")
        parts.append(f"* beta: {self.beta}")
        parts.append(f"* progress: {self.progress}")
        parts.append(f"* too_ill_to_move: {self.too_ill_to_move}")

        if self.contrib_foi != [1.0] * len(self.beta):
            if self.contrib_foi != [1.0] * (len(self.beta) - 1) + [0.0]:
                parts.append(f"* contrib_foi: {self.contrib_foi}")

        parts.append(f"* start_symptom: {self.start_symptom}")

        return "\n".join(parts)

    def __repr__(self):
        return f"Disease(name={self.name}, stage={self.stage}, " \
               f"beta={self.beta}, " \
               f"progress={self.progress}, " \
               f"too_ill_to_move={self.too_ill_to_move}, contrib_foi=" \
               f"{self.contrib_foi})"

    def __eq__(self, other):
        return \
            self.stage == other.stage and \
            self.mapping == other.mapping and \
            self.beta == other.beta and \
            self.progress == other.progress and \
            self.too_ill_to_move == other.too_ill_to_move and \
            self.contrib_foi == other.contrib_foi and \
            self.start_symptom == other.start_symptom

    def __len__(self):
        if self.beta:
            return len(self.beta)
        else:
            return 0

    def __getitem__(self, index: int) -> _Dict[str, _Union[str, float, bool]]:
        """Return the values of parameters of the stage as specified
           index
        """
        index = int(index)

        if abs(index) >= len(self):
            raise IndexError(f"Invalid index {index}. Size = {len(self)}")

        return {"name": self.stage[index],
                "mapping": self.mapping[index],
                "beta": self.beta[index],
                "progress": self.progress[index],
                "too_ill_to_move": self.too_ill_to_move[index],
                "contrib_foi": self.contrib_foi[index],
                "is_start_symptom": (index+1) == self.start_symptom}

    def __setitem__(self, index: int,
                    value: _Dict[str, _Union[str, float, bool]]) -> None:
        """Set the value of parameters at this index. The keys in the
           dictionary (and their values) match the arguments to the
           "insert" or "add" functions
        """
        if abs(index) >= len(self):
            raise IndexError(f"Invalid index {index}. Size = {len(self)}")

        name = value.get("name", "*")
        mapping = value.get("mapping", None)

        if mapping is None:
            mapping = _infer_mapping([name])[0]

        beta = value.get("beta", None)

        if beta is None:
            if mapping.upper() == "I":
                beta = 0.5
            else:
                beta = 0.0

        progress = value.get("progress", None)

        if progress is None:
            if mapping.upper() == "R":
                progress = 0.0
            else:
                progress = 1.0

        too_ill_to_move = value.get("too_ill_to_move", None)

        if too_ill_to_move is None:
            too_ill_to_move = 0.0

        contrib_foi = value.get("contrib_foi", None)

        if contrib_foi is None:
            contrib_foi = 1.0

        is_start_symptom = value.get("is_start_symptom", None)

        name = str(name)
        mapping = str(mapping)

        beta = float(beta)

        if beta < 0 or beta > 1:
            raise ValueError(
                f"Invalid value of beta {beta}. Should be 0 <= beta <= 1")

        progress = float(progress)

        if progress < 0 or progress > 1:
            raise ValueError(
                f"Invalid value of progress {progress}. Should be "
                f"0 <= progress <= 1")

        too_ill_to_move = float(too_ill_to_move)

        if too_ill_to_move < 0 or too_ill_to_move > 1:
            raise ValueError(
                f"Invalid value of too_ill_to_move {too_ill_to_move}. "
                f"Should be 0 <= too_ill_to_move <= 1")

        contrib_foi = float(contrib_foi)

        if contrib_foi < 0:
            raise ValueError(
                f"Invalid value of contrib_foi {contrib_foi}. Should "
                f"be 0 <= contrib_foi")

        self.stage[index] = name
        self.mapping[index] = mapping
        self.beta[index] = beta
        self.progress[index] = progress
        self.too_ill_to_move[index] = too_ill_to_move
        self.contrib_foi[index] = contrib_foi

        if is_start_symptom:
            self.start_symptom = index + 1
        elif is_start_symptom is None and self.start_symptom is None:
            if mapping.upper() == "I":
                self.start_symptom = index + 1

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
            raise AssertionError(f"Data read for disease {self.name} "
                                 f"is corrupted! {e.__class__}: {e}")

        if self.stage is None and n < 4:
            raise AssertionError(
                f"There must be at least 4 disease stages ('*', 'E', 'I', "
                f"'R') - the number of stages here is {n}")

        elif n == 0:
            # we haven't set any parameters. This is likely an "overall"
            # disease file, where just names are needed. Populate wuth
            # default parameters
            n = len(self.stage)

            self.beta = [0.0] * n
            self.progress = [1.0] * n
            self.too_ill_to_move = [0.0] * n
            self.contrib_foi = [1.0] * n

            self.progress[-1] = 0.0

        if self.start_symptom is None or self.start_symptom == 0:
            self.start_symptom = min(3, n)

        if self.start_symptom is None or self.start_symptom < 1 or \
                self.start_symptom > n:
            raise AssertionError(f"start_symptom {self.start_symptom} is "
                                 f"invalid for a disease with {n} stages. "
                                 f"It should be between 1 and {n}")

        self.start_symptom = int(self.start_symptom)

        from ._interpret import Interpret

        for i in range(0, n):
            try:
                self.progress[i] = Interpret.number(self.progress[i])
                self.too_ill_to_move[i] = Interpret.number(
                    self.too_ill_to_move[i])
                self.beta[i] = Interpret.number(self.beta[i])
                self.contrib_foi[i] = Interpret.number(self.contrib_foi[i])
            except Exception as e:
                raise AssertionError(
                    f"Invalid disease parameter at index {i}: "
                    f"{e.__class__} {e}")

        # for the model to work the different stages have set meanings
        errors = []

        if self.stage is None:
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

            # - stage 1 is 'latent', meaning that beta must be 0
            # (not infective)
            if self.beta[1] != 0.0:
                errors.append(
                    f"The beta[1] value must be 0.0 as 'latent' individuals "
                    f"are not infectious and should not be able to infect "
                    f"others.")

            # - stage -1 is 'recovered', meaning that beta must not be 0
            #   and progress is 0, as once recovered, always recovered
            if self.beta[-1] != 0.0:
                errors.append(
                    f"The beta[-1] value must be 0.0 as 'recovered' "
                    f"are not infectious and should not be able to infect "
                    f"others.")

            if self.progress[-1] != 0.0:
                errors.append(
                    f"The progress[-1] value must be 0.0 as 'recovered' "
                    f"individuals have no further disease stage to progress "
                    f"to. We hope that once recovered, always recovered.")

            if len(errors) > 0:
                from .utils._console import Console
                Console.error("\n".join(errors))
                raise AssertionError("Invalid disease parameters!\n" +
                                     "\n".join(errors))

            # set the default names - these are '*', "E", "I?", "R"
            self.stage = ["R"] * self.N_INF_CLASSES()

            self.stage[0] = "*"
            self.stage[1] = "E"

            if len(self.stage) == 4:
                self.stage[2] = "I"
            else:
                j = 1
                for i in range(2, self.N_INF_CLASSES() - 1):
                    self.stage[i] = f"I{j}"
                    j += 1
        else:
            if len(self.stage) != n:
                raise AssertionError(
                    f"Number of named stages ({len(self.stage)}) does not "
                    f"equal the number of stages ({n}).")

            self.stage = [str(x) for x in self.stage]

        if self.mapping is None:
            if self.stage is None:
                # default mapping is first stage is '*', second stage is 'E',
                # last stage is 'R' and remaining stages are 'I'
                self.mapping = ["I"] * self.N_INF_CLASSES()
                self.mapping[0] = "*"
                self.mapping[1] = "E"
                self.mapping[-1] = "R"
            else:
                # the mapping is the character part of the stage name, e.g.
                # "H1" maps to "H", "ICU2" maps to ICU etc.
                self.mapping = _infer_mapping(self.stage)

        elif len(self.mapping) != self.N_INF_CLASSES():
            raise AssertionError(
                f"Invalid number of mapping stages. Should be "
                f"{self.N_INF_CLASSES()} but got {len(self.mapping)}.")

        else:
            mapping = _infer_mapping(self.stage)

            for i, v in enumerate(self.mapping):
                if v is None:
                    self.mapping[i] = mapping[i]

            valid = set(mapping + self.stage + ["E", "I", "R", "*"])

            for v in self.mapping:
                if v not in valid:
                    raise AssertionError(
                        f"Invalid mapping value '{v}'. Valid values "
                        f"are only {valid}")

    def insert(self, index: int, name: str, mapping: str = None,
               beta: float = None, progress: float = None,
               too_ill_to_move: float = None, contrib_foi: float = None,
               is_start_symptom: bool = None) -> None:
        """Insert a new stage into the disease. This will insert a new stage
           into the list of stages at index 'index'

           Parameters
           ----------
           index: str
             The index at which to insert the new stage
           name: str
             The name of the stage, e.g. "E", "I", "R" etc.
           mapping: str
             Which main stage this stage should map to (if this is a
             sub-stage). This will be derived automatically if not set.
           beta: float
             The beta (infectivity) parameter. This should be between
             0.0 amd 1.0. If not set, then this will be set automatically.
           progress: float
             The fraction of individuals at this stage who will move to
             the next stage. This should be between 0.0 amd 1.0. If this
             is not set, then this will be set automatically.
           too_ill_to_move: float
             The proportion of workers at this stage who do not travel
             to work. This should be between 0.0 and 1.0. If this is not
             set, then this will be set automatically.
           contrib_foi: float
             The contribution of individuals in this stage to the
             force-of-infection (foi) of the wards they visit. This
             should normally be 1.0 and will be set automatically
             if not set.
           is_start_symptom: bool
             Whether this is the start symptom of the disease. This
             normally doesn't need to be set as this will be worked
             out automatically by the code.
        """
        index = int(index)

        if self.beta is None:
            if self.name is None:
                self.name = "unnamed"

            self.stage = []
            self.mapping = []
            self.beta = []
            self.progress = []
            self.too_ill_to_move = []
            self.contrib_foi = []

        if len(self.beta) <= abs(index):
            while len(self.beta) <= abs(index):
                self.stage.append("*")
                self.mapping.append("*")
                self.beta.append(0.0)
                self.progress.append(1.0)
                self.too_ill_to_move.append(0.0)
                self.contrib_foi.append(1.0)
        else:
            self.stage.insert(index, "*")
            self.mapping.insert(index, "*")
            self.beta.insert(index, 0.0)
            self.progress.insert(index, 1.0)
            self.too_ill_to_move.insert(index, 0.0)
            self.contrib_foi.insert(index, 1.0)

        self.__setitem__(index, {"name": name,
                                 "mapping": mapping,
                                 "beta": beta,
                                 "progress": progress,
                                 "too_ill_to_move": too_ill_to_move,
                                 "contrib_foi": contrib_foi,
                                 "is_start_symptom": is_start_symptom})

    def add(self, name: str, mapping: str = None,
            beta: float = None, progress: float = None,
            too_ill_to_move: float = None, contrib_foi: float = None,
            is_start_symptom: bool = None) -> None:
        """Add a new stage to the disease. This will append a new stage
           onto the list of stages.

           Parameters
           ----------
           name: str
             The name of the stage, e.g. "E", "I", "R" etc.
           mapping: str
             Which main stage this stage should map to (if this is a
             sub-stage). This will be derived automatically if not set.
           beta: float
             The beta (infectivity) parameter. This should be between
             0.0 amd 1.0. If not set, then this will be set automatically.
           progress: float
             The fraction of individuals at this stage who will move to
             the next stage. This should be between 0.0 amd 1.0. If this
             is not set, then this will be set automatically.
           too_ill_to_move: float
             The proportion of workers at this stage who do not travel
             to work. This should be between 0.0 and 1.0. If this is not
             set, then this will be set automatically.
           contrib_foi: float
             The contribution of individuals in this stage to the
             force-of-infection (foi) of the wards they visit. This
             should normally be 1.0 and will be set automatically
             if not set.
           is_start_symptom: bool
             Whether this is the start symptom of the disease. This
             normally doesn't need to be set as this will be worked
             out automatically by the code.
        """
        idx = 0 if self.beta is None else len(self.beta)

        self.insert(idx, name=name, mapping=mapping, beta=beta,
                    progress=progress, too_ill_to_move=too_ill_to_move,
                    contrib_foi=contrib_foi,
                    is_start_symptom=is_start_symptom)

    def get_index(self, idx):
        """Return the index of disease stage 'idx' in this disease"""
        if isinstance(idx, str):
            # lookup by name
            for i, name in enumerate(self.stage):
                if idx == name:
                    return i

            raise KeyError(
                f"There is no disease stage called {idx}. Available "
                f"stages are {self.stage}.")
        else:
            idx = int(idx)

            if idx < 0:
                idx = self.N_INF_CLASSES() + idx

            if idx < 0 or idx >= self.N_INF_CLASSES():
                raise IndexError(
                    f"There is no diseaes stage at index {idx}. The number "
                    f"of stages is {self.N_INF_CLASSES()}")

            return idx

    def get_mapping_to(self, other):
        """Return the mapping from stage index i of this disease to
           stage index j other the passed other disease. This returns
           'None' if there is no need to map because the stages
           are the same.

           The mapping will map the states according to their label,
           matching the ith labelled X state in this disease to the
           ith labelled X state in other (or to the highest labelled
           X state if we have more of these states than other).

           Thus, is we have;

           self =  ["*", "E", "I", "I", "R"]
           other = ["*", "E", "I", "I", "I", "R"]

           then

           self.get_mapping_to(other) = [0, 1, 2, 3, 5]
           other.get_mapping_to(self) = [0, 1, 2, 3, 3, 4]

           If we can't map a state, then we will try to map to "I".
           If we still can't map, then this is an error.
        """
        if self.mapping == other.mapping:
            # no need to map,
            return None

        mapping = []

        stages = {"*": [],
                  "E": [],
                  "I": [],
                  "R": []}

        for i, stage in enumerate(other.mapping):
            try:
                stages[stage].append(i)
            except KeyError:
                stages[stage] = [i]

        for stage in self.mapping:
            try:
                s = stages[stage]
            except KeyError:
                s = stages["I"]

            if len(s) == 0:
                # we are mapped to an invalid state
                mapping.append(-1)
            elif len(s) == 1:
                mapping.append(s[0])
            else:
                mapping.append(s.pop(0))

        if -1 in mapping:
            # we are missing a state
            raise ValueError(
                f"It is not possible to map from {self.mapping} to "
                f"{other.mapping}, as the stages marked '-1' cannot be "
                f"safely mapped: {mapping}")

        return mapping

    @staticmethod
    def load(disease: str = None,
             repository: str = None,
             folder: str = None,
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

        import os

        is_local_file = False

        if filename is None:
            if disease is None:
                disease = "ncov"

            if folder is not None:
                d = os.path.join(folder, disease)
                if os.path.exists(d):
                    filename = disease
                    is_local_file = True
                elif os.path.exists(f"{d}.json"):
                    filename = f"{d}.json"
                    is_local_file = True
                elif os.path.exists(f"{d}.json.bz2"):
                    filename = f"{d}.json.bz2"
                    is_local_file = True

            if filename is None:
                if os.path.exists(disease):
                    filename = disease
                    is_local_file = True
                elif os.path.exists(f"{disease}.json"):
                    filename = f"{disease}.json"
                    is_local_file = True
                elif os.path.exists(f"{disease}.json.bz2"):
                    filename = f"{disease}.json.bz2"
                    is_local_file = True

        if filename is None:
            from ._parameters import get_repository
            repository, v = get_repository(repository)

            if folder is None:
                folder = _default_folder_name

            filename = os.path.join(repository, folder,
                                    f"{disease}.json")

            repository = v["repository"]
            repository_version = v["version"]
            repository_branch = v["branch"]

        if is_local_file:
            disease = Disease.from_json(filename)
            disease._filename = filename
            return disease

        json_file = os.path.abspath(filename)

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

        data["name"] = disease

        disease = Disease.from_data(data)
        disease._filename = json_file,
        disease._repository = repository,
        disease._repository_branch = repository_branch,
        disease._repository_version = repository_version

        return disease

    @staticmethod
    def from_data(data) -> Disease:
        """Return a new Disease constructed from the passed data
           dictionary (e.g. deserialised from json)
        """
        beta = data.get("beta", [])
        default = [1.0] * len(beta)

        progress = data.get("progress", [])
        too_ill_to_move = data.get("too_ill_to_move", default)
        contrib_foi = data.get("contrib_foi", default)

        start_symptom = data.get("start_symptom", None)

        disease = Disease(beta=beta,
                          progress=progress,
                          too_ill_to_move=too_ill_to_move,
                          contrib_foi=contrib_foi,
                          start_symptom=start_symptom,
                          mapping=data.get("mapping", None),
                          stage=data.get("stage", None),
                          name=data.get("name", "unnamed"),
                          _authors=data.get("author(s)", None),
                          _contacts=data.get("contact(s)", None),
                          _references=data.get("reference(s)", None))

        disease._validate()

        return disease

    def to_data(self) -> _Dict[str, any]:
        """Return a data dictionary version of this disease, suitable
           for serialising to, e.g., json
        """
        self._validate()

        data = {}

        if self.name is not None:
            data["name"] = str(self.name)

        if self.stage is not None:
            data["stage"] = [str(x) for x in self.stage]

        if self.mapping is not None:
            data["mapping"] = [str(x) for x in self.mapping]

        if self.beta is not None:
            data["beta"] = [float(x) for x in self.beta]

        if self.progress is not None:
            data["progress"] = [float(x) for x in self.progress]

        if self.too_ill_to_move is not None:
            data["too_ill_to_move"] = [float(x) for x in self.too_ill_to_move]

        if self.contrib_foi is not None:
            data["contrib_foi"] = [float(x) for x in self.contrib_foi]

        if self.start_symptom is not None:
            data["start_symptom"] = int(self.start_symptom)

        if self._authors is not None:
            data["author(s)"] = str(self._authors)

        if self._contacts is not None:
            data["contact(s)"] = str(self._contacts)

        if self._references is not None:
            data["reference(s)"] = str(self._references)

        return data

    @staticmethod
    def from_json(s: str) -> Disease:
        """Return the Disease constructed from the passed json. This will
           either load from a passed json string, or from json loaded
           from the passed file
        """
        import os
        import json

        if os.path.exists(s):
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
            Console.error(f"Unable to load a Disease from '{s}'. Check that "
                          f"this is valid JSON or that the file exists.")

            raise IOError(f"Cannot load Disease from '{s}'")

        return Disease.from_data(data)

    def to_json(self, filename: str = None, indent: int = None,
                auto_bzip: bool = True) -> str:
        """Serialise the Disease to JSON. This will write to a file
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
