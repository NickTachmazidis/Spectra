# Core
from itertools import count
from typing import Iterator, Optional
# Data/visualisation
import numpy as np
from matplotlib.lines import Line2D

class Spectrum():
    """Spectum class for plotted data."""

    new_id: Iterator = count()

    def __init__(self, curve: Line2D) -> None:
        # ID
        self.id = next(Spectrum.new_id)
        # Data
        self.curve: Line2D = curve
        self.x_data: np.ndarray = self.curve.get_xdata()
        self.y_data: np.ndarray = self.curve.get_ydata()
        self.label: str = self.curve.get_label()

        # State
        self.loaded: bool = False
        self.tristate: int = 1 # -1 tristate, 0 unchecked, 1 checked
        
        # Data proccessing
        self.y_orig: np.ndarray = np.copy(self.y_data)
        
        # Peaks
        self.peaks: bool = False
        self.peaks_object: Optional[np.ndarray] = None

    @property
    def y(self):
        """The y data of the Spectrum."""
        return self.y_data

    @y.setter
    def y(self, value):
        """Changes the current y values."""
        self.curve.set_ydata(value)
        self.y_data = value

    def visible(self) -> None:
        self.curve.set_visible(True)
        self.curve.set_color(self.color)
        self.tristate = 1

    def invisible(self) -> None:
        self.curve.set_visible(False)
        self.tristate = 0

    def disabled(self) -> None:
        self.curve.set_visible(True)
        self.curve.set_color('grey')
        self.tristate = -1

    def delete_peaks(self) -> None:
        self.peaks        = False
        self.peaks_object = None

    def add_peaks(self, peaks_obj: np.array) -> None:
        self.peaks = True
        self.peaks_object = peaks_obj

    def __str__(self):
        return f"{self.label}"
    
class Peaks:
    """Peaks class for peaks contained in Spectrum objects."""
    def __init__(self, obj) -> None:
        pass