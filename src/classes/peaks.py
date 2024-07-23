"""Peaks class used in the GUI."""

from typing import Optional

from matplotlib.collections import PathCollection
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.axes import Axes
from zipp import Path


class Peaks:
    """Peaks class for peaks contained in Spectrum objects."""

    def __init__(self, obj: Optional[PathCollection] = None) -> None:
        self._obj: PathCollection = obj
        self._x: np.ndarray = self._obj.get_offsets()[:, 0] if self._obj is not None else None


        # self._x: np.ndarray = self._obj.get_xdata() if self._obj is not None else None
        self._label: str = self._obj.get_label() if self._obj is not None else None

    @property
    def x(self) -> np.ndarray:
        return self._x

    @property
    def name(self) -> str:
        return self._label

    def visible(self) -> None:
        self._obj.set_visible(True)

    def invisible(self) -> None:
        self._obj.set_visible(False)

    def remove(self) -> None:
        self._obj.remove()

    def add_to_axes(self, ax: Axes) -> None:
        ax.add_collection(self._obj)

    def __str__(self) -> str:
        return f"{self.name}"
