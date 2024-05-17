# Core
from itertools import count
from typing import Any, Optional, List, Iterator
# Data/visualisation
import numpy as np
from matplotlib.lines import Line2D

class Spectrum():
    # Initialize count
    newid: Iterator = count()

    def __init__(self, curve):
        # ID
        self.id: int = next(Spectrum.newid)
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
        self.y_smooth: Optional[np.ndarray] = None 
        self.y_baseline: Optional[np.ndarray] = None
        self.y_normalized: Optional[np.ndarray] = None
        self.y_normalized_z: Optional[np.ndarray] = None
        # Peaks
        self.peaks: bool = False
        self.peaks_object: Optional[np.ndarray] = None
        self.peaks_color: Optional[str] = None
        # Styles
        self.linewidth: float = self.curve.get_lw()
        self.linestyle: str = self.curve.get_ls()
        self.drawstyle: str = self.curve.get_drawstyle() 
        self.color: str = self.curve.get_color()
        self.marker: str = self.curve.get_marker()
        self.marker_size: float = self.curve.get_markersize()
        self.marker_edge_color: str = self.curve.get_markeredgecolor()
        self.marker_edge_width: float = self.curve.get_markeredgewidth()
        self.marker_face_color: str = self.curve.get_markerfacecolor()
            
    # def label(self) -> str:
    #     return self.curve.get_label()

    # def x(self) -> List:
    #     return self.curve.get_xdata()

    # def y(self) -> List:
    #     return self.curve.get_ydata()

    # def line(self) -> Line2D:
    #     return self.curve

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

    def lw(self) -> float:
        return self.linewidth

    def color(self) -> str:
        return self.color

    def mrkr_size(self) -> float:
        return self.marker_size

    def mrkr_face(self) -> str:
        return self.marker_face_color

    def mrkr_edge(self) -> str:
        return self.marker_edge_color

    def change_y(self, y: np.ndarray) -> None:
        """Changes the current y values."""
        self.curve.set_ydata(y)
        self.y_data = y