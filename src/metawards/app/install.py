
def parse_args():
    """Parse all of the command line arguments"""
    import configargparse
    import sys

    configargparse.init_argument_parser(
        name="main",
        description="MetaWards optional package installation tool. See "
        "https://metawards.org for more information.",
        prog="metawards-install")

    parser = configargparse.get_argument_parser("main")

    parser.add_argument('--version', action="store_true",
                        default=None,
                        help="Print the version information about "
                             "metawards-plot")

    parser.add_argument('--install-optional', action="store_true",
                        default=None,
                        help="Install all of the optional MetaWards "
                             "dependencies")

    parser.add_argument("--conda", action="store_true",
                        default=None,
                        help="Install dependencies using 'conda'")

    parser.add_argument("--pip", action="store_true",
                        default=None,
                        help="Install dependencies using 'pip'")

    parser.add_argument("--dry-run", action="store_true",
                        default=None,
                        help="Just print out what will be done - don't "
                             "actually do anything")

    parser.add_argument("--list", action="store_true",
                        default=None,
                        help="Print out of the optional dependencies.")

    parser.add_argument("--user", action="store_true",
                        default=None,
                        help="Install using '--user' rather than globally.")

    args = parser.parse_args()

    if args.version:
        from metawards import get_version_string
        print(get_version_string())
        sys.exit(0)

    return (args, parser)


def run_command(cmd, dry=False):
    """Run the passed shell command"""
    if dry:
        print(f"[DRY-RUN] {cmd}")
        return 0

    print(f"[EXECUTE] {cmd}")

    try:
        import shlex
        import subprocess
        args = shlex.split(cmd)
        subprocess.run(args).check_returncode()
        return 0
    except Exception as e:
        print(f"[INSTALL ERROR] {e}")
        return -1


def check_gifsicle():
    import subprocess
    try:
        subprocess.run(["gifsicle", "--version"],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL).check_returncode()
        have_gifsicle = True
    except Exception as e:
        print(e)
        have_gifsicle = False

    if not have_gifsicle:
        print("Cannot find 'gifsicle'.\n"
              "Please consider installing it using the instructions at\n"
              "https://www.lcdf.org/gifsicle'.\n\n"
              "This package will be used to optimise gifs produced via,\n"
              "e.g. metawards-plot --animate. Optimising gifs reduces their\n"
              "size by 5-10 times.")


def cli():
    import os
    import sys

    args, parser = parse_args()

    if args.pip:
        install_cmd = "pip"
    elif args.conda:
        install_cmd = "conda"
    else:
        install_cmd = "pip"

    if args.user:
        if install_cmd.find("pip") != -1:
            user = " --user"
        else:
            print("You cannot use '--user' with conda. Try using a "
                  "conda environment instead.")
            sys.exit(-1)
    else:
        user = ""

    # the requirements should have been installed to
    # share/metawards/requirements
    metawards_dir = "share/metawards"

    d = os.path.join(sys.prefix, metawards_dir)

    if os.path.exists(d):
        metawards_dir = d
    else:
        import site
        d = os.path.join(site.USER_BASE, metawards_dir)
        if os.path.exists(d):
            metawards_dir = d
        else:
            raise AssertionError(
                f"MetaWards does not appear to be installed correctly. "
                f"There should be a 'share/metawards' directory in "
                f"either {sys.prefix} or {site.USER_BASE}.")

    requirements = os.path.join(metawards_dir,
                                "requirements",
                                "requirements-optional.txt")

    deps = open(requirements).readlines()
    deps = [dep.strip() for dep in deps]

    if args.list:
        for dep in deps:
            print(dep)

    if args.install_optional:
        failures = []

        for dep in deps:
            cmd = f"{install_cmd} install{user} {dep}"

            result = run_command(cmd, args.dry_run)

            if result != 0:
                failures.append(dep)

            print("")

        check_gifsicle()

        if not args.dry_run:
            if len(failures) == 0:
                print("\nEverything install correctly :-)")
            else:
                print(
                    f"\nProblems installing {failures}. See above for errors")
