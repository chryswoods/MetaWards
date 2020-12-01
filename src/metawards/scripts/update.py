
def parse_args():
    """Parse all of the command line arguments"""
    import configargparse
    import sys

    configargparse.init_argument_parser(
        name="main",
        description="MetaWards update program. Used to update the software. "
        "https://metawards.org for more information.",
        prog="metawards-update")

    parser = configargparse.get_argument_parser("main")

    parser.add_argument('--version', action="store_true",
                        default=None,
                        help="Print the version information about "
                             "metawards-install")

    parser.add_argument('--update', action="store_true",
                        default=None,
                        help="Update MetaWards to the latest version")

    parser.add_argument('--check-for-updates', action="store_true",
                        default=None,
                        help="Print whether or not there are any updates "
                             "available. If there aren't, then nothing "
                             "is printed to the screen")

    parser.add_argument("--dry-run", action="store_true",
                        default=None,
                        help="Just print out what will be done - don't "
                             "actually do anything")

    parser.add_argument("--user", action="store_true",
                        default=None,
                        help="Install updates using '--user' rather than "
                             "globally.")

    args = parser.parse_args()

    if args.version:
        from metawards import get_version_string
        print(get_version_string())
        sys.exit(0)

    return (args, parser)


def cli():
    args, parser = parse_args()

    if args.update:
        from metawards.utils import update_metawards
        update_metawards(dry_run=args.dry_run, user=args.user)
    elif args.check_for_updates:
        from metawards.utils import check_for_updates
        updates = check_for_updates(dry_run=args.dry_run)

        if updates:
            print(updates)

    else:
        parser.print_help()
