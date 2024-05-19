import numpy as np
from matplotlib.lines import Line2D
from omegaconf import DictConfig
from scipy import sparse
from scipy.signal import find_peaks, savgol_filter

from src.functions.canvas import canvas_remove
from src.gui.canvas import Canvas
from src.classes.spectra import Spectrum


def smoothing(*args) -> tuple[str, np.ndarray, np.ndarray, Spectrum]:
    """
    Smooths the lines by removing the noise in the signal,
    using the Savitzky-Golay filter.

    """
    sp: Spectrum = args[0]
    params: DictConfig = args[1]
    prev: np.ndarray = np.copy(sp.y_data)

    y_smooth = savgol_filter(
        x=sp.y_data,
        window_length=params.window_length,
        polyorder=params.polyorder,
        deriv=params.deriv,
        delta=params.delta,
        axis=params.axis,
    )

    sp.y = y_smooth

    return ("Smooth", prev, y_smooth, sp)


def peaks_find(*args) -> tuple[str, Line2D, Spectrum]:
    """Finds peaks in the lines."""

    sp: Spectrum = args[0]
    params: DictConfig = args[1][0]
    canvas: Canvas = args[1][1]

    if sp.has_peaks:
        # find the sp.peak_object in the canvas and remove it
        canvas_remove(canvas, sp.peaks_object)
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

        pks = canvas.axes.plot(
            sp.x_data[peaks], 
            sp.y_data[peaks],
            "ro",
            ms=2,
            label=f"peak_{sp.label}"
        )[-1]

        sp.peaks_object = pks
        
        return ("Peaks", pks, sp)


def baseline(*args) -> tuple[str, np.ndarray, np.ndarray, Spectrum]:
    """Removes the baseline from the lines.

    Based on "Asymmetric Least Squares Smoothing" paper
    by P. Eilers and H. Boelens in 2005.
    
    """
    sp: Spectrum = args[0]
    params: DictConfig = args[1]
    prev = np.copy(sp.y)

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
    sp: Spectrum = args[0]
    prev: np.ndarray = np.copy(sp.y_data)

    min_val = sp.y_data.min()
    max_val = sp.y_data.max()

    y_normalized = (sp.y_data - min_val) / (max_val - min_val)

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
    sp: Spectrum = args[0]
    prev: np.ndarray = np.copy(sp.y_data)

    mean_val = sp.y_data.mean()
    std_val = sp.y_data.std()

    y_normalized_z = (sp.y_data - mean_val) / std_val

    sp.y = y_normalized_z

    return ("Normalize Z", prev, y_normalized_z, sp)
