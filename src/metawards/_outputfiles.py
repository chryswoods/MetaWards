
from pathlib import Path as _Path

__all__ = ["OutputFiles"]


def _get_bool(arg):
    """Simple function to make sure that flags that are supposed
       to be true/false are actually stored as bools
    """
    if arg:
        return True
    else:
        return False


def _is_empty(outdir):
    """Simple function that checks whether or not the passed directory
       is empty
    """
    import os

    if os.path.isfile(outdir):
        # this is a file, so it definitely is not 'empty'
        return False
    elif os.path.isdir(outdir):
        # the directory is empty if it contains no hidden files
        # or other directories - sorry to wipe out dotfiles...!
        return len(os.listdir(outdir)) == 0
    else:
        return True


def _rmdir(directory):
    """Function modified from one copied from 'mitch' on stackoverflow
       https://stackoverflow.com/questions/13118029/deleting-folders-in-python-recursively
    """
    directory = _Path(directory)

    # first, check for removing important directories such as $HOME or root
    if directory == _Path.home():
        raise FileExistsError(f"We WILL NOT remove your "
                              f"home directory ${directory}")

    if directory == _Path("/"):
        raise FileExistsError(f"We WILL NOT remove the root directory "
                              f"{directory}")

    # get the directory containing '$HOME'
    if directory == _Path.home().parent:
        raise FileExistsError(f"We WILL NOT remove the users/home "
                              f"directory {directory}")

    if not directory.is_dir():
        directory.unlink()
        return

    from .utils._console import Console

    for item in directory.iterdir():
        if item.is_dir():
            _rmdir(item)
        else:
            item.unlink()

    Console.print(f"removing directory {directory}", style="warning")
    directory.rmdir()


def _check_remove(outdir, prompt):
    """Function to check if the user wants to remove the directory,
       giving them the option to continue, quit or remove all files
    """
    if prompt is None:
        raise FileExistsError(f"Cannot continue as {outdir} already exists!")

    from .utils._console import Console
    Console.warning(f"{outdir} already exists.")
    y = prompt("Do you want to remove it? (y/n) ")

    y = y.strip().lower()

    if len(y) > 0 and y == "y":
        Console.print(f"Removing all files in {outdir}", style="warning")
        _rmdir(_Path(outdir))
        return

    Console.warning(f"Continuing with this run will mix its output with "
                    f"the files already in {outdir}.")

    y = prompt("Do you want to continue with this run? (y/n) ")

    y = y.strip().lower()

    if len(y) == 0 or y != "y":
        from .utils._console import Console
        Console.error(f"Exiting the program as we cannot run any more.")
        import sys
        sys.exit(-1)


def _force_remove(outdir, prompt):
    """Function to force the removal of a directory, using the
       passed prompt to double-check with the user. If 'prompt'
       is None, then we go ahead
    """
    import os
    if not os.path.exists(outdir):
        return

    from .utils._console import Console

    if prompt:
        Console.warning(f"{outdir} already exists")

        y = prompt("Do you want to remove it? (y/n) ")
        y = y.strip().lower()

        if len(y) == 0 or y != "y":
            raise FileExistsError(
                f"Cannot continue as {outdir} already exists")

    Console.print(f"Removing all files in {outdir}", style="red")
    _rmdir(_Path(outdir))


def _expand(path):
    """Expand all variables and user indicators in the passed path"""
    import os
    return os.path.expanduser(os.path.expandvars(path))


def _bz2compress(filename, bz2filename):
    """bz2 compress 'filename' to write 'bz2filename'"""
    if filename == bz2filename:
        raise IOError(f"Cannot be equal {filename} vs {bz2filename}")

    import bz2 as _bz2

    compressor = _bz2.BZ2Compressor()
    BLOCK_SIZE = 2048

    with open(bz2filename, "wb") as BZ2FILE:
        with open(filename, "rb") as FILE:
            while True:
                block = FILE.read(BLOCK_SIZE)

                if not block:
                    remaining = compressor.flush()
                    BZ2FILE.write(remaining)
                    return

                compressed = compressor.compress(block)
                BZ2FILE.write(compressed)


class OutputFiles:
    """This is a class that manages all of the output files that
       are written to during a model outbreak. This object is used
       to hold the 'FILE' objects for open files, and will
       ensure that these files are closed and written to disk
       as needed. It will also ensure that files are written
       to the correct output directory, and that they are only
       opened when they are needed (e.g. only the first call
       to open the file will actually open it - subsequent
       calls will return the already-open file handler)

       Examples
       --------
       >>> output = OutputFiles(output_dir="output", check_empty=True)
       >>> FILE = output.open("output.txt")
       >>> FILE.write("some output\\n")
       >>> FILE = output.open("something.csv.bz2", auto_bzip=True)
       >>> FILE.write("something,else,is,here\\n")
       >>> output.flush()
       >>> FILE = output.open("output.txt")
       >>> FILE.write("some more output\\n")
       >>> output.close()

       Note that you can also use OutputFiles in a contexthandler, to
       ensure that all output files are automatically closed, e.g.

       >>> with OutputFiles(output_dir="output") as output:
       >>>     FILE = output.open("output.txt")
       >>>     FILE.write("something\\n")
    """

    def __init__(self, output_dir: str = "output",
                 check_empty: bool = True,
                 force_empty: bool = False,
                 prompt=input,
                 auto_bzip: bool = False):
        """Construct a set of OutputFiles. These will all be written
           to 'output_dir'.

           Parameters
           ----------
           output_dir: str
             The directory in which to create all of the output files.
             This directory will be created automatically if it doesn't
             exist
           check_empty: bool
             Whether or not to check if the directory is empty before
             continuing. If the directory is not empty, then the user
             will be prompted to make a decision to either keep going,
             choose a different directory, remove existing output
             or exit
           force_empty: bool
             Force the output directory to be empty. BE CAREFUL as this
             will remove all files in that directory! There are checks
             to stop you doing something silly, but these are not
             fool-proof. The user will be prompted to confirm that
             the files should be removed
           prompt:
             This is the function that should be called to prompt the
             user for input, e.g. to confirm whether or not files
             should be deleted. This defaults to `input`. Set this
             to None if you *really* want MetaWards to remove files
             silently (e.g. useful if you are running batch jobs
             on a cluster and you really know what you are doing)
           auto_bzip: bool
             The default flag for `auto_bzip` when opening files. If
             this is true then all files will be automatically bzipped
             (compressed) as they are written, unless the code opening
             the file has explicitly asked otherwise
        """
        self._check_empty = _get_bool(check_empty)
        self._force_empty = _get_bool(force_empty)
        self._auto_bzip = _get_bool(auto_bzip)
        self._prompt = prompt
        self._output_dir = output_dir
        self._is_open = False
        self._open_files = {}
        self._filenames = {}
        self._is_database = {}

        self._open_dir()

    def __enter__(self):
        self._open_dir()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._close_dir()

    def _open_dir(self):
        """Internal function used to open the directory in which
           all output files will be placed
        """
        if self._is_open or self._output_dir is None:
            return

        import os

        if self._output_dir is None:
            raise ValueError("You cannot open an empty OutputFiles!")

        outdir = _expand(self._output_dir)

        mask = None

        if os.path.exists(outdir):
            outdir = os.path.abspath(outdir)

            if self._check_empty:
                if not _is_empty(outdir):
                    if self._force_empty:
                        _force_remove(outdir, self._prompt)
                    else:
                        _check_remove(outdir, self._prompt)

                    # remake the directory after it has been removed
                    try:
                        import sys

                        # Make sure write bit is set on Windows.
                        if sys.platform == "win32":
                            # Safely preserve the permissions of the
                            # current process
                            import stat
                            mask = os.umask(0)
                            os.makedirs(outdir, stat.S_IWRITE)
                            os.umask(mask)
                            mask = None
                        else:
                            os.makedirs(outdir)
                    except FileExistsError:
                        pass
                    finally:
                        if mask is not None:
                            os.umask(mask)
                            mask = None

            if not os.path.isdir(outdir):
                from .utils._console import Console
                Console.error(
                    f"Cannot open {outdir} as it is not a directory!")
                raise FileExistsError(f"{outdir} is an existing file!")

        try:
            import sys

            # Make sure write bit is set on Windows.
            if sys.platform == "win32":
                # Safely preserve the permissions of the current process
                import stat
                mask = os.umask(0)
                os.makedirs(outdir, stat.S_IWRITE)
                os.umask(mask)
                mask = None
            else:
                os.makedirs(outdir)

        except FileExistsError as e:
            # this is no problem, as we have already validated
            # that the directory already existing is ok
            if not os.path.isdir(outdir):
                # but it is a problem if it is not a directory...
                raise e
        finally:
            if mask is not None:
                os.umask(mask)
                mask = None

        self._output_dir = str(_Path(outdir).absolute().resolve())

        self._is_open = True

    def _close_dir(self):
        """Internal function used to close all of the output files"""
        if not self._is_open:
            return

        errors = []

        for filename, handle in self._open_files.items():
            try:
                if self._is_database.get(filename, False):
                    handle.commit()
                    handle.close()

                    if self._filenames[filename].endswith("bz2"):
                        # we need to manually compress this file
                        _bz2compress(filename, self._filenames[filename])
                        import os as _os
                        _os.remove(filename)
                else:
                    handle.close()

            except Exception as e:
                errors.append(f"Could not close {filename}: "
                              f"{e.__class__} {e}")

        self._is_open = False
        self._open_files = {}
        self._filenames = {}
        self._is_database = {}

    def is_database(self, filename):
        """Return whether or not 'filename' is an open database"""
        return self._is_database.get(filename, False)

    @staticmethod
    def remove(path, prompt=input):
        """Remove the passed filename or directory

           Parameters
           ----------
           path: str
             The path to the file or directory or remove
           prompt:
             Prompt to use to ask the user - if None then no checks!
        """
        path = _Path(_expand(path)).absolute().resolve()
        _force_remove(path, prompt)

    def is_open(self):
        """Return whether or not the output files are open"""
        return self._is_open

    def is_closed(self):
        """Return whether or not the output files are closed"""
        return not self.is_open()

    def output_dir(self):
        """Return the absolute path of the directory to which
           the output files will be written
        """
        return self._output_dir

    def open_db(self, filename: str, auto_bzip=None, initialise=None):
        """Open up a SQLite3 database connection to a file called
           'filename' in the output directory, returning the
           SQLite3 connection to the database. Note that this will
           open the database one, and will return the already-made
           connection on all subsequence calls.

           Parameters
           ----------
           filename: str
             The name of the file containing the database to open.
             This must be relative to the output directory, and within
             that directory. It is an error to try to open a database
             that is not contained in this directory.
           auto_bzip: bool
             Whether or not to automatically compress the file
             using bzip2 when it is closed. The filename will
             automatically have '.bz2' appended so that this
             is clear. If 'None' is passed (the default) then
             the value of 'auto_bzip' that was passed to the
             constructor of this OutputFiles will be used. Note that
             this flag is ignored if the database is already open
          initialise: function
             A function that is called to initialise the database the
             first time that it is opened. The function is called
             with the argument "CONN" (representing the sqlite3 database
             connection). Use this to create the tables that you need
        """
        import os

        self._open_dir()

        outdir = self._output_dir
        p = _Path(_expand(filename))

        if not p.is_absolute():
            p = _Path(os.path.join(outdir, filename))

        filename = str(p.absolute().resolve())

        prefix = os.path.commonprefix([outdir, filename])
        if prefix != outdir:
            raise ValueError(f"You cannot try to open {filename} as "
                             f"this is not in the output directory "
                             f"{outdir} - common prefix is {prefix}")

        if filename in self._open_files:
            if self._is_database.get(filename, False):
                return self._open_files[filename]
            else:
                raise IOError(f"{filename} is a file, not a database!")

        if auto_bzip is None:
            auto_bzip = self._auto_bzip

        auto_bzip = _get_bool(auto_bzip)

        if auto_bzip is None:
            auto_bzip = self._auto_bzip

        auto_bzip = _get_bool(auto_bzip)

        import sqlite3 as _sqlite3

        CONN = _sqlite3.connect(filename)

        if initialise is not None:
            initialise(CONN)

        self._open_files[filename] = CONN
        self._is_database[filename] = True

        if auto_bzip:
            if not filename.endswith(".bz2"):
                suffix = ".bz2"
            else:
                suffix = ""

            self._filenames[filename] = f"{filename}{suffix}"
        else:
            self._filenames[filename] = filename

        return CONN

    def open(self, filename: str, auto_bzip=None, mode="t",
             headers=None, sep=" "):
        """Open the file called 'filename' in the output directory,
           returning a handle to that file. Note that this will
           open the file once, and will return the already-open
           file handle on all subsequent calls.

           Parameters
           ----------
           filename: str
             The name of the file to open. This must be relative
             to the output directory, and within that directory.
             It is an error to try to open a file that is
             not contained within this directory.
           auto_bzip: bool
             Whether or not to open the file in auto-bzip (compression)
             mode. If this is True then the file will be automatically
             compressed as it is written. The filename will have
             '.bz2' automatically appended so that this is clear.
             If this is False then the file will be written uncompressed.
             If 'None' is passed (the default) then the value of
             `auto_bzip` that was passed to the constructor of
             this OutputFiles will be used. Note that this flag is
             ignored if the file is already open.
           mode: str
             The mode of opening the file, e.g. 't' for text mode, and
             'b' for binary mode. The default is text mode
           headers: list[str] or plain str or function
             The headers to add to the top of the file, e.g. if it will
             contain column data. This will be written to the first line
             when the file is opened. If a list is passed, then this
             will be written joined together using 'sep'. If a plain
             string is passed then this will be written. If this is a function
             then this function will be called with "FILE" as the argument.
             If nothing is passed then no headers will be written.
           sep: str
             The separator used for the headers (e.g. " " or "," are good
             choices). By default things are space-separated

           Returns
           -------
           file
             The handle to the open file
        """
        import os

        self._open_dir()

        outdir = self._output_dir
        p = _Path(_expand(filename))

        if not p.is_absolute():
            p = _Path(os.path.join(outdir, filename))

        filename = str(p.absolute().resolve())

        prefix = os.path.commonprefix([outdir, filename])
        if prefix != outdir:
            raise ValueError(f"You cannot try to open {filename} as "
                             f"this is not in the output directory "
                             f"{outdir} - common prefix is {prefix}")

        if filename in self._open_files:
            if self._is_database.get(filename, False):
                raise IOError(f"{filename} is a database, not a file!")
            else:
                return self._open_files[filename]

        if auto_bzip is None:
            auto_bzip = self._auto_bzip

        auto_bzip = _get_bool(auto_bzip)

        if mode is None:
            mode = "w"
        elif mode.find("w") == -1:
            mode = f"w{mode}"

        if mode.find("b") == -1:
            # text file = encoding should be "UTF-8"
            encoding = "UTF-8"
        else:
            encoding = None

        if auto_bzip:
            import bz2
            if not filename.endswith(".bz2"):
                suffix = ".bz2"
            else:
                suffix = ""

            if encoding:
                FILE = bz2.open(f"{filename}{suffix}", mode=mode,
                                encoding=encoding)
            else:
                FILE = bz2.open(f"{filename}{suffix}", mode=mode)

            self._open_files[filename] = FILE
            self._filenames[filename] = f"{filename}{suffix}"
        else:
            if encoding:
                FILE = open(filename, mode=mode, encoding=encoding)
            else:
                FILE = open(filename, mode=mode)

            self._open_files[filename] = FILE
            self._filenames[filename] = filename

        if headers is not None:
            if isinstance(headers, str):
                FILE.write(headers)
                FILE.write("\n")
            elif hasattr(headers, "__call__"):
                headers(FILE)
            else:
                FILE.write(sep.join([str(x) for x in headers]))
                FILE.write("\n")

        return FILE

    def open_subdir(self, dirname):
        """Create and open a sub-directory in this OutputFiles
           called 'dirname'. This will inherit all properties,
           e.g. check_empty, auto_bzip etc from this OutputFiles

           Parameters
           ----------
           dirname: str
             The name of the subdirectory to open

           Returns
           -------
           subdir: OutputFiles
             The open subdirectory
        """
        import os

        self._open_dir()

        outdir = self._output_dir
        p = _Path(_expand(dirname))

        if not p.is_absolute():
            p = _Path(os.path.join(outdir, dirname))

        subdir = str(p.absolute().resolve())

        prefix = os.path.commonprefix([outdir, subdir])
        if prefix != outdir:
            raise ValueError(f"You cannot try to open {dirname} as "
                             f"this is not in the output directory "
                             f"{outdir} - common prefix is {prefix}")

        return OutputFiles(output_dir=subdir, check_empty=self._check_empty,
                           force_empty=self._force_empty, prompt=self._prompt,
                           auto_bzip=self._auto_bzip)

    def auto_bzip(self):
        """Return whether the default is to automatically bzip2 files"""
        return self._auto_bzip

    def get_path(self):
        """Return the full expanded path to this directory"""
        return self._output_dir

    def get_filename(self, filename):
        """Return the full expanded filename for 'filename'"""
        import os

        self._open_dir()

        outdir = self._output_dir
        p = _Path(_expand(filename))

        if not p.is_absolute():
            p = _Path(os.path.join(outdir, filename))

        filename = str(p.absolute().resolve())

        if filename in self._filenames:
            return self._filenames[filename]
        else:
            raise FileNotFoundError(f"No open file {filename}")

    def close(self):
        """Close all of the files and this directory"""
        self._close_dir()

    def flush(self):
        """Flush the contents of all files to disk"""
        for filename, handle in self._open_files.items():
            try:
                handle.flush()
            except Exception:
                pass
