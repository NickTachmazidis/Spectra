"""Spectra processing functions used in the GUI app."""

import numpy as np
from matplotlib.lines import Line2D
from omegaconf import DictConfig
from scipy import sparse
from scipy.signal import find_peaks
from scipy.signal import savgol_filter

from ..classes.spectra import Peaks
from ..classes.spectra import Spectrum
from ..functions.canvas import canvas_remove
from ..gui.canvas import Canvas


def smoothing(*args) -> tuple[str, np.ndarray, np.ndarray, Spectrum]:
    """
    Smooths the lines by removing the noise in the signal,
    using the Savitzky-Golay filter.

    """
    # Unpack the arguments
    sp: Spectrum = args[0]
    params: DictConfig = args[1]

    # Get the previous y data
    prev: np.ndarray = np.copy(sp.y_data)

    y_smooth = savgol_filter(
        x=sp.y_data,
        window_length=params.window_length,
        polyorder=params.polyorder,
        deriv=params.deriv,
        delta=params.delta,
        axis=params.axis,
    )

    # Update the y data
    sp.y = y_smooth

    return ("Smooth", prev, y_smooth, sp)


def peaks_find(*args) -> tuple[str, Line2D, Spectrum]:
    """Finds peaks in the curves."""
    # Unpack the arguments
    sp: Spectrum = args[0]
    params: DictConfig = args[1][0]
    canvas: Canvas = args[1][1]

    if sp.has_peaks:
        # remove the sp.peak_object from the canvas
        canvas_remove(sp.peaks)
        sp.peaks_object = None

    peaks, _ = find_peaks(
        x=sp.y_data,
        height=params.height,
        threshold=params.threshold,
        distance=params.distance,
        prominence=params.prominence,
        width=params.width,
    )

    if peaks.size > 0:
        sp.has_peaks = True

        pks = canvas.axes.scatter(
            x=sp.x_data[peaks], 
            y=sp.y_data[peaks],
            c="red",
            s=2,
            zorder=3,
            label=f"peak_{sp.label}"
        )
        
        # Update the peaks object within the Spectrum object
        pks_obj = Peaks(pks)
        sp.peaks = pks_obj

        return ("Peaks", pks_obj, sp)


def baseline(*args) -> tuple[str, np.ndarray, np.ndarray, Spectrum]:
    """Removes the baseline from the lines.

    Based on "Asymmetric Least Squares Smoothing" paper
    by P. Eilers and H. Boelens in 2005.
    
    """
    # Unpack the arguments
    sp: Spectrum = args[0]
    params: DictConfig = args[1]

    # Get the previous y data
    prev = np.copy(sp.y)

    # Initialize the variables
    y_ = sp.y
    lam = params.lam
    p = params.p
    niter = params.niter

    L = len(y_)
    D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
    # Precompute this term since it does not depend on `w`
    D = lam * D.dot(D.transpose())
    w = np.ones(L)
    W = sparse.spdiags(w, 0, L, L)
    for _ in range(niter):
        # Do not create a new matrix, just update diagonal values
        W.setdiag(w)
        Z = W + D
        z = sparse.linalg.spsolve(Z, w * sp.y)
        w = p * (sp.y > z) + (1 - p) * (sp.y < z)

    y_baseline = abs(z - y_)

    # Update the y data
    sp.y = y_baseline

    return ("Baseline", prev, y_baseline, sp)


def norm_min_max(*args) -> tuple[str, np.ndarray, np.ndarray, Spectrum]:
    """
    Applies the Min-Max Normalization:

    normalized_value = ( x - min(x)) / (max(x) - min(x))

    where:
        x - original array
        min(x) - minimum value of the array
        max(x) - maximum value of the array

    """
    # Unpack the arguments
    sp: Spectrum = args[0]

    # Get the previous y data
    prev: np.ndarray = np.copy(sp.y_data)

    # Calculate the min and max values
    min_val = sp.y_data.min()
    max_val = sp.y_data.max()

    y_normalized = (sp.y_data - min_val) / (max_val - min_val)

    # Update the y data
    sp.y = y_normalized

    return ("Normalize Min-Max", prev, y_normalized, sp)


def norm_z(*args) -> tuple[str, np.ndarray, np.ndarray, Spectrum]:
    """
    Applies the Z-score Normalization:

    normalized_value = ( x - mean) / std

    where:
        x - original value
        mean - mean of the array
        std - standard deviation of the array

    """
    # Unpack the arguments
    sp: Spectrum = args[0]

    # Get the previous y data
    prev: np.ndarray = np.copy(sp.y_data)

    # Calculate the mean and std values
    mean_val = sp.y_data.mean()
    std_val = sp.y_data.std()

    y_normalized_z = (sp.y_data - mean_val) / std_val

    # Update the y data
    sp.y = y_normalized_z

    return ("Normalize Z", prev, y_normalized_z, sp)
