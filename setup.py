# Package setup copied from
# https://github.com/FedericoStra/cython-package-example
# Thanks - this was really helpful :-)

import os
import versioneer
from setuptools import setup, Extension

try:
    from Cython.Build import cythonize
    have_cython = True
except Exception:
    have_cython = False

cflags = '-O3 -march=native -Wall -fopenmp'

nbuilders = int(os.getenv("CYTHON_NBUILDERS", 2))

compiler_directives = {"language_level": 3, "embedsignature": True,
                       "boundscheck": False, "cdivision": True,
                       "initializedcheck": False, "cdivision_warnings": False,
                       "wraparound": False, "binding": False,
                       "nonecheck": False, "overflowcheck": False}

if os.getenv("CYTHON_LINETRACE", 0):
    print("Compiling with Cython line-tracing support - will be SLOW")
    define_macros = [("CYTHON_TRACE", "1")]
    compiler_directives["linetrace"] = True
else:
    define_macros = []

random_sources = ["src/metawards/ran_binomial/mt19937.c",
                  "src/metawards/ran_binomial/distributions.c"]


# https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#distributing-cython-modules
def no_cythonize(extensions, **_ignore):
    for extension in extensions:
        sources = []
        for sfile in extension.sources:
            path, ext = os.path.splitext(sfile)
            if ext in (".pyx", ".py"):
                if extension.language == "c++":
                    ext = ".cpp"
                else:
                    ext = ".c"
                sfile = path + ext
            sources.append(sfile)
        extension.sources[:] = sources
    return extensions

# Currently each file compiles to its own module. Ideally I'd like
# them all to compile into a single module library, but this doesn't
# work (get the error "ImportError: dynamic module does not define
# init function" and the answers on stackoverflow didn't work.
# If anyone can help please do :-)


extensions = [
    Extension("metawards._nodes", ["src/metawards/_nodes.pyx"],
              define_macros=define_macros),
    Extension("metawards._links", ["src/metawards/_links.pyx"],
              define_macros=define_macros),
    Extension("metawards.utils._workspace",
              ["src/metawards/utils/_workspace.pyx"],
              define_macros=define_macros),
    Extension("metawards.utils._clear_all_infections",
              ["src/metawards/utils/_clear_all_infections.pyx"],
              define_macros=define_macros),
    Extension("metawards.utils._build_wards_network",
              ["src/metawards/utils/_build_wards_network.pyx"],
              define_macros=define_macros),
    Extension("metawards.utils._add_wards_network_distance",
              ["src/metawards/utils/_add_wards_network_distance.pyx"],
              define_macros=define_macros),
    Extension("metawards.utils._get_min_max_distances",
              ["src/metawards/utils/_get_min_max_distances.pyx"],
              define_macros=define_macros),
    Extension("metawards.utils._reset_everything",
              ["src/metawards/utils/_reset_everything.pyx"],
              define_macros=define_macros),
    Extension("metawards.utils._rescale_matrix",
              ["src/metawards/utils/_rescale_matrix.pyx"],
              define_macros=define_macros),
    Extension("metawards.utils._recalculate_denominators",
              ["src/metawards/utils/_recalculate_denominators.pyx"],
              define_macros=define_macros),
    Extension("metawards.utils._move_population",
              ["src/metawards/utils/_move_population.pyx"],
              define_macros=define_macros),
    Extension("metawards.utils._fill_in_gaps",
              ["src/metawards/utils/_fill_in_gaps.pyx"],
              define_macros=define_macros),
    Extension("metawards.utils._build_play_matrix",
              ["src/metawards/utils/_build_play_matrix.pyx"],
              define_macros=define_macros),
    Extension("metawards.utils._array", ["src/metawards/utils/_array.pyx"],
              define_macros=define_macros),
    Extension("metawards.utils._ran_binomial",
              ["src/metawards/utils/_ran_binomial.pyx"]+random_sources,
              define_macros=define_macros),
    Extension("metawards.utils._assert_sane_network",
              ["src/metawards/utils/_assert_sane_network.pyx"],
              define_macros=define_macros),
    Extension("metawards.utils._get_array_ptr",
              ["src/metawards/utils/_get_array_ptr.pyx"],
              define_macros=define_macros),
    Extension("metawards.iterators._advance_play",
              ["src/metawards/iterators/_advance_play.pyx"]+random_sources,
              define_macros=define_macros),
    Extension("metawards.iterators._advance_fixed",
              ["src/metawards/iterators/_advance_fixed.pyx"]+random_sources,
              define_macros=define_macros),
    Extension("metawards.iterators._advance_infprob",
              ["src/metawards/iterators/_advance_infprob.pyx"]+random_sources,
              define_macros=define_macros),
    Extension("metawards.iterators._advance_recovery",
              ["src/metawards/iterators/_advance_recovery.pyx"]+random_sources,
              define_macros=define_macros),
    Extension("metawards.iterators._advance_foi",
              ["src/metawards/iterators/_advance_foi.pyx"]+random_sources,
              define_macros=define_macros),
    Extension("metawards.iterators._advance_imports",
              ["src/metawards/iterators/_advance_imports.pyx"]+random_sources,
              define_macros=define_macros),
    Extension("metawards.extractors._output_core",
              ["src/metawards/extractors/_output_core.pyx"],
              define_macros=define_macros),
    Extension("metawards.extractors._output_dispersal",
              ["src/metawards/extractors/_output_dispersal.pyx"],
              define_macros=define_macros),
]

CYTHONIZE = bool(int(os.getenv("CYTHONIZE", 0)))

if not have_cython:
    CYTHONIZE = False

os.environ['CFLAGS'] = cflags

if CYTHONIZE:
    extensions = cythonize(extensions, compiler_directives=compiler_directives,
                           nthreads=nbuilders)
else:
    extensions = no_cythonize(extensions)

with open("requirements.txt") as fp:
    install_requires = fp.read().strip().split("\n")

with open("requirements-dev.txt") as fp:
    dev_requires = fp.read().strip().split("\n")

setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    ext_modules=extensions,
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
        "docs": ["sphinx", "sphinx-rtd-theme"]
    },
    entry_points={
        "console_scripts": [
           "metawards = metawards.app.run:cli",
           "metawards-plot = metawards.app.plot:cli"
        ]
    }
)
