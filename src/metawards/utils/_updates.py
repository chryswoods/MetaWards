
__all__ = ["check_for_updates", "update_metawards"]


def _run_command(cmd, dry=False, capture_output=False, silent=False):
    """Run the passed shell command"""
    if dry:
        print(f"[DRY-RUN] {cmd}")
        return 0

    lines = []

    try:
        import shlex
        import subprocess
        import sys

        args = shlex.split(cmd)
        with subprocess.Popen(args, stdin=sys.stdin,
                              stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE, bufsize=1,
                              universal_newlines=True) as PROC:
            while True:
                line = PROC.stdout.readline()
                if not line:
                    break

                if capture_output:
                    lines.append(line)

                if not silent:
                    sys.stdout.write(line)
                    sys.stdout.flush()

            return_val = PROC.poll()

            if capture_output:
                return lines
            else:
                return return_val

    except Exception as e:
        print(f"[ERROR] {e}")
        return -1


def check_for_updates(dry_run: bool = False):
    """Check if a newer version of MetaWards is available. If there is,
       then return the version number string. If not, then return None.

       If 'dry_run' is True, then this will just print the commands
       to the screen that will be used to query the version info
    """
    import sys

    try:
        import pip
        have_pip = True
    except ImportError:
        have_pip = False
    except Exception:
        have_pip = True

    if not have_pip:
        raise SystemError(
            "Pip is not available so we cannot discover if newer versions "
            "of MetaWards are available")

    cmd = f"{sys.executable} -m pip search metawards"
    output = _run_command(cmd, dry=dry_run, silent=True, capture_output=True)

    if dry_run:
        return None

    installed = None
    latest = None

    for line in output:
        if line.find("INSTALLED") != -1:
            installed = line.strip().split()[-1]
        elif line.find("LATEST") != -1:
            latest = line.strip().split()[-1]

    if latest is None:
        return None

    installed = installed.split("+")[0]

    if installed != latest:
        return latest
    else:
        return None


def update_metawards(dry_run: bool = False, user: bool = False):
    """Update MetaWards to the latest version. If dry_run is True
       then only print the commands that will be called. If
       user is True then install within the user space
    """
    import sys

    try:
        import pip
        have_pip = True
    except ImportError:
        have_pip = False
    except Exception:
        have_pip = True

    if not have_pip:
        raise SystemError(
            "Pip is not available so we cannot update to newer versions "
            "of MetaWards")

    if user:
        user = "--user"
    else:
        user = ""

    cmd = f"{sys.executable} -m pip install {user} metawards --upgrade"
    try:
        output = _run_command(cmd, dry=dry_run,
                              silent=True, capture_output=True)
    except Exception:
        from ._console import Console
        Console.error(f"Cannot update MetaWards. Do you have permission to "
                      f"update this software? Output from updating is "
                      f"written below:\n" + "".join(output))

    for line in output:
        if line.startswith("Successfully installed"):
            print(line, end="")
            return True

    return None
