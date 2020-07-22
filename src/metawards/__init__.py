"""
.. currentmodule:: metawards

Classes
=======

.. autosummary::
    :toctree: generated/

    Demographic
    Demographics
    Disease
    Infections
    InputFiles
    Interpret
    Link
    Links
    Network
    Networks
    Node
    Nodes
    OutputFiles
    Parameters
    Population
    Populations
    VariableSet
    VariableSets
    Ward
    WardInfo
    WardInfos
    Wards
    Workspace

Functions
=========

.. autosummary::
    :toctree: generated/

    get_version_string
    print_version_string
    input
    run

"""

import sys as _sys
import os as _os

from ._version import get_versions

__all__ = ["get_version_string", "print_version_string", "input",
           "Demographic", "Demographics", "Disease", "Infections",
           "InputFiles", "Interpret", "Link", "Links", "Network",
           "Networks", "Node", "Nodes", "OutputFiles", "Parameters",
           "Population", "Populations", "VariableSet", "VariableSets",
           "Ward", "WardInfo", "WardInfos", "Wards", "Workspace"]

# make sure that the directory containing this __init__.py is
# early in the path - this will ensure that this versions modules
# will be imported rather than globally installed modules. This is
# needed so that lazily imported modules will come from this directory,
# rather than any other installed version of metawards
_install_path = _os.path.dirname(__file__)
_sys.path.insert(0, _install_path)

_disable_lazy_import = True

try:
    if _disable_lazy_import:
        raise AssertionError()

    import lazy_import as _lazy_import
    _lazy_import.logging.disable(_lazy_import.logging.DEBUG)
except Exception:
    class _lazy_import:
        """This is not lazy_import, but instead a thin stub that matches the
           API but DOES NOT lazy_import anything. This imports at call time.
        """
        @staticmethod
        def lazy_module(m):
            from importlib import import_module
            return import_module(m, package="metawards")

        @staticmethod
        def lazy_function(f):
            module_name, unit_name = f.rsplit('.', 1)
            module = _lazy_import.lazy_module(module_name)
            return getattr(module, unit_name)

        @staticmethod
        def lazy_class(c):
            return _lazy_import.lazy_function(c)

analysis = _lazy_import.lazy_module(".analysis")
app = _lazy_import.lazy_module(".app")
movers = _lazy_import.lazy_module(".movers")
mixers = _lazy_import.lazy_module(".mixers")
extractors = _lazy_import.lazy_module(".extractors")
iterators = _lazy_import.lazy_module(".iterators")
utils = _lazy_import.lazy_module(".utils")

Demographic = _lazy_import.lazy_class("._demographic.Demographic")
Demographics = _lazy_import.lazy_class("._demographics.Demographics")
Disease = _lazy_import.lazy_class("._disease.Disease")
Infections = _lazy_import.lazy_class("._infections.Infections")
InputFiles = _lazy_import.lazy_class("._inputfiles.InputFiles")
Interpret = _lazy_import.lazy_class("._interpret.Interpret")
Link = _lazy_import.lazy_class("._link.Link")
Links = _lazy_import.lazy_class("._links.Links")
Network = _lazy_import.lazy_class("._network.Network")
Networks = _lazy_import.lazy_class("._networks.Networks")
Node = _lazy_import.lazy_class("._node.Node")
Nodes = _lazy_import.lazy_class("._nodes.Nodes")
OutputFiles = _lazy_import.lazy_class("._outputfiles.OutputFiles")
Parameters = _lazy_import.lazy_class("._parameters.Parameters")
Population = _lazy_import.lazy_class("._population.Population")
Populations = _lazy_import.lazy_class("._population.Populations")
VariableSet = _lazy_import.lazy_class("._variableset.VariableSet")
VariableSets = _lazy_import.lazy_class("._variableset.VariableSets")
Ward = _lazy_import.lazy_class("._ward.Ward")
WardInfo = _lazy_import.lazy_class("._wardinfo.WardInfo")
WardInfos = _lazy_import.lazy_class("._wardinfo.WardInfos")
Wards = _lazy_import.lazy_class("._wards.Wards")
Workspace = _lazy_import.lazy_class("._workspace.Workspace")

run = _lazy_import.lazy_class("._run.run")

if _sys.version_info < (3, 7):
    print("MetaWards requires Python version 3.7 or above.")
    print("Your python is version")
    print(_sys.version)
    _sys.exit(-1)

# import the pyx cython-compiled modules

__manual_version__ = "1.2.0"

_v = get_versions()
__version__ = _v['version']

if __version__.find("untagged") != -1:
    __version__ = __manual_version__

__branch__ = _v['branch']
__repository__ = _v['repository']
__revisionid__ = _v['full-revisionid']
del _v
del get_versions


def _url(url):
    """Simple function to include URLs on OS's that support them in
       console output
    """
    import sys
    if sys.platform == "win32":
        return url
    else:
        return f"[{url}]({url})"


def get_version_string():
    """Return a version string for metawards which can be printed
       into a file or written out to the screen
    """
    from ._parameters import get_repository
    repository, v = get_repository(error_on_missing=False)

    if repository is None:
        repo_info = f"""
***WARNING: MetaWardsData cannot be found!
Please see {_url('https://metawards.org/model_data')}
for instructions on how to download and install this necessary data.***
"""
    else:
        if v["is_dirty"]:
            dirty = """
***WARNING: This data has not been committed to git.
You may not be able to reproduce this run.***
"""
        else:
            dirty = ""

        repo_info = f"""
# MetaWardsData information
* version: {v['version']}
* repository: {_url(v['repository'])}
* branch: {v['branch']}
{dirty}
"""

    from ._version import get_versions
    v = get_versions()

    if v['version'].find("untagged") != -1:
        # the version couldn't be found - this is likely because this
        # is run as part of github actions or in a disconnected repo.
        # We need to drop back to '__manual_version__'
        v['version'] = __manual_version__

    if v["dirty"]:
        dirty = """
**WARNING: This version has not been committed to git,
so you may not be able to recover the original
source code that was used to generate this run!**
"""
    else:
        dirty = ""

    return f"""
# MetaWards version {v['version']}
# {_url('https://metawards.org')}

# Source information

* repository: {_url(v['repository'])}
* branch: {v['branch']}
* revision: {v['full-revisionid']}
* last modified: {v['date']}
{dirty}
{repo_info}

# Additional information
Visit {_url('https://metawards.org')} for more information
about metawards, its authors and its license
"""


def print_version_string():
    from metawards.utils import Console
    Console.panel(get_version_string(), markdown=True,
                  style="header", width=72, expand=False)


_system_input = input


def input(prompt: str, default="y"):
    """Wrapper for 'input' that returns 'default' if it detected
       that this is being run from within a batch job or other
       service that doesn't have access to a tty
    """
    import sys

    try:
        if sys.stdin.isatty():
            return _system_input(prompt)
        else:
            print(f"Not connected to a console, so having to use the "
                  f"default ({default})")
            return default
    except Exception as e:
        print(f"Unable to get the input: {e.__class__} {e}")
        print(f"Using the default ({default}) instead")
        return default
