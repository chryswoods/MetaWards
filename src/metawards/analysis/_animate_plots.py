
from typing import List as _List

__all__ = ["animate_plots", "import_animate_modules"]


def import_animate_modules():
    """Import the python modules needed to animate plots. This
       imports Python Pillow

       Returns
       -------
       (Image, ImageDraw)
         The PIL.Image and PIL.ImageDraw modules
    """
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("Could not import Python Pillow to create animated plot.")
        print("Please install using 'pip install Pillow>=6.2.1'")
        print("(or by running metawards-install --optional)")

    return (Image, ImageDraw)


def animate_plots(plots: _List[str], output: str,
                  delay: int = 500,
                  ordering: str = "fingerprint",
                  verbose = False):
    """Animate the plots contained in the filenames 'plots', writing
       the output to 'output'. Creates an animated gif of the plots
       and writes them to the file 'output'

       Parameters
       ----------
       plots: List[str]
         The list of files containing graphs to plot
       output: str
         The name of the file to write the animated gif to
       delay: int
         The delay in milliseconds between frames. Default is
         500 milliseconds (2 frames per second) which is reasonable
         for animated graphs
       ordering: str
         The ordering to use for the frames. This can be
         'fingerprint', 'filename' or 'custom'
       verbose: bool
         Whether to print out information to the screen during
         processing
    """

    if ordering == "fingerprint":
        from .._variableset import VariableSet

        if verbose:
            print("Arranging into fingerprint order...")

        fingerprints = {}

        for plot in plots:
            try:
                (values, repeat_idx) = VariableSet.extract_values(plot)
            except Exception as e:
                raise ValueError(
                    f"Could not extract a fingerprint from '{plot}'. "
                    f"Error was {e.__class__} {e}")

            if repeat_idx:
                values.append(repeat_idx)
            else:
                values.append(0)

            # now create a sortable string from these values
            key = " ".join([("%.5f" % x) for x in values])
            fingerprints[key] = plot

        keys = list(fingerprints.keys())
        keys.sort()

        plots = []
        for key in keys:
            plots.append(fingerprints[key])

    elif ordering == "filename":
        if verbose:
            print("Arranging into filename order...")

        plots.sort()

    elif ordering == "custom":
        if verbose:
            print("Using the user-supplied order...")

    else:
        print(f"Could not recognise ordering scheme {ordering}")
        raise ValueError(f"Unrecognised ordering scheme {ordering}")

    if output is None:
        import os
        common = os.path.commonprefix(plots)
        if not (common.endswith("_")):
            common += "_"

        output = f"{common}animate.gif"

    if verbose:
        print(f"Animating the below frame in this order, with a delay "
              f"between frames of {delay} ms.")

        for i, plot in enumerate(plots):
            print(f"{i+1}: {plot}")

        print(f"Output will be written to {output}")

    # open all of the images
    images = []

    (Image, ImageDraw) = import_animate_modules()

    for plot in plots:
        images.append(Image.open(plot))

    images[0].save(output, save_all=True, append_images=images[1:],
                   optimize=False, duration=delay, loop=0)

    # now try to optimize the gif
    try:
        from pygifsicle import optimize
        have_optimize = True
    except Exception:
        have_optimize = False

    if have_optimize:
        if verbose:
            print("Optimizing the resulting gif...")

        try:
            optimize(output)
        except Exception:
            if verbose:
                print("Optimisation failed - using unoptimized gif")

    return output
