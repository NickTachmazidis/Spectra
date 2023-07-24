from typing import Tuple
import numpy as np
from matplotlib.lines import Line2D
from scipy import sparse
from scipy.signal import savgol_filter, find_peaks
from src.spectra import Spectrum

def smoothing(*args) -> Tuple[str,np.array, Spectrum]:
    """
    Smooths the lines by removing the noise in the signal,
    using the Savitzky-Golay filter.
    
    """
    sp = args[0]        # the spectrum object
    params = args[1]    # the parameters for smoothing
    
    prev = np.copy(sp.y_data)
                
    sp.y_smooth = savgol_filter(
                    x=sp.y(),
                    window_length=params.window_length,
                    polyorder=params.polyorder,
                    deriv=params.deriv,
                    delta=params.delta,
                    axis=params.axis)

    sp.y_data = sp.y_smooth

    sp.line().set_ydata(sp.y_smooth)

    # Add to undo stack
    return ('Smooth', prev, sp.y_smooth, sp)

def peaks_find(*args) -> Tuple[str, Line2D, Spectrum]:
    """Finds peaks in the lines."""
    
    sp = args[0]           # the spectrum object
    params = args[1][0]    # the parameters for peaks_find
    canvas = args[1][1]

    if sp.peaks:
        # find the sp.peak_object in the canvas and remove it
        idx = canvas.axes.lines.index(sp.peaks_object) # O(n)
        canvas.axes.lines[idx].remove()

        sp.peaks_data = []
        sp.peaks_object = False

    peaks, _ = find_peaks(
                x=sp.y(),
                height=params.height,
                threshold=params.threshold,
                distance=params.distance,
                prominence=params.prominence,
                width=params.width)

    if peaks.size > 0:
        sp.peaks = True

        pks = canvas.axes.plot(
            sp.x()[peaks],
            sp.y()[peaks],
            'ro',
            ms= 2,
            label= f"peak_{sp.label()}")[-1]
        
        sp.peaks_object = pks

        return ('Peaks', pks, sp)
    
def baseline(*args) -> Tuple[str, np.array, np.array, Spectrum]:
    """Removes the baseline from the lines.
    Based on "Asymmetric Least Squares Smoothing" paper
    by P. Eilers and H. Boelens in 2005.
    """
    sp = args[0]        # the spectrum object
    params = args[1]    # the parameters for baseline

    prev = np.copy(sp.y_data)
    y_ = sp.y_data

    lam = params.lam
    p = params.p
    niter = params.niter

    L = len(y_)
    D = sparse.diags([1,-2,1],[0,-1,-2], shape=(L,L-2))
    # Precompute this term since it does not depend on `w`
    D = lam * D.dot(D.transpose()) 
    w = np.ones(L)
    W = sparse.spdiags(w, 0, L, L)
    for _ in range(niter):
        # Do not create a new matrix, just update diagonal values
        W.setdiag(w) 
        Z = W + D
        z = sparse.linalg.spsolve(Z, w * sp.y_data)
        w = p * (sp.y_data > z) + (1-p) * (sp.y_data < z)
    
    sp.y_baseline = abs(z-y_)
    sp.y_data = sp.y_baseline
    sp.line().set_ydata(sp.y_baseline)
    # Add to undo stack
    return ('Baseline', prev, sp.y_baseline, sp)

def norm_min_max(*args) -> Tuple[str, np.array, np.array, Spectrum]:
    """
    Applies the Min-Max Normalization:

    normalized_value = ( x - min(x)) / (max(x) - min(x))

    where:
        x - original array
        min(x) - minimum value of the array
        max(x) - maximum value of the array
        
    """    
    sp = args[0]        # the spectrum object
   
    prev = np.copy(sp.y_data)
    
    min_val = sp.y().min()
    max_val = sp.y().max()

    sp.y_normalized = (sp.y() - min_val) / (max_val - min_val)
    
    sp.y_data = sp.y_normalized
    sp.curve.set_ydata(sp.y_normalized)

    return ('Normalize Min-Max', prev, sp.y_normalized, sp)

def norm_z(*args) -> Tuple[str, np.array, np.array, Spectrum]:
    """
    Applies the Z-score Normalization:

    normalized_value = ( x - mean) / std

    where:
        x - original value
        mean - mean of the array
        std - standard deviation of the array

    """
    sp = args[0]        # the spectrum object

    prev = np.copy(sp.y_data)
    
    mean_val = sp.y().mean()
    std_val = sp.y().std()

    sp.y_normalized_z = (sp.y() - mean_val) / std_val
    
    sp.y_data = sp.y_normalized_z
    sp.curve.set_ydata(sp.y_normalized_z)
    
    return ('Normalize Z', prev, sp.y_normalized_z, sp)