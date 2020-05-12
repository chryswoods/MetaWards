
from typing import List as _List
from typing import Dict as _Dict

__all__ = ["VariableSets", "VariableSet"]


def _set_beta(params, name: str, index: int, value: float):
    """Adjust the Disease.beta parameter"""
    params.disease_params.beta[index] = value


def _set_progress(params, name: str, index: int, value: float):
    """Adjust the Disease.progress parameter"""
    params.disease_params.progress[index] = value


def _set_too_ill_to_move(params, name: str, index: int, value: float):
    """Adjust the Disease.too_ill_to_move parameter"""
    params.disease_params.too_ill_to_move[index] = value


def _set_contrib_foi(params, name: str, index: int, value: float):
    """Adjust the Disease.contrib_foi parameter"""
    params.disease_params.contrib_foi[index] = value


def _set_lengthday(params, name: str, index: int, value: float):
    """Adjust the Parameters.length_day parameter"""
    if index is not None:
        raise IndexError("You cannot index the lengthday")

    params.length_day = value


def _set_plengthday(params, name: str, index: int, value: float):
    """Adjust the Parameters.plength_day parameter"""
    if index is not None:
        raise IndexError("You cannot index the lengthday")

    params.plength_day = value


def _set_uv(params, name: str, index: int, value: float):
    """Adjust the Parameters.UV parameter"""
    if index is not None:
        raise IndexError("You cannot index the UV parameter")

    params.UV = value


def _set_initial_inf(params, name: str, index: int, value: float):
    """Adjust the Parameters.initial_inf parameter"""
    if index is not None:
        raise IndexError("You cannot index the initial_inf parameter")

    params.initial_inf = value


def _set_static_play_at_home(params, name: str, index: int, value: float):
    """Adjust the Parameters.static_play_at_home parameter"""
    if index is not None:
        raise IndexError("You cannot index the static_play_at_home parameter")

    params.static_play_at_home = value


def _set_dyn_play_at_home(params, name: str, index: int, value: float):
    """Adjust the Parameters.dyn_play_at_home parameter"""
    if index is not None:
        raise IndexError("You cannot index the dyn_play_at_home parameter")

    params.dyn_play_at_home = value


def _set_data_dist_cutoff(params, name: str, index: int, value: float):
    """Adjust the Parameters.data_dist_cutoff parameter"""
    if index is not None:
        raise IndexError("You cannot index the data_dist_cutoff parameter")

    params.data_dist_cutoff = value


def _set_dyn_dist_cutoff(params, name: str, index: int, value: float):
    """Adjust the Parameters.dyn_dist_cutoff parameter"""
    if index is not None:
        raise IndexError("You cannot index the dyn_dist_cutoff parameter")

    params.dyn_dist_cutoff = value


def _set_play_to_work(params, name: str, index: int, value: float):
    """Adjust the Parameters.play_to_work parameter"""
    if index is not None:
        raise IndexError("You cannot index the play_to_work parameter")

    params.play_to_work = value


def _set_work_to_play(params, name: str, index: int, value: float):
    """Adjust the Parameters.work_to_play parameter"""
    if index is not None:
        raise IndexError("You cannot index the work_to_play parameter")

    params.work_to_play = value


def _set_local_vaccination_thresh(params, name: str, index: int, value: float):
    """Adjust the Parameters.local_vaccination_thresh parameter"""
    if index is not None:
        raise IndexError("You cannot index the local_vaccination_thresh "
                         "parameter")

    params.local_vaccination_thresh = value


def _set_global_detection_thresh(params, name: str, index: int, value: float):
    """Adjust the Parameters.global_detection_thresh parameter"""
    if index is not None:
        raise IndexError("You cannot index the global_detection_thresh "
                         "parameter")

    params.global_detection_thresh = value


def _set_daily_ward_vaccination_capacity(params, name: str,
                                         index: int, value: float):
    """Adjust the Parameters.daily_ward_vaccination_capacity
       parameter
    """
    if index is not None:
        raise IndexError("You cannot index the daily_ward_vaccination "
                         "parameter")

    params.daily_ward_vaccination_capacity = value


def _set_neighbour_weight_threshold(params, name: str,
                                    index: int, value: float):
    """Adjust the Parameters.neighbour_weight_threshold parameter"""
    if index is not None:
        raise IndexError("You cannot index the neighbour_weight_threshold "
                         "parameter")

    params.neighbour_weight_threshold = value


def _set_daily_imports(params, name: str, index: int, value: float):
    """Adjust the Parameters.daily_imports parameter"""
    if index is not None:
        raise IndexError("You cannot index the daily_imports parameter")

    params.daily_imports = value


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
        return 1.0
    elif x.lower() == "false":
        return 0.0
    elif x == "=" or x == ":":
        return "=="
    else:
        return x


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

        # look for 'variable[index]'
        m = re.search(r"([\.\w]+)\[(\d+)\]", name)

        if m:
            varname = m.group(1)
            index = int(m.group(2))
            value = float(value)
        else:
            varname = name
            index = None
            value = float(value)

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

        self._varnames.append(varname)
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
        variables = VariableSet()

        with open(filename, "r") as FILE:
            # use the first line of the file to work out the mode
            line = FILE.readline()

            # find the first line of the file. Use this to work out
            # the separator to use and also to see if the user has
            # named the adjustable variables
            first_line = None
            separator = ","

            # default adjustable variables
            titles = ["beta[2]", "beta[3]", "progress[1]",
                      "progress[2]", "progress[3]"]

            is_title_line = False
            is_vertical = False

            while line:
                line = line.strip()

                if line.startswith("#") or len(line) == 0:
                    line = FILE.readline()
                    continue

                if first_line is None:
                    # this is a valid first line - what separator
                    # should we use?
                    if line.find(",") != -1:
                        separator = ","
                    else:
                        separator = None  # spaces

                    first_line = line

                    words = [_clean(x) for x in line.split(separator)]

                    try:
                        float(words[0])
                        is_title_line = False
                        is_vertical = False
                    except Exception:
                        is_title_line = True

                    if is_title_line:
                        is_vertical = False
                        is_title_line = True

                        for i in range(1, len(words)):
                            try:
                                float(words[i])
                                is_vertical = True
                                is_title_line = False
                                titles = None
                                break
                            except Exception:
                                pass

                    if is_title_line:
                        titles = words
                        line = FILE.readline()
                        continue

                words = [_clean(x) for x in line.split(separator)]

                if is_vertical:
                    value = None

                    try:
                        value = float(words[1])
                    except Exception:
                        if words[1] == "==":
                            try:
                                value = float(words[2])
                            except Exception:
                                pass

                    if value is None:
                        raise ValueError(
                            f"Corrupted file {filename}. Expected at least "
                            f"two words for the 'variable value', but "
                            f"got {line}")

                    variables._add(words[0], value)
                    line = FILE.readline()
                    continue
                else:
                    values = []

                    try:
                        for i in range(0, len(titles)):
                            values.append(float(words[i]))
                    except Exception as e:
                        print(e)
                        pass

                    if len(values) != len(titles):
                        raise ValueError(
                            f"Corrupted file {filename}. Expected at least "
                            f"{len(titles)} words for {titles}, but got "
                            f"{line}")

                    for name, value in zip(titles, values):
                        variables._add(name, value)

                    return variables

        return variables

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
            for varname, varidx, value in zip(self._varnames, self._varidxs,
                                              self._vals):
                if varname.startswith("user.") or varname.startswith("."):
                    _adjustable["user"](params=params,
                                        name=varname,
                                        index=varidx,
                                        value=value)
                elif varname in _adjustable:
                    _adjustable[varname](params=params,
                                         name=varname,
                                         index=varidx,
                                         value=value)
                else:
                    raise KeyError(
                        f"Cannot set unrecognised parameter {varname} "
                        f"to {value}")
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
            return "{" + ", ".join(s) + "}"
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

    def repeat(self, nrepeats: int):
        """Return a copy of this VariableSet in which all of the
           unique VaribleSet objects have been repeated 'nrepeats'
           times

           Parameters
           ----------
           nrepeats: int
             The number of repeats of the VariableSet objects to
             perform

           Returns
           -------
           repeats: VariableSets
             A new VariableSets object containing 'nrepeats' copies
             of the VariableSet objects from this set
        """
        if nrepeats <= 1:
            return self

        from copy import deepcopy

        repeats = VariableSets()

        for i in range(1, nrepeats+1):
            for v in self._vars:
                v2 = deepcopy(v)
                v2._idx = i
                repeats.append(v2)

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

        variables = VariableSets()

        i = -1
        with open(filename, "r") as FILE:
            line = FILE.readline()

            # find the first line of the file. Use this to work out
            # the separator to use and also to see if the user has
            # named the adjustable variables
            first_line = None
            separator = ","

            # default adjustable variables
            titles = ["beta[2]", "beta[3]", "progress[1]",
                      "progress[2]", "progress[3]"]

            while line:
                i += 1

                line = line.strip()

                if line.startswith("#") or len(line) == 0:
                    line = FILE.readline()
                    continue

                if first_line is None:
                    # this is a valid first line - what separator
                    # should we use?
                    if line.find(",") != -1:
                        separator = ","
                    else:
                        separator = None  # spaces

                    first_line = line

                    words = line.split(separator)

                    try:
                        float(words[0])
                        is_title_line = False
                    except Exception:
                        is_title_line = True

                    if is_title_line:
                        titles = words
                        line = FILE.readline()
                        continue

                if line_numbers is None or i in line_numbers:
                    words = [_clean(x) for x in line.split(separator)]

                    if len(words) != len(titles):
                        raise ValueError(
                            f"Corrupted input file. Expecting {len(titles)} "
                            f"values. Received {line}")

                    vals = []

                    try:
                        for word in words:
                            vals.append(float(word))
                    except Exception:
                        raise ValueError(
                            f"Corrupted input file. Expected {len(titles)} "
                            f"numbers. Received {line}")

                    variables.append(VariableSet(names=titles,
                                                 values=vals))

                    if line_numbers is not None:
                        if len(variables) == len(line_numbers):
                            return variables

                line = FILE.readline()

        # get here if we can't find this line in the file (or if we
        # are supposed to read all lines)
        if line_numbers is None:
            return variables
        else:
            raise ValueError(
                f"Cannot read parameters from line {line_numbers} "
                f"as the number of lines in the file is {i+1}")
