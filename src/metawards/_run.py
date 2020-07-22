from __future__ import annotations

from typing import Union as _Union
from typing import List as _List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._disease import Disease
    from ._demographics import Demographics
    from ._demographic import Demographic
    from ._parameters import Parameters
    from ._wards import Wards
    from ._ward import Ward
    from ._variableset import VariableSet, VariableSets

    from datetime import date


__all__ = ["run"]


def _write_to_file(obj: any, filename: str, dir: str = ".", bzip: bool = False,
                   dry_run: bool = False) -> str:
    """Write the passed object to a file called 'filename' in
       directory 'dir', returning the
       relative path to that file
    """
    import os

    if dry_run:
        return filename

    filename = os.path.join(dir, filename)

    if hasattr(obj, "to_json"):
        return obj.to_json(filename, auto_bzip=bzip)
    else:
        raise IOError(f"Cannot convert {obj} to a file!")

    return filename


def _rmdir(directory):
    """Function modified from one copied from 'mitch' on stackoverflow
       https://stackoverflow.com/questions/13118029/deleting-folders-in-python-recursively
    """
    if directory is None:
        return

    from pathlib import Path
    directory = Path(directory)

    # first, check for removing important directories such as $HOME or root
    if directory == Path.home():
        raise FileExistsError(f"We WILL NOT remove your "
                              f"home directory ${directory}")

    if directory == Path("/"):
        raise FileExistsError(f"We WILL NOT remove the root directory "
                              f"{directory}")

    # get the directory containing '$HOME'
    if directory == Path.home().parent:
        raise FileExistsError(f"We WILL NOT remove the users/home "
                              f"directory {directory}")

    if not directory.is_dir():
        directory.unlink()
        return

    for item in directory.iterdir():
        if item.is_dir():
            _rmdir(item)
        else:
            item.unlink()

    directory.rmdir()


def run(help: bool = None,
        version: bool = None,
        dry_run: bool = None,
        silent: bool = False,
        auto_load: bool = False,
        config: str = None,
        input: _Union[str, VariableSet, VariableSets] = None,
        line: int = None,
        repeats: int = None,
        seed: int = None,
        additional: _Union[str, _List[str]] = None,
        output: str = None,
        disease: _Union[str, Disease] = None,
        model: _Union[str, Wards, Ward] = None,
        demographics: _Union[str, Demographics, Demographic] = None,
        start_date: _Union[str, date] = None,
        start_day: int = None,
        parameters: _Union[str, Parameters] = None,
        repository: str = None,
        population: int = None,
        nsteps: int = None,
        user_variables: _Union[str, VariableSet] = None,
        iterator: str = None,
        extractor: str = None,
        mixer: str = None,
        mover: str = None,
        star_as_E: bool = None,
        star_as_R: bool = None,
        disable_star: bool = None,
        UV: float = None,
        debug: bool = None,
        debug_level: int = None,
        outdir_scheme: str = None,
        nthreads: int = None,
        nprocs: int = None,
        hostfile: str = None,
        cores_per_node: int = None,
        auto_bzip: bool = None,
        no_auto_bzip: bool = None,
        force_overwrite_output: bool = None,
        profile: bool = None,
        no_profile: bool = None,
        mpi: bool = None,
        scoop: bool = None) -> _Union[str, 'pandas.DataFrame']:
    """Run a MetaWards simulation

       Parameters
       ----------
       silent: bool
         Run without printing the output to the screen
       dry_run: bool
         Don't run anything - just print what will be run
       help: bool
         Whether or not to print the full help
       version: bool
         Whether or not to print the metawards version info
       output: str
         The name of the directory in which to write the output. If this
         is not set, then a new, random-named directory will be used.
       force_overwrite_output: bool
         Force overwriting the output directory - this will remove any
         existing directory before running
       auto_load: bool
         Whether or not to automatically load and return a pandas dataframe
         of the output/results.csv.bz2 file. If pandas is available then
         this defaults to True, otherwise False
       disease: Disease or str
         The disease to model (or the filename of the json file containing
         the disease, or name of the disease)
       model: Ward, Wards or str
         The network wards to run (of the filename of the json file
         containing the network, or name of the network))

       There are many more parameters, based on the arguments to
       metawards --help.

       Please set "help" to True to print out a full list of
       help for all of the arguments

        Returns
        -------
        results: str or pandas.DataFrame
          The file containing the output results (output/results.csv.bz2),
          or, if auto_load is True, the pandas.DataFrame containing
          those results
    """
    import sys
    import os
    import tempfile
    from .utils._console import Console

    metawards = os.path.join(os.path.dirname(sys.executable), "metawards")

    if not os.path.exists(metawards):
        Console.error(f"Cannot find the metawards executable: {metawards}")
        return -1

    args = []

    tmpdir = None

    theme = "simple"
    no_progress = True
    no_spinner = True

    if help:
        args.append("--help")
    elif version:
        args.append("--version")
    else:
        if output is None and not dry_run:
            output = tempfile.mkdtemp(prefix="output_", dir=".")
            force_overwrite_output = True

        if force_overwrite_output:
            args.append("--force-overwrite-output")
        else:
            if output is None:
                output = "output"

            while os.path.exists(output):
                import metawards as _metawards
                print(f"Output directory {output} exists.")
                output = _metawards.input("Please choose a new directory: ",
                                          default="error")

                if output is None:
                    return 0

                output = output.strip()
                if len(output) == 0:
                    return 0

                if output.lower() == "error":
                    Console.error("You need to delete the directory or set "
                                  "'force_overwrite_output' to TRUE")
                    return -1

        try:
            if config is not None:
                args.append(f"--config {config}")

            if input is not None:
                if not isinstance(input, str):
                    if tmpdir is None:
                        tmpdir = tempfile.mkdtemp(prefix="input_", dir=".")

                    input = _write_to_file(input, "input.dat", dir=tmpdir,
                                           bzip=False, dry_run=dry_run)

                args.append(f"--input {input}")

            if line is not None:
                args.append(f"--line {int(line)}")

            if repeats is not None:
                args.append(f"--repeats {int(repeats)}")

            if seed is not None:
                args.append(f"--seed {int(seed)}")

            if additional is not None:
                if isinstance(additional, list):
                    additional = "\\n".join(additional)
                elif not isinstance(additional, str):
                    additional = str(int(additional))

                if "'" in additional:
                    args.append(f"--additional \"{additional}\"")
                else:
                    args.append(f"--additional '{additional}'")

            if output is not None:
                args.append(f"--output {output}")

            if disease is not None:
                if not isinstance(disease, str):
                    if tmpdir is None:
                        tmpdir = tempfile.mkdtemp(prefix="input_", dir=".")

                    disease = _write_to_file(disease, "disease.json",
                                             dir=tmpdir,
                                             bzip=False, dry_run=dry_run)

                args.append(f"--disease {disease}")

            if model is not None:
                from ._ward import Ward
                from ._wards import Wards

                if isinstance(model, Ward):
                    m = Wards()
                    m.add(model)
                    model = m

                if not isinstance(model, str):
                    if tmpdir is None:
                        tmpdir = tempfile.mkdtemp(prefix="input_", dir=".")

                    model = _write_to_file(model, "model.json", dir=tmpdir,
                                           bzip=True, dry_run=dry_run)

                args.append(f"--model {model}")

            if demographics is not None:
                from ._demographic import Demographic
                from ._demographics import Demographics

                if isinstance(demographics, Demographic):
                    d = Demographics()
                    d.add(demographics)
                    demographics = demographics

                if not isinstance(demographics, str):
                    if tmpdir is None:
                        tmpdir = tempfile.mkdtemp(prefix="input_", dir=".")

                    demographics = _write_to_file(demographics,
                                                  "demographics.json",
                                                  dir=tmpdir,
                                                  bzip=False,
                                                  dry_run=dry_run)

                args.append(f"--demographics {demographics}")

            if start_date is not None:
                from datetime import date
                if isinstance(start_date, date):
                    start_date = date.isoformat()

                args.append(f"--start-date {start_date}")

            if start_day is not None:
                args.append(f"--start-day {int(start_day)}")

            if parameters is not None:
                if not isinstance(parameters, str):
                    if tmpdir is None:
                        tmpdir = tempfile.mkdtemp(prefix="input_", dir=".")

                    parameters = _write_to_file(parameters, "parameters.dat",
                                                dir=tmpdir, bzip=False,
                                                dry_run=dry_run)

                args.append(f"--parameters {parameters}")

            if repository is not None:
                args.append(f"--repository {repository}")

            if population is not None:
                args.append(f"--population {int(population)}")

            if nsteps is not None:
                args.append(f"--nsteps {int(nsteps)}")

            if user_variables is not None:
                if not isinstance(user_variables, str):
                    if tmpdir is None:
                        tmpdir = tempfile.mkdtemp(prefix="input_", dir=".")

                    user_variables = _write_to_file(user_variables,
                                                    "user_variables.dat",
                                                    dir=tmpdir,
                                                    bzip=False,
                                                    dry_run=dry_run)

                args.append(f"--user {user_variables}")

            if iterator is not None:
                args.append(f"--iterator {iterator}")

            if extractor is not None:
                args.append(f"--extractor {extractor}")

            if mixer is not None:
                args.append(f"--mixer {mixer}")

            if mover is not None:
                args.append(f"--mover {mover}")

            if star_as_E:
                args.append("--star-as-E")
            elif star_as_R:
                args.append("--star-as-R")
            elif disable_star:
                args.append("--disable-star")

            if UV is not None:
                args.append(f"--UV {UV}")

            if theme is not None:
                args.append(f"--theme {theme}")

            if no_spinner:
                args.append("--no-spinner")

            if no_progress:
                args.append("--no-progress")

            if debug:
                args.append("--debug")

                if debug_level is not None:
                    args.append(f"--debug-level {debug_level}")

            if outdir_scheme is not None:
                args.append(f"--outdir-scheme {outdir_scheme}")

            if nthreads is not None:
                args.append(f"--nthreads {int(nthreads)}")

            if nprocs is not None:
                args.append(f"--nprocs {int(nprocs)}")

            if hostfile is not None:
                args.append(f"--hostfile {hostfile}")

            if cores_per_node is not None:
                args.append(f"--cores-per-node {int(cores_per_node)}")

            if auto_bzip:
                args.append("--auto-bzip")
            elif no_auto_bzip:
                args.append("--no-auto-bzip")

            if profile:
                args.append("--profile")
            elif no_profile:
                args.append("--no-profile")

            if mpi:
                args.append("--mpi")

            if scoop:
                args.append("--scoop")

        except Exception as e:
            Console.error(f"[ERROR] Error interpreting the arguments"
                          f"[ERROR] {e.__class__}: {e}")
            _rmdir(tmpdir)
            raise
            return -1

    cmd = f"{metawards} {' '.join(args)}"

    if dry_run:
        Console.info(f"[DRY-RUN] {cmd}")
        return_val = 0
    else:
        Console.info(f"Writing output to directory {output}")

        try:
            import shlex
            import subprocess
            args = shlex.split(cmd)
            with subprocess.Popen(args, stdin=sys.stdin,
                                  stderr=subprocess.PIPE,
                                  stdout=subprocess.PIPE, bufsize=1,
                                  universal_newlines=True) as PROC:
                while True:
                    line = PROC.stdout.readline()
                    if not line:
                        break

                    if not silent:
                        sys.stdout.write(line)
                        sys.stdout.flush()

                return_val = PROC.poll()
        except Exception as e:
            Console.error(f"[ERROR] {e.__class__}: {e}")
            return_val = -1

    _rmdir(tmpdir)

    if dry_run:
        return

    if return_val == 0:
        results = os.path.join(output, "results.csv")

        if not os.path.exists(results):
            results += ".bz2"

        if auto_load:
            try:
                import pandas
            except ImportError:
                Console.error("Cannot import pandas:\n{e}")
                auto_load = False

        if auto_load is None:
            try:
                import pandas
                auto_load = True
            except ImportError as e:
                auto_load = False

        if auto_load:
            import pandas as pd
            return pd.read_csv(results)
        else:
            return results
    else:
        Console.error(f"Something went wrong with the run. Please look "
                      f"at {output}/console.log.bz2 for more information")
        return None
