"""Peaks class used in the GUI."""

from typing import Optional

import numpy as np
from matplotlib.lines import Line2D


class Peaks:
    """Peaks class for peaks contained in Spectrum objects."""

    def __init__(self, obj: Optional[Line2D] = None) -> None:
        self._obj: Line2D = obj
        self._x: np.ndarray = self._obj.get_xdata() if self._obj is not None else None
        self._label: str = self._obj.get_label() if self._obj is not None else None

    @property
    def x(self):
        return self._x

    @property
    def name(self):
        return self._label

    def visible(self):
        self._obj.set_visible(True)

    def invisible(self):
        self._obj.set_visible(False)

    def remove(self):
        self._obj.remove()

    def add(self, ax):
        ax.add_line(self._obj)

    def __str__(self):
        return f"{self.name}"
