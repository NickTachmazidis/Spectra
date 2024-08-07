"""Spectrum class used in the GUI."""

from itertools import count
from typing import Iterator, Optional

import numpy as np
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from .peaks import Peaks


class Spectrum:
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
        self.tristate: int = 1  # -1 tristate, 0 unchecked, 1 checked

        # Data proccessing
        self.y_orig: np.ndarray = np.copy(self.y_data)

        # Color
        self._color: str = self.curve.get_color()

        # Peaks
        self.has_peaks: bool = False
        self._peaks_object: Optional[Peaks] = None
        self.old_peaks: Optional[Peaks] = None
    
    @property
    def y(self):
        """The y data of the Spectrum."""
        return self.y_data

    @y.setter
    def y(self, value):
        """Changes the current y values."""
        self.curve.set_ydata(value)
        self.y_data = value

    @property
    def peaks(self):
        return self._peaks_object
    
    @peaks.setter
    def peaks(self, value: Peaks) -> None:
        if not isinstance(value, Peaks):
            raise ValueError("value must be a Peaks object.")
        self._peaks_object = value

    def visible(self) -> None:
        self.curve.set_visible(True)
        self.curve.set_color(self._color)
        self.tristate = 1

    def invisible(self) -> None:
        self.curve.set_visible(False)
        self.tristate = 0

    def disabled(self) -> None:
        self.curve.set_visible(True)
        self.curve.set_color("grey")
        self.tristate = -1

    def delete_peaks(self) -> None:
        self.has_peaks = False
        self._peaks_object = None

    def add_peaks(self, peaks_obj: Peaks, ax: Optional[Axes] = None) -> None:
        self.has_peaks = True
        self._peaks_object = peaks_obj
        if ax is not None:
            self._peaks_object.add_to_axes(ax)

    def __str__(self):
        return f"{self.label}"


class SpectrumList:
    """Spectrum list class to manage spectra."""

    def __init__(self) -> None:
        self._list = {}

    def add(self, spectrum):
        if not self._list.get(spectrum.id, False):
            self._list[spectrum.id] = {
                "spectrum": spectrum,
                "name": spectrum.label,
                "visible": True,
                "peaks": spectrum.peaks,
            }

    @property
    def list(self):
        return self._list
