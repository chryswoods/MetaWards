
__all__ = ["import_graphics_modules",
           "save_summary_plots",
           "create_overview_plot",
           "create_average_plot",
           "create_demographics_plot"]


def import_graphics_modules(verbose=False):
    """Imports pandas and matplotlib in a safe way, giving a good
       error message if something goes wrong.

       Parameters
       ----------
       verbose: bool
         Whether or not to print to the screen to signal progress...

       Returns
       -------
       (pd, plt)
          The pandas (pd) and matplotlib.pyplot (plt) modules
    """
    try:
        if verbose:
            print("Importing graphics modules...")
        import pandas as pd
        import matplotlib.pyplot as plt
    except ImportError:
        print("You must have pandas and matplotlib installed to run "
              "metawards-plot")
        print("Install using either `pip install pandas` if you are using")
        print("pip, or 'conda install pandas' if you are using conda, ")
        print("or by running 'metawards-install --optional")
        raise ImportError("Cannot produce the plot as pandas and matplotlib "
                          "are not installed.")

    return (pd, plt)


def create_overview_plot(df, output_dir: str = None,
                         format: str = "jpg", dpi: int = 150,
                         align_axes: bool = True, verbose: bool = True):
    """Create a summary plot of the result.csv data held in the
       passed pandas dataframe. This returns the figure for you
       to save if desired (or just call ``plt.show()`` to show
       it in Jupyter)

       If the dataframe contains multiple fingerprints, then this
       will return a dictionary of figures, one for each fingerprint,
       indexed by fingerprint

       Parameters
       ----------
       df : Pandas Dataframe
         The pandas dataframe containing the data from results.csv.bz2
       output_dir: str
         The name of the directory in which to draw the graphs. If this
         is set then the graphs are written to files as they are generated
         and the filenames of the figures are returned. This is necessary
         when the number of graphs to draw is high and you don't want
         to waste too much memory
       format: str
         Format to save the figures in if output_dir is supplied
       dpi: int
         dpi (dots per inch) resolution to save the figures with if
         a bitmap format is used and output_dir is supplied
       align_axes: bool
         If true (default) then this will ensure that all of the plots
         for different fingerprints are put on the same axis scale
       verbose: bool
         Whether or not to print progress to the screen

       Returns
       -------
       fig
         The matplotlib figure containing the summary plot, or a
         dictionary of figures if there are multiple fingerprints,
         or the filename if output_dir was supplied, or a dictionary
         of multiple filenames indexed by fingerprint
    """
    _, plt = import_graphics_modules()

    try:
        fingerprints = df["fingerprint"].unique()
        repeat = "repeat"
    except Exception:
        # no fingerprints
        fingerprints = [None]
        repeat = "demographic"

    try:
        import PIL        # noqa - disable unused warning
    except ImportError:
        if format == "jpg":
            print(
                "WARNING: Missing 'pillow' package, defaulting to PNG format.")
            format = "png"

    figs = {}

    min_date = None
    max_date = None
    max_y = {}
    min_y = {}

    columns = ["E", "I", "IW", "R"]

    nfigs = len(fingerprints)

    if len(fingerprints) > 1 and align_axes:
        for fingerprint in fingerprints:
            df2 = df[df["fingerprint"] == fingerprint]

            for column in columns:
                min_d = df2["day"].min()
                max_d = df2["day"].max()
                min_val = df2[column].min()
                max_val = df2[column].max()

                if min_date is None:
                    min_date = min_d
                    max_date = max_d
                else:
                    if min_d < min_date:
                        min_date = min_d
                    if max_d > max_date:
                        max_date = max_d

                if column not in min_y:
                    min_y[column] = min_val
                    max_y[column] = max_val
                else:
                    if min_val < min_y[column]:
                        min_y[column] = min_val
                    if max_val > max_y[column]:
                        max_y[column] = max_val

    for fingerprint in fingerprints:
        if fingerprint is None:
            df2 = df
        else:
            df2 = df[df["fingerprint"] == fingerprint]

        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 10))

        i = 0
        j = 0

        for column in columns:
            ax = df2.pivot(index="date", columns=repeat,
                           values=column).plot.line(ax=axes[i][j])
            ax.tick_params('x', labelrotation=90)
            ax.get_legend().remove()
            ax.set_ylabel("Population")

            if len(fingerprints) > 1 and align_axes:
                ax.set_xlim(min_date, max_date)
                ax.set_ylim(min_y[column], 1.1*max_y[column])

            if len(fingerprints) > 1:
                from metawards import VariableSet
                fvals, _rpt = VariableSet.extract_values(fingerprint)
                ax.set_title(f"{fvals} : {column}")
            else:
                ax.set_title(column)

            j += 1
            if j == 2:
                j = 0
                i += 1

        fig.tight_layout(pad=1)

        if output_dir:
            import os

            if nfigs == 1:
                filename = os.path.join(output_dir, f"overview.{format}")
            else:
                filename = os.path.join(output_dir,
                                        f"overview_{fingerprint}.{format}")

            if verbose:
                print(f"Saving figure {filename}")

            fig.savefig(filename, dpi=dpi)
            plt.close()
            fig = None
            figs[fingerprint] = filename
        else:
            if verbose:
                print(f"Created the figure for {fingerprint}")

            figs[fingerprint] = fig

    if len(figs) == 0:
        return None
    elif len(figs) == 1:
        return figs[list(figs.keys())[0]]
    else:
        return figs


def create_average_plot(df, output_dir: str = None, format: str = "jpg",
                        dpi: int = 150, align_axes: bool = True,
                        verbose: bool = True):
    """Create an average plot of the result.csv data held in the
       passed pandas dataframe. This returns the figure for you
       to save if desired (or just call ``plt.show()`` to show
       it in Jupyter)

       Note that this won't do anything unless there are multiple
       repeats of the model run in the output. In that case, it
       will return None

       If the dataframe contains multiple fingerprints, then this
       will return a dictionary of figures, one for each fingerprint,
       indexed by fingerprint

       Parameters
       ----------
       df : Pandas Dataframe
         The pandas dataframe containing the data from results.csv.bz2
       output_dir: str
         The name of the directory in which to draw the graphs. If this
         is set then the graphs are written to files as they are generated
         and the filenames of the figures are returned. This is necessary
         when the number of graphs to draw is high and you don't want
         to waste too much memory
       format: str
         Format to save the figures in if output_dir is supplied
       dpi: int
         dpi (dots per inch) resolution to save the figures with if
         a bitmap format is used and output_dir is supplied
       align_axes: bool
         If true (default) then this will ensure that all of the plots
         for different fingerprints are put on the same axis scale
       verbose: bool
         Whether or not to print progress to the screen

       Returns
       -------
       fig
         The matplotlib figure containing the average plot, or a
         dictionary of figures if there are multiple fingerprints,
         or the filename if output_dir was supplied, or a dictionary
         of multiple filenames indexed by fingerprint
    """
    try:
        import PIL        # noqa - disable unused warning
    except ImportError:
        if format == "jpg":
            print(
                "WARNING: Missing 'pillow' package, defaulting to PNG format.")
            format = "png"

    fingerprints = df["fingerprint"].unique()

    figs = {}

    nfigs = len(fingerprints)

    for fingerprint in fingerprints:
        df2 = df[df["fingerprint"] == fingerprint]

        nrepeats = len(df2["repeat"].unique())

        if nrepeats > 1:
            _, plt = import_graphics_modules()

            fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 10))

            mean_average = df2.groupby("date").mean()
            stddev = df2.groupby("date").std()

            i = 0
            j = 0

            for column in ["E", "I", "IW", "R"]:
                ax = mean_average.plot.line(y=column, yerr=stddev[column],
                                            ax=axes[i][j])
                ax.tick_params('x', labelrotation=90)
                ax.get_legend().remove()
                ax.set_title(column)
                ax.set_ylabel("Population")

                j += 1
                if j == 2:
                    j = 0
                    i += 1

            fig.tight_layout(pad=1)

            if output_dir:
                import os

                if nfigs == 1:
                    filename = os.path.join(output_dir, f"average.{format}")
                else:
                    filename = os.path.join(output_dir,
                                            f"average_{fingerprint}.{format}")

                if verbose:
                    print(f"Saving figure {filename}")

                fig.savefig(filename, dpi=dpi)
                fig = None
                plt.close()
                figs[fingerprint] = filename
            else:
                if verbose:
                    print(f"Created the figure for {fingerprint}")

                figs[fingerprint] = fig

    if len(figs) == 0:
        return None
    elif len(figs) == 1:
        return figs[list(figs.keys())[0]]
    else:
        return figs


def get_color(name=None, idx=None):
    """Return a good color for the passed name or passed index (idx)"""
    name = str(name).strip().lower()

    if name == "overall":
        return "black"

    elif name in ["red", "blue", "green", "orange", "yellow", "black",
                  "white", "gray", "pink"]:
        return name

    else:
        names = ["red", "blue", "green", "orange", "pink", "gray"]

        if idx is None or idx < 0 or idx >= len(names):
            # return a random colour
            import random
            rgb = (random.random(), random.random(), random.random())
            return rgb
        else:
            return names[int(idx)]


def create_demographics_plot(df, output_dir: str = None,
                             format: str = "jpg", dpi: int = 150,
                             verbose: bool = True):
    """Create a demographics plot of the trajectory.csv data held in the
       passed pandas dataframe. This returns the figure for you
       to save if desired (or just call ``plt.show()`` to show
       it in Jupyter)

       Parameters
       ----------
       df : Pandas Dataframe
         The pandas dataframe containing the data from trajectory.csv.bz2
       output_dir: str
         The name of the directory in which to draw the graphs. If this
         is set then the graphs are written to files as they are generated
         and the filenames of the figures are returned. This is necessary
         when the number of graphs to draw is high and you don't want
         to waste too much memory
       format: str
         Format to save the figures in if output_dir is supplied
       dpi: int
         dpi (dots per inch) resolution to save the figures with if
         a bitmap format is used and output_dir is supplied
       align_axes: bool
         If true (default) then this will ensure that all of the plots
         for different fingerprints are put on the same axis scale
       verbose: bool
         Whether or not to print progress to the screen

       Returns
       -------
       fig
         The matplotlib figure containing the demographics plot, or
         the filename if output_dir was supplied
    """
    try:
        import PIL        # noqa - disable unused warning
    except ImportError:
        if format == "jpg":
            print(
                "WARNING: Missing 'pillow' package, defaulting to PNG format.")
            format = "png"

    _, plt = import_graphics_modules()

    columns = ["E", "I", "IW", "R"]

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 10))

    # see if any of these give colour names
    colors = []

    demographics = df.pivot(index="date", columns="demographic",
                            values="day").columns

    for i, demographic in enumerate(demographics):
        colors.append(get_color(demographic, i))

    i = 0
    j = 0

    for column in columns:
        ax = df.pivot(index="date", columns="demographic",
                      values=column).plot.line(ax=axes[i][j],
                                               color=colors)
        ax.tick_params('x', labelrotation=90)
        ax.set_ylabel("Population")
        ax.set_title(column)

        j += 1
        if j == 2:
            j = 0
            i += 1

    fig.tight_layout(pad=1)

    if output_dir:
        import os

        filename = os.path.join(output_dir, f"demographics.{format}")

        if verbose:
            print(f"Saving figure {filename}")

        fig.savefig(filename, dpi=dpi)
        plt.close()
        fig = filename

    return fig


def save_summary_plots(results: str, output_dir: str = None,
                       format: str = "jpg", dpi: int = 150,
                       align_axes: bool = True,
                       verbose=False):
    """Create summary plots of the data contained in the passed
       'results.csv.bz2' file that was produced by metawards
       and save them to disk.

       Parameters
       ----------
       results: str
         The full path to the file containing the results. This
         **must** have been created by ``metawards``
       output_dir: str
         Path to the directory in which you want to place the graphs.
         This defaults to the same directory that contains 'results'
       format: str
         The format to use to save the graphs. This defaults to 'pdf'
       dpi: int
         The dots-per-inch to use when saving bitmap graphics (e.g.
         png, jpg etc)
       align_axes: bool
         Whether or not to plot all graphs in a set on the same axes
       verbose: bool
         Whether or not to print progress to the screen

       Returns
       -------
       filenames: List(str)
         Full file paths of all of the files written by this function
    """
    try:
        import PIL        # noqa - disable unused warning
    except ImportError:
        if format == "jpg":
            print(
                "WARNING: Missing 'pillow' package, defaulting to PNG format.")
            format = "png"

    pd, _ = import_graphics_modules(verbose=verbose)
    import os

    if verbose:
        print(f"Reading data from {results}...")

    df = pd.read_csv(results)

    if output_dir is None:
        output_dir = os.path.dirname(results)

        if output_dir is None or len(output_dir) == 0:
            output_dir = "."

    if format is None:
        format = "pdf"

    filenames = []

    # is this an output from multiple runs?
    try:
        df["fingerprint"]
        has_fingerprint = True
    except Exception:
        has_fingerprint = False
        pass

    # does this have demographic data?
    try:
        df["demographic"]
        has_demographics = True
    except Exception:
        has_demographics = False

    if has_fingerprint:
        if verbose:
            print(f"Creating overview plot(s)...")

        figs = create_overview_plot(df, output_dir=output_dir,
                                    format=format, dpi=dpi,
                                    align_axes=align_axes)

        if isinstance(figs, dict):
            filenames += list(figs.values())
        elif figs is not None:
            filenames.append(figs)

        if verbose:
            print(f"Creating average plot(s)...")

        figs = create_average_plot(df, output_dir=output_dir,
                                   format=format, dpi=dpi,
                                   align_axes=align_axes)

        if isinstance(figs, dict):
            filenames += list(figs.values())
        elif figs is not None:
            filenames.append(figs)

    if has_demographics:
        fig = create_demographics_plot(df, output_dir=output_dir,
                                       format=format, dpi=dpi)

        if fig is not None:
            filenames.append(fig)

    return filenames
