
from typing import List as _List
from typing import Dict as _Dict
from typing import Union as _Union

__all__ = ["VariableSets", "VariableSet"]


def _set_beta(params, name: str, index: int, value: float):
    """Adjust the Disease.beta parameter"""
    params.disease_params.beta[index] = float(value)


def _set_progress(params, name: str, index: int, value: float):
    """Adjust the Disease.progress parameter"""
    params.disease_params.progress[index] = float(value)


def _set_too_ill_to_move(params, name: str, index: int, value: float):
    """Adjust the Disease.too_ill_to_move parameter"""
    params.disease_params.too_ill_to_move[index] = float(value)


def _set_contrib_foi(params, name: str, index: int, value: float):
    """Adjust the Disease.contrib_foi parameter"""
    params.disease_params.contrib_foi[index] = float(value)


def _set_lengthday(params, name: str, index: int, value: float):
    """Adjust the Parameters.length_day parameter"""
    if index is not None:
        raise IndexError("You cannot index the lengthday")

    params.length_day = float(value)


def _set_plengthday(params, name: str, index: int, value: float):
    """Adjust the Parameters.plength_day parameter"""
    if index is not None:
        raise IndexError("You cannot index the lengthday")

    params.plength_day = float(value)


def _set_uv(params, name: str, index: int, value: float):
    """Adjust the Parameters.UV parameter"""
    if index is not None:
        raise IndexError("You cannot index the UV parameter")

    params.UV = float(value)


def _set_initial_inf(params, name: str, index: int, value: float):
    """Adjust the Parameters.initial_inf parameter"""
    if index is not None:
        raise IndexError("You cannot index the initial_inf parameter")

    params.initial_inf = float(value)


def _set_static_play_at_home(params, name: str, index: int, value: float):
    """Adjust the Parameters.static_play_at_home parameter"""
    if index is not None:
        raise IndexError("You cannot index the static_play_at_home parameter")

    params.static_play_at_home = float(value)


def _set_dyn_play_at_home(params, name: str, index: int, value: float):
    """Adjust the Parameters.dyn_play_at_home parameter"""
    if index is not None:
        raise IndexError("You cannot index the dyn_play_at_home parameter")

    params.dyn_play_at_home = float(value)


def _set_data_dist_cutoff(params, name: str, index: int, value: float):
    """Adjust the Parameters.data_dist_cutoff parameter"""
    if index is not None:
        raise IndexError("You cannot index the data_dist_cutoff parameter")

    params.data_dist_cutoff = float(value)


def _set_dyn_dist_cutoff(params, name: str, index: int, value: float):
    """Adjust the Parameters.dyn_dist_cutoff parameter"""
    if index is not None:
        raise IndexError("You cannot index the dyn_dist_cutoff parameter")

    params.dyn_dist_cutoff = float(value)


def _set_play_to_work(params, name: str, index: int, value: float):
    """Adjust the Parameters.play_to_work parameter"""
    if index is not None:
        raise IndexError("You cannot index the play_to_work parameter")

    params.play_to_work = float(value)


def _set_work_to_play(params, name: str, index: int, value: float):
    """Adjust the Parameters.work_to_play parameter"""
    if index is not None:
        raise IndexError("You cannot index the work_to_play parameter")

    params.work_to_play = float(value)


def _set_local_vaccination_thresh(params, name: str, index: int, value: float):
    """Adjust the Parameters.local_vaccination_thresh parameter"""
    if index is not None:
        raise IndexError("You cannot index the local_vaccination_thresh "
                         "parameter")

    params.local_vaccination_thresh = float(value)


def _set_global_detection_thresh(params, name: str, index: int, value: float):
    """Adjust the Parameters.global_detection_thresh parameter"""
    if index is not None:
        raise IndexError("You cannot index the global_detection_thresh "
                         "parameter")

    params.global_detection_thresh = float(value)


def _set_daily_ward_vaccination_capacity(params, name: str,
                                         index: int, value: float):
    """Adjust the Parameters.daily_ward_vaccination_capacity
       parameter
    """
    if index is not None:
        raise IndexError("You cannot index the daily_ward_vaccination "
                         "parameter")

    params.daily_ward_vaccination_capacity = float(value)


def _set_neighbour_weight_threshold(params, name: str,
                                    index: int, value: float):
    """Adjust the Parameters.neighbour_weight_threshold parameter"""
    if index is not None:
        raise IndexError("You cannot index the neighbour_weight_threshold "
                         "parameter")

    params.neighbour_weight_threshold = float(value)


def _set_daily_imports(params, name: str, index: int, value: float):
    """Adjust the Parameters.daily_imports parameter"""
    if index is not None:
        raise IndexError("You cannot index the daily_imports parameter")

    params.daily_imports = float(value)


def _set_user_params(params, name: str, index: int, value: float):
    """Adjust a custom user-supplied parameter, held in
       Parameters.user_params[name]. Set a user parameter
       called 'name' via 'user.name' or '.name'.
    """
    if name.startswith("user."):
        name = name[5:]
    elif name.startswith("."):
        name = name[1:]

    if params.user_params is None:
        params.user_params = {}

    if index is None:
        params.user_params[name] = value
    else:
        if name not in params.user_params:
            params.user_params[name] = []

        while len(params.user_params[name]) <= index:
            params.user_params[name].append(None)

        params.user_params[name][index] = value


_adjustable = {}
_adjustable["beta"] = _set_beta
_adjustable["progress"] = _set_progress
_adjustable["too_ill_to_move"] = _set_too_ill_to_move
_adjustable["contrib_foi"] = _set_contrib_foi
_adjustable["user"] = _set_user_params
_adjustable["length_day"] = _set_lengthday
_adjustable["plength_day"] = _set_plengthday
_adjustable["UV"] = _set_uv
_adjustable["initial_inf"] = _set_initial_inf
_adjustable["static_play_at_home"] = _set_static_play_at_home
_adjustable["dyn_play_at_home"] = _set_dyn_play_at_home
_adjustable["data_dist_cutoff"] = _set_data_dist_cutoff
_adjustable["dyn_dist_cutoff"] = _set_dyn_dist_cutoff
_adjustable["play_to_work"] = _set_play_to_work
_adjustable["work_to_play"] = _set_work_to_play
_adjustable["local_vaccination_thesh"] = _set_local_vaccination_thresh
_adjustable["global_detection_thresh"] = _set_global_detection_thresh
_adjustable["daily_ward_vaccination_capacity"] = \
    _set_daily_ward_vaccination_capacity
_adjustable["neighbour_weight_threshold"] = _set_neighbour_weight_threshold
_adjustable["daily_imports"] = _set_daily_imports


def _clean(x):
    """Clean the passed string by stripping off unnecesary characters,
       and turning "True" and "False" into 1 and 0. Also change
       '=' and ':' into '=='
    """
    x = x.strip()

    if x.lower() == "true":
        return True
    elif x.lower() == "false":
        return False
    elif x == "=" or x == ":":
        return "=="
    elif x.endswith("=="):
        return x[0:-2], "=="
    elif x.endswith(":") or x.endswith("="):
        return x[0:-1], "=="
    else:
        return x


def _interpret(value):
    if not isinstance(value, str):
        return value

    canonical = value.lower().replace('"', "'")

    if canonical.startswith("d'"):
        # this is a date
        try:
            from dateparser import parse
            return parse(value[2: -1]).date()
        except Exception:
            pass

        from datetime import date
        return date.fromisoformat(value[2: -1])

    elif canonical.startswith("f'"):
        # this is a floating point number
        return float(value[2: -1])

    elif canonical.startswith("i'"):
        # this is an integer
        return int(value[2:-1])

    elif canonical.startswith("s'"):
        # this is a string
        return value[2:-1]

    # now we have to guess...
    try:
        v = float(value)
        if v.is_integer():
            return int(v)
        else:
            return v
    except Exception:
        pass

    try:
        from datetime import date
        return date.fromisoformat(value)
    except Exception:
        pass

    try:
        from .utils._safe_eval import safe_eval_number
        return safe_eval_number(value)
    except Exception:
        pass

    # do this last as it is quite slow...
    try:
        from dateparser import parse
        return parse(value).date()
    except Exception:
        pass

    # this can only be a string...
    return value


def _wrap(text, width=70):
    """Return 'text' wrapped to at most 'width' characters, as
       a list of lines
    """
    import textwrap
    text = text.strip().replace(r"\s+", " ").replace("\n", " ")
    return textwrap.wrap(text, width)


class VariableSet:
    """This class holds a single set of adjustable variables that
       are used to adjust the variables as part of a model run

       Examples
       --------
       >>> v = VariableSet()
       >>> v["beta[1]"] = 0.95
       >>> v["beta[2]"] = 0.9
       >>> print(v.fingerprint())
       (beta[1]=0.95, beta[2]=0.9)[repeat 1]
       >>> params = Parameters()
       >>> params.set_disease("ncov")
       >>> v.adjust(params)
       >>> print(params.disease_params.beta[1],
       >>>       params.disease_params.beta[2])
       0.95 0.9
    """

    def __init__(self,
                 variables: _Dict[str, float] = None,
                 repeat_index: int = 1,
                 names: _List[str] = None,
                 values: _List[float] = None):
        """Construct a new VariableSet from the passed adjusted variable
           values.

           Parameters
           ----------
           names: List[str]
             The list of the names of the variables to adjust
           values: List[float]
             The values of the variables to adjust (same order as names)
           variables: Dict[str, float]
             names and values of variables to adjust passed as a dictionary
           repeat_index: int
             the index used to distinguish different repeats of the same
             VariableSet from one another

           Examples
           --------
           >>> v = VariableSet()
           >>> v["beta[1]"] = 0.95
           >>> v["beta[2]"] = 0.9
           >>> print(v.fingerprint())
           (beta[1]=0.95, beta[2]=0.9)[repeat 1]
        """
        self._names = None
        self._vals = None
        self._varnames = None
        self._varidxs = None
        self._idx = None
        self._output = None

        if variables is not None:
            for name, value in variables.items():
                self._add(name, value)

        if values is not None:
            if names is None:
                names = ["beta[2]", "beta[3]", "progress[1]",
                         "progress[2]", "progress[3]"]

            if len(names) != len(values):
                raise IndexError(
                    f"The number of variable values '{values}' must equal "
                    f"the number of variable names '{names}'")

            for name, value in zip(names, values):
                self._add(name, value)

        self._idx = repeat_index

    def __str__(self):
        """Return a printable representation of the variables to
           be adjusted
        """
        s = []

        if self._vals is not None and len(self._vals) > 0:
            for key, value in zip(self._names, self._vals):
                s.append(f"{key}={value}")

        if len(s) == 0:
            return f"(NO_CHANGE)[repeat {self._idx}]"
        else:
            return f"({', '.join(s)})[repeat {self._idx}]"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, dict):
            other = VariableSet(variables=other)

        if self._idx != other._idx:
            return False

        if len(self) != len(other):
            return False

        if self._vals is None:
            return

        for i in range(0, len(self._vals)):
            if self._vals[i] != other._vals[i]:
                return False

            if self._varnames[i] != other._varnames[i]:
                return False

            if self._varidxs[i] != other._varidxs[i]:
                return False

            if self._names[i] != other._names[i]:
                return False

        return True

    def __len__(self):
        if self._vals is None:
            return 0
        else:
            return len(self._vals)

    def __getitem__(self, key):
        if self._vals is None:
            raise KeyError(f"No adjustable parameter {key} in an empty set")

        if key.startswith("user."):
            key = key[4:]

        for i, name in enumerate(self._names):
            if key == name:
                return self._vals[i]

        raise KeyError(f"No adjustable parameter {key}. Available parameters "
                       f"are '{self._names}'")

    def __setitem__(self, key, value):
        if self._names is None:
            self._names = []

        for i, name in enumerate(self._names):
            if key == name:
                self._vals[i] = value
                return

        self._add(key, value)

    def _add(self, name, value):
        """Internal function to add a new variable called 'name' to
           be varied - it will be set equal to 'value'
        """
        import re

        if self._vals is None:
            self._names = []
            self._vals = []
            self._varnames = []
            self._varidxs = []

        name = name.strip()

        if name == "output":
            # this is the output directory for this run. This will
            # replace the default name, which is based on the fingerprint
            value = str(value).strip()

            if len(value) == 0:
                raise ValueError("You cannot use an empty string as the "
                                 "output directory")

            self._output = value
            return

        # look for 'variable[index]'
        m = re.search(r"([\s:\.\w]+)\[(\d+)\]", name)

        if m:
            varname = m.group(1)
            index = int(m.group(2))
            value = value
        else:
            varname = name
            index = None
            value = value

        if varname.find(":") != -1:
            # this sets the variable in a demographic
            parts = varname.split(":")

            if len(parts) != 2:
                raise KeyError(
                    f"It is not possible to adjust the variable {name} to "
                    f"equal {value} as it is not in the format "
                    f"variable=value or demographic:variable=value")

            demographic = parts[0]
            varname = parts[1]
        else:
            demographic = None

        if not (varname.startswith("user.") or varname.startswith(".") or
                varname in _adjustable):
            raise KeyError(f"It is not possible to adjust the variable "
                           f"{name} to equal {value}. Available variables "
                           f"are {list(_adjustable.keys())}, or to set "
                           f"a user parameter 'user.parameter' or "
                           f"'.parameter'. To set an index use "
                           f"'parameter[index]', e.g. 'beta[2]'")

        if varname.startswith("user."):
            # strip off 'user' so that it just starts with a dot
            varname = varname[4:]

        if name.startswith("user."):
            name = name[4:]

        if demographic is None:
            self._varnames.append(varname)
        else:
            self._varnames.append((demographic, varname))

        self._varidxs.append(index)
        self._names.append(name)
        self._vals.append(value)

    @staticmethod
    def adjustable_help():
        """Return a string that contains some help that is useful
           for finding out which variables can be adjusted
        """
        lines = []

        names = list(_adjustable.keys())
        names.sort()

        for name in names:
            func = _adjustable[name]
            docs = _wrap(func.__doc__, 60)
            lines.append("")
            lines.append(f"{name}:")

            for doc in docs:
                lines.append(f"  {doc}")

        return "\n".join(lines)

    def variable_names(self):
        """Return the names of the variables that will be adjusted
           by this VariableSet

           Returns
           -------
           names: List[str]
             The list of names of variables to be adjusted
        """
        if self._vals is None or len(self._vals) == 0:
            return None
        else:
            from copy import deepcopy
            return deepcopy(self._names)

    def variable_values(self):
        """Return the values that the variables will be adjusted to.
           Note that 'None' means that the variable won't be adjusted
           from its default (original) value

           Returns
           -------
           values: List[float]
             The list of values for variables to be adjusted to
        """
        if self._vals is None or len(self._vals) == 0:
            return None
        else:
            from copy import deepcopy
            return deepcopy(self._vals)

    def variables(self):
        """Return the variables (name and values) to be adjusted

           Returns
           -------
           variables: Dict[str, float]
             The dictionary mapping the names of the variables that
             with be adjusted to their desired values
        """
        v = {}

        for name, value in zip(self._names, self._vals):
            v[name] = value

        return v

    def repeat_index(self):
        """Return the repeat index of this set. The repeat index is the
           ID of this set if the VariableSet is repeated. The index should
           range from 1 to nrepeats

           Returns
           -------
           index: int
             The repeat index of this set
        """
        return self._idx

    def make_compatible_with(self, other):
        """Return a copy of this VariableSet which has been made
           compatible with 'other'. This means that it will change
           the same variables as 'other', e.g. by adding 'None'
           changes for missing variables. This will raise an error
           if it is not possible to make this set compatible

           Parameters
           ----------
           other: VariableSet
             The passed VariableSet for which this should be made compatible

           Returns
           -------
           result: VariableSet
             A copy of this VariableSet which is now compatible with 'other'

           Example
           -------
           >>> v1 = VariableSet()
           >>> v1["beta[1]"] = 0.9
           >>> v1["beta[2]"] = 0.8

           >>> v2 = VariableSet()
           >>> v2["beta[1]"] = 0.6
           >>> v2 = v2.make_compatible_with(v1)
           >>> print(v2)
           (beta[1]=0.6, beta[2]=0.8)[repeat 1]
        """
        from copy import deepcopy

        if self._names is None:
            v = deepcopy(other)
            v._idx = self._idx
            return v

        if other._names is None:
            raise ValueError(f"VariableSet {self} is not compatible with "
                             f"VariableSet {other}")

        nmatch = 0

        for name in self._names:
            if name not in other._names:
                raise ValueError(f"VariableSet {self} is not compatible with "
                                 f"VariableSet {other}")
            nmatch += 1

        if len(other._names) == nmatch:
            # fully compatible
            return deepcopy(self)

        v = deepcopy(self)

        for name in other._names:
            if name not in self._names:
                v[name] = other[name]

        return v

    @staticmethod
    def _extract_values(fingerprint: str):
        fingerprint = str(fingerprint)

        # has this fingerprint been added onto the end of a filename
        # using a hyphen or underscore? If so, then remove this
        if fingerprint.find("-") != -1:
            fingerprint = fingerprint.split("-")[-1]

        if fingerprint.find("_") != -1:
            fingerprint = fingerprint.split("_")[-1]

        fingerprint.strip()

        # does this have a repeat index - if so, this is the last
        # value at the end after the 'x'
        parts = fingerprint.split("x")

        if len(parts) > 1:
            repeat_index = int(parts[-1])
            fingerprint = "x".join(parts[0:-1])
        else:
            repeat_index = None

        # now get the values
        values = []

        if fingerprint != "REPEAT":
            for part in fingerprint.split("v"):
                try:
                    if part == "T":
                        values.append(True)
                    elif part == "F":
                        values.append(False)
                    else:
                        values.append(float(part.replace("i", ".")))
                except Exception:
                    # this is not part of the fingerprint
                    pass

        return (values, repeat_index)

    @staticmethod
    def extract_values(fingerprint: str):
        """Return the original values from the passed fingerprint
           or filename. This assumes that the fingerprint
           was created using the 'fingerprint' function, namely
           that any integers are actually 0.INTEGER

           Parameters
           ----------
           fingerprint: str
             The fingerprint (or filename) to decode

           Returns
           -------
           (values, repeat): (List[float], int)
             The list of values of the variables and the repeat
             index. The repeat index is None if it wasn't included
             in the fingerprint
        """
        from pathlib import Path

        path = fingerprint

        # if this is a filename then extract only the fingerprint
        fingerprint = Path(Path(fingerprint).name)
        for suffix in fingerprint.suffixes:
            fingerprint = str(fingerprint).replace(suffix, "")

        values, repeat_idx = VariableSet._extract_values(fingerprint)

        if len(values) > 0 or repeat_idx is not None:
            return (values, repeat_idx)

        import os

        if path.find(os.path.sep) != -1:
            fingerprint = os.path.sep.join(
                path.split(os.path.sep)[0:-1])
            return VariableSet.extract_values(fingerprint)
        else:
            return (values, repeat_idx)

    @staticmethod
    def create_fingerprint(vals: _List[float], index: int = None,
                           include_index: bool = False):
        """Create the fingerprint for the passed values"""
        f = None

        if vals is None or len(vals) == 0:
            f = "REPEAT"
        else:
            for val in vals:
                if isinstance(val, bool):
                    if val:
                        v = "T"
                    else:
                        v = "F"
                else:
                    v = float(val)

                    if v.is_integer():
                        v = int(val)
                        v = f"{v}.0"

                    v = str(v).replace(".", "i")

                if f is None:
                    f = v
                else:
                    f += "v" + v

        if include_index:
            return "%sx%03d" % (f, index)
        else:
            return f

    def fingerprint(self, include_index: bool = False):
        """Return a fingerprint for this VariableSet. This can be
           used to quickly identify and distinguish the values of
           the variables in this set from the values in other
           VariableSets which have the same adjustable variables,
           but different parameters

           Parameters
           ----------
           include_index: bool
             Whether or not to include the repeat_index in the fingerprint

           Returns
           -------
           fingerprint: str
             The fingerprint for this VariableSet
        """
        return VariableSet.create_fingerprint(vals=self._vals,
                                              index=self._idx,
                                              include_index=include_index)

    def output_dir(self):
        """Return the output directory in which runs using this
           variable set should be placed. Normally this would
           be the fingerprint of the variable set, but users may
           prefer to specify their own naming scheme, which
           can be added via a design file
        """
        if self._output is None:
            return self.fingerprint(include_index=True)
        else:
            return self._output

    @staticmethod
    def read(filename: str):
        """Read a single set of adjustable variables from the passed
           file. The file can either write the variables in horizontal
           or vertical mode, using space or comma separated values.

           This is useful for when you want to set a global set of parameters
           at the start of a calculation and don't want to use
           a large VariableSets

           Parameters
           ----------
           filename: str
             The name of the file containing the VariableSet

           Returns
           -------
           variables: VariableSet
             The VariableSet that has been read
        """
        variables = VariableSets.read(filename)

        if len(variables) == 0:
            return VariableSet()
        elif len(variables) != 1:
            raise ValueError(
                "More than one set of variables was read from {filename}")
        else:
            return variables[0]

    def adjust(self, params):  # should be 'Parameters' but circular include
        """Use the variables in this set to adjust the passed parameters.
           Note that this directly modifies 'params'

           Parameters
           ----------
           params: Parameters
             The parameters whose variables will be adjusted

           Returns
           -------
           None

           Examples
           --------
           >>> v = VariableSet()
           >>> v["beta[1]"] = 0.95
           >>> v["beta[2]"] = 0.9
           >>> print(v.fingerprint())
           (beta[1]=0.95, beta[2]=0.9)[repeat 1]
           >>> params = Parameters()
           >>> params.set_disease("ncov")
           >>> v.adjust(params)
           >>> print(params.disease_params.beta[1],
           >>>       params.disease_params.beta[2])
           0.95 0.9
        """
        if self._vals is None or len(self._vals) == 0:
            return

        try:
            # loop over all adjustable variables, and adjust global
            # (all demographic) variables first
            specialised = params.specialised_demographics()

            for varname, varidx, value in zip(self._varnames, self._varidxs,
                                              self._vals):
                if isinstance(varname, tuple):
                    continue

                if varname.startswith("user.") or varname.startswith("."):
                    _adjustable["user"](params=params,
                                        name=varname,
                                        index=varidx,
                                        value=value)
                    for s in specialised:
                        _adjustable["user"](params=params[s],
                                            name=varname,
                                            index=varidx,
                                            value=value)

                elif varname in _adjustable:
                    _adjustable[varname](params=params,
                                         name=varname,
                                         index=varidx,
                                         value=value)
                    for s in specialised:
                        _adjustable[varname](params=params[s],
                                             name=varname,
                                             index=varidx,
                                             value=value)
                else:
                    raise KeyError(
                        f"Cannot set unrecognised parameter {varname} "
                        f"to {value}")

            # now loop over and adjust the demographic-specific values
            # (except for 'overall', which must be done last)
            need_overall = False

            for varname, varidx, value in zip(self._varnames, self._varidxs,
                                              self._vals):
                if isinstance(varname, tuple):
                    demographic, varname = varname
                else:
                    continue

                if demographic == "overall":
                    need_overall = True
                    continue

                if varname.startswith("user.") or varname.startswith("."):
                    _adjustable["user"](params=params[demographic],
                                        name=varname,
                                        index=varidx,
                                        value=value)
                elif varname in _adjustable:
                    _adjustable[varname](params=params[demographic],
                                         name=varname,
                                         index=varidx,
                                         value=value)
                else:
                    raise KeyError(
                        f"Cannot set unrecognised parameter {varname} "
                        f"to {value} in demographic {demographic}")

            # finally(!) loop over and adjust the overall values
            if need_overall:
                for varname, varidx, value in zip(self._varnames,
                                                  self._varidxs,
                                                  self._vals):
                    if isinstance(varname, tuple):
                        demographic, varname = varname
                    else:
                        continue

                    if demographic != "overall":
                        continue

                    if varname.startswith("user.") or varname.startswith("."):
                        _adjustable["user"](params=params[demographic],
                                            name=varname,
                                            index=varidx,
                                            value=value)
                    elif varname in _adjustable:
                        _adjustable[varname](params=params[demographic],
                                             name=varname,
                                             index=varidx,
                                             value=value)
                    else:
                        raise KeyError(
                            f"Cannot set unrecognised parameter {varname} "
                            f"to {value} in demographic {demographic}")

        except Exception as e:
            raise ValueError(
                f"Unable to set parameters from {self}. Error "
                f"equals {e.__class__}: {e}")


class VariableSets:
    """This class holds the collection of all VariableSet objects
       that contain the set of adjustable variables that are used
       to control a single run of the model

       Examples
       --------
       >>> v = VariableSets()
       >>> v.append({"beta[2]": 0.95, "beta[3]": 0.9})
       >>> v.append({"beta[1]": 0.86, "beta[2]": 0.89})
       >>> print(v)
       {(beta[2]=0.95, beta[3]=0.9)[repeat 1], (beta[1]=0.86,
       beta[2]=0.89)[repeat 1]}
       >>> v = v.repeat(2)
       >>> print(v)
       {(beta[2]=0.95, beta[3]=0.9)[repeat 1], (beta[1]=0.86,
       beta[2]=0.89)[repeat 1], (beta[2]=0.95, beta[3]=0.9)[repeat 2],
       (beta[1]=0.86, beta[2]=0.89)[repeat 2]}
    """

    def __init__(self):
        """Initialise an empty VariableSets object

           Parameters
           ----------
           None

           Returns
           -------
           None
        """
        self._vars = []

    def __str__(self):
        s = []

        for v in self._vars:
            s.append(str(v))

        if len(s) == 1:
            return s[0]
        elif len(s) > 0:
            return "{" + ",\n ".join(s) + "\n}"
        else:
            return "VariableSets:empty"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, dict):
            v = VariableSet(variables=other)
            other = VariableSets()
            other.append(v)

        if len(self._vars) != len(other._vars):
            return False

        for v0, v1 in zip(self._vars, other._vars):
            if v0 != v1:
                return False

        return True

    def __len__(self):
        if self._vars is None:
            return 0
        else:
            return len(self._vars)

    def __getitem__(self, i: int):
        """Return the VariableSet at the specified index"""
        if self._vars is None:
            raise IndexError("Cannot index an empty VariableSets object")
        else:
            return self._vars[i]

    def append(self, variables: VariableSet):
        """Append the passed set of variables to the set that will
           be used to run a model. If there are any existing
           VariableSet objects in this list, then the new VariableSet
           must adjust the same variables

           Parameters
           ----------
           variables: VariableSet
             The VariableSet to append to this list. If you pass a
             dict of {str: float} values, then this will automatically
             be converted into a VariableSet. Note that all VariableSet
             objects in a VariableSets must adjust the same variables

           Returns
           -------
           None
        """
        if isinstance(variables, dict):
            variables = VariableSet(variables=variables)

        if self._vars is None:
            self._vars = []

        if len(self._vars) > 0:
            variables = variables.make_compatible_with(self._vars[0])

        self._vars.append(variables)

    def repeat(self, nrepeats: _Union[_List[int], int]):
        """Return a copy of this VariableSet in which all of the
           unique VaribleSet objects have been repeated 'nrepeats'
           times

           Parameters
           ----------
           nrepeats: int or list[int]
             The number of repeats of the VariableSet objects to
             perform. If this is a list, then nrepeats[i] will be
             the number of times to repeat variables[i]

           Returns
           -------
           repeats: VariableSets
             A new VariableSets object containing 'nrepeats' copies
             of the VariableSet objects from this set
        """
        if not isinstance(nrepeats, list):
            nrepeats = [nrepeats]

        if len(nrepeats) == 1 and nrepeats[0] <= 1:
            return self

        from copy import deepcopy

        repeats = VariableSets()

        if len(nrepeats) == 1:
            nrepeats = nrepeats[0]
            for i in range(1, nrepeats+1):
                for v in self._vars:
                    v2 = deepcopy(v)
                    v2._idx = i
                    repeats.append(v2)
        else:
            if len(nrepeats) != len(self._vars):
                raise ValueError(
                    f"Disagreement of the number of repeats {len(nrepeats)} "
                    f"and the number of variables {len(self._vars)}")

            added = True
            n = 1
            while added:
                added = False

                for i, v in enumerate(self._vars):
                    if n <= nrepeats[i]:
                        v2 = deepcopy(v)
                        v2._idx = n
                        repeats.append(v2)
                        added = True

                n += 1

        return repeats

    @staticmethod
    def read(filename: str, line_numbers: _List[int] = None):
        """Read and return collection of VariableSet objects from the
           specified line number(s) of the specified file

           Parameters
           ----------
           filename: str
             The name of the file from which to read the VariableSets
           line_numbers: List[int]
             The line numbers from the file to read. This is 0-indexed,
             meaning that the first line is line 0. If this is None,
             then all lines are read and used

           Returns
           -------
           variables: VariableSets
             The collection of VariableSet objects that have been read,
             in the order they were read from the file
        """
        if not isinstance(line_numbers, list):
            if line_numbers is not None:
                line_numbers = [line_numbers]

        # parse all lines using the csv module
        import csv
        lines = open(filename, "r").readlines()

        csvlines = []
        for line in lines:
            line = line.strip()

            if len(line) > 0 and (not line.startswith("#")):
                csvlines.append(line)

        lines = []

        # first try to guess the dialect of the file (space or comma
        # separated, newline character etc.)
        try:
            dialect = csv.Sniffer().sniff(csvlines[0], delimiters=[" ", ","])
        except Exception:
            from .utils._console import Console
            Console.warning(
                f"Could not identify what sort of separator to use to "
                f"read {filename}, so will assume commas. If this is wrong, "
                f"then could you add commas to separate the "
                f"fields?")
            dialect = csv.excel  #  default comma-separated file

        for line in csv.reader(csvlines, dialect=dialect,
                               quoting=csv.QUOTE_ALL,
                               skipinitialspace=True):
            cleaned = [_clean(x) for x in line]

            line = []

            if len(cleaned) > 0:
                for clean in cleaned:
                    if isinstance(clean, list) or isinstance(clean, tuple):
                        for c in clean:
                            if len(c) > 0:
                                line.append(c)
                    else:
                        line.append(clean)

                lines.append(line)

        if len(lines) == 0:
            # there is nothing to read?
            return VariableSets()

        if len(lines[0]) > 1 and len(lines[0]) > 1 and lines[0][1] == "==":
            # this is a vertical file
            if line_numbers is not None:
                raise ValueError(
                    "You cannot specify line numbers for a vertical file!")
            return VariableSets._read_vertical(lines)
        else:
            return VariableSets._read_horizontal(lines=lines,
                                                 line_numbers=line_numbers)

    @staticmethod
    def _read_vertical(lines):
        """Read the data from the vertical lines"""
        variables = VariableSets()
        variable = VariableSet()

        for line in lines:
            if len(line) > 1:
                key = line[0]

                if line[1] == "==":
                    if len(line) > 3:
                        value = " ".join(line[2:])
                    else:
                        value = line[2]
                else:
                    if len(line) > 2:
                        value = " ".join(line[1:])
                    else:
                        value = line[1]

                variable[key] = _interpret(value)

        variables.append(variable)

        return variables

    @staticmethod
    def _read_horizontal(lines, line_numbers):
        """Read the data from the horizontal lines"""
        variables = VariableSets()

        # are there any strings on the first line? If so, then these
        # are the titles
        has_titles = False
        for v in lines[0]:
            try:
                float(v)
            except Exception:
                has_titles = True
                break

        if has_titles:
            titles = lines[0]
            lines = lines[1:]
        else:
            # default adjustable variables
            titles = ["beta[2]", "beta[3]", "progress[1]",
                      "progress[2]", "progress[3]"]

        if "repeats" in titles:
            repeats_index = titles.index("repeats")
            titles.pop(repeats_index)
        else:
            repeats_index = None

        repeats = []

        for i, line in enumerate(lines):
            if line_numbers is None or i in line_numbers:
                values = [_interpret(x) for x in line]

                if repeats_index is not None:
                    repeats.append(int(values.pop(repeats_index)))

                variable = VariableSet()

                for j, key in enumerate(titles):
                    variable[key] = values[j]

                variables.append(variable)

                if line_numbers is not None:
                    if len(line_numbers) == len(variables):
                        if repeats_index is not None:
                            variables = variables.repeat(repeats)

                        return variables

        # get here if we can't find this line in the file (or if we
        # are supposed to read all lines)
        if line_numbers is None:
            if repeats_index is not None:
                variables = variables.repeat(repeats)
            return variables
        else:
            raise ValueError(
                f"Cannot read parameters from line {line_numbers} "
                f"as the number of lines in the file is {i+1}")
