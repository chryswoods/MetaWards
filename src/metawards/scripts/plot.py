
def parse_args():
    """Parse all of the command line arguments"""
    import configargparse
    import sys

    configargparse.init_argument_parser(
        name="main",
        description="MetaWards simple plotting program - see "
        "https://metawards.org for more information.",
        prog="metawards-plot")

    parser = configargparse.get_argument_parser("main")

    parser.add_argument('--version', action="store_true",
                        default=None,
                        help="Print the version information about "
                             "metawards-plot")

    parser.add_argument('-c', '--config', is_config_file=True,
                        help="Config file that can be used to set some "
                             "or all of these command line options.")

    parser.add_argument("-i", "--input", type=str, nargs="*",
                        help="Full path to the 'results.csv.bz2' file "
                             "that you want to quickly plot.")

    parser.add_argument("-a", "--animate", type=str, nargs="*",
                        help="Full path to the set of plots that you "
                             "want to animate together into an animated "
                             "gif")

    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Location for the output. By default "
                             "this is inferred from the input")

    parser.add_argument("--format", type=str, default="jpg",
                        help="Desired format of the graphs that are "
                             "produced. Good formats are 'pdf' for "
                             "publication graphics and 'png' or 'jpeg' "
                             "for webpages")

    parser.add_argument("--align-axes", action="store_true", default=None,
                        help="Whether to align the axes of all graphs "
                             "so that they are all plotted on the same "
                             "scale (default true)")

    parser.add_argument("--no-align-axes", action="store_true", default=None,
                        help="Disable alignment of the axes of graphs. "
                             "Each graph will be drawn using its own scale")

    parser.add_argument("--dpi", type=int, default=150,
                        help="Resolution to use when creating bitmap "
                             "outputs, e.g. jpg, png etc.")

    parser.add_argument("--delay", type=int, default=500,
                        help="The delay in milliseconds between animation "
                             "frames if an animation is being produced")

    parser.add_argument("--ordering", type=str, default="fingerprint",
                        help="Ordering to use for the frames. This "
                             "can be fingerprint, filename or custom")

    args = parser.parse_args()

    if args.version:
        from metawards import get_version_string
        print(get_version_string())
        sys.exit(0)

    return (args, parser)


def cli():
    """Main function for the metawards-plot command line interface.
       This is a simple program that creates basic plots of the output
       data. The aim is to make visualisation of the data as quick
       and painless as possible.
    """
    args, parser = parse_args()

    if args.input and len(args.input) > 0:
        from metawards.analysis import save_summary_plots

        align_axes = True

        if args.align_axes:
            align_axes = True
        elif args.no_align_axes:
            align_axes = False

        for filename in args.input:
            filenames = save_summary_plots(results=filename,
                                           output_dir=args.output,
                                           format=args.format,
                                           dpi=args.dpi,
                                           align_axes=align_axes,
                                           verbose=True)

            print(f"Written graphs to {', '.join(filenames)}")

    elif args.animate is not None and len(args.animate) > 0:
        from metawards.analysis import animate_plots

        filename = animate_plots(plots=args.animate,
                                 output=args.output,
                                 delay=args.delay,
                                 ordering=args.ordering,
                                 verbose=True)

        print(f"Written animation to {filename}")
    else:
        import sys
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    cli()
