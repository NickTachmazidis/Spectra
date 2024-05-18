# Core
from itertools import count
from typing import Any

import pandas as pd
from matplotlib.backend_bases import KeyEvent, MouseEvent
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT

# Data/visualisation
from omegaconf import DictConfig

# GUI
from PyQt5 import QtCore, QtWidgets, uic

# src
from src.classes.spectra import Spectrum
from src.gui.canvas import Canvas
from src.gui.functions import QtFunctions
from src.functions.spectra_process import baseline, norm_min_max, norm_z, peaks_find, smoothing
from src.functions.utils import save_as

class QtMain(QtWidgets.QMainWindow, QtFunctions):
    """Main Window class of the GUI app."""

    def __init__(self, settings: DictConfig) -> None:
        """Initializes the main application."""
        super().__init__()
        # Load UI
        uic.loadUi("./src/UI/main.ui", self)

        # Initiate Canvas and Toolbar
        self.canvas = Canvas(self, width=10, height=18, dpi=120)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        # Initiate the settings from ./conf/config.yaml
        self.settings = settings

        # Variables for csv_read
        self.sep = "," if settings.general.sep is None else settings.general.sep
        self.engine = "python" if len(self.sep) > 1 else settings.general.engine

        # Initialize variables
        self.x: list[float] = [1.0, 2.0, 3.0]
        self.y: list[float] = [1.0, 2.0, 3.0]
        self.title: str = ""
        self.xlabel: str = ""
        self.ylabel: str = ""
        self.x_rev: bool = False
        self.y_rev: bool = False
        self.legend: bool = False
        self.label: str = "demo"
        self.count = count()

        self.load_list: list[Spectrum] = []
        self.labels: list[str] = ["None"]
        self.added: list[str] = [""]
        self.curves: dict[str, Any] = {}

        # Plot a a demo line
        self.plot_demo()

        # Initialize My_peaks DataFrame
        self.df_p = pd.DataFrame(columns=["p_x", "p_y"])

        # Undo-Redo stacks
        self.undo_stack: list[tuple] = [("Load", "", self.canvas.axes.lines[-1])]
        self.redo_stack: list[tuple] = []

        # Add Canvas and Toolbar to the Layout
        self.verticalLayout_3.insertWidget(0, self.canvas)
        self.verticalLayout_3.insertWidget(1, self.toolbar)

        ## Buttons ##

        # Load
        self.button_load.clicked.connect(lambda: self.load())
        self.button_load.setShortcut(self.settings.shortcuts.load)

        # Peaks Table
        self.button_clear_table.clicked.connect(self.clear_peaks_table)
        self.button_save_table.clicked.connect(self.save_table)

        # Label
        self.button_lbl.clicked.connect(lambda: self.add_label())

        # Peaks
        self.button_peaks.clicked.connect(
            lambda: self.process_data(peaks_find, [self.settings.peaks, self.canvas])
        )
        self.button_peaks.setShortcut(self.settings.shortcuts.peaks)

        # Add Plot
        self.button_add_plot.clicked.connect(lambda: self.add_plot())
        self.button_add_plot.setShortcut(self.settings.shortcuts.add_plot)

        # Baseline
        self.button_baseline.clicked.connect(
            lambda: self.process_data(baseline, self.settings.baseline)
        )
        self.button_baseline.setShortcut(self.settings.shortcuts.baseline)

        # Smooth
        self.button_savgol.clicked.connect(
            lambda: self.process_data(smoothing, self.settings.smooth)
        )
        self.button_savgol.setShortcut(self.settings.shortcuts.smoothing)

        # Normalize
        self.button_normalize.clicked.connect(
            lambda: self.process_data(norm_min_max, None)
        )
        self.button_normalize.setShortcut(self.settings.shortcuts.normalize)

        # Normalize Z
        self.button_normalize_z.clicked.connect(lambda: self.process_data(norm_z, None))
        self.button_normalize_z.setShortcut(self.settings.shortcuts.normalize_z)

        # Save As
        self.button_save_as.clicked.connect(lambda: save_as(self.curves, self.sep))
        self.button_save_as.setShortcut(self.settings.shortcuts.save_as)

        # TODO Change this button and function
        # self.button_settings.clicked.connect(lambda: self.open_settings())
        # self.button_settings.setShortcut(self.settings.shortcuts.settings)

        # Edit
        self.button_edit.clicked.connect(lambda: self.edit_form())
        self.button_edit.setShortcut(self.settings.shortcuts.edit)

        # Reverse Y
        self.button_reverse_y.clicked.connect(lambda: self.reverse_axis("Y"))
        self.button_reverse_y.setShortcut(self.settings.shortcuts.reverse_y)

        # Reverse X
        self.button_reverse_x.clicked.connect(lambda: self.reverse_axis("X"))
        self.button_reverse_x.setShortcut(self.settings.shortcuts.reverse_x)

        # Undo
        self.button_undo.clicked.connect(lambda: self.undo())
        self.button_undo.setShortcut(self.settings.shortcuts.undo)
        # Redo
        self.button_redo.clicked.connect(lambda: self.redo())
        self.button_redo.setShortcut(self.settings.shortcuts.redo)
        # Prominence
        self.button_change.clicked.connect(lambda: self.prom_change())

        ## Tables ##
        self.table.cellClicked.connect(self.chkbox_clicked)

        ## Spinboxes & Checkbox ##
        self.doubleSpinBox_y_axis.valueChanged.connect(
            lambda: self.spinbox_value_changed("y")
        )
        self.doubleSpinBox_x_axis.valueChanged.connect(
            lambda: self.spinbox_value_changed("x")
        )
        self.legend_checkBox.stateChanged.connect(lambda: self.add_legend())

        ## Show Window ##
        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas.setFocus()
        self.show()  # uncomment for small window and comment showMaximized
        # self.showMaximized()

        # Manual Peaks
        def add_peak(event: MouseEvent) -> None:
            """Add marks for peaks with left double click."""
            if event.button == 1 and event.dblclick:
                new_row = pd.DataFrame(
                    {"p_x": event.xdata, "p_y": event.ydata},
                    index=[str(next(self.count))],
                )
                if self.df_p.empty:
                    self.df_p = new_row
                else:
                    self.df_p = pd.concat([self.df_p, new_row])
                
                self.df_p_plot(self.canvas.axes)
                
                self.undo_stack.append(("New_my_peak", new_row))

                if self.legend:
                    self.add_legend()

                self.canvas_update()

        self.canvas.mpl_connect("button_press_event", add_peak)

        def delete_peaks(event: KeyEvent) -> None:
            """Delete peaks with control+delete."""
            if event.key == "ctrl+delete":
                if not self.df_p.empty:
                    last = self.df_p.tail(1)
                    self.df_p = self.df_p.drop(last.index).reset_index(drop=True)
                    
                    self.undo_stack.append(("Delete_my_peak", last, None))
                    
                    self.update_peaks_table()
                    
                    self.canvas.axes.collections[-1].remove()
                
                if self.legend:
                    self.add_legend()

                self.canvas_update()

        self.canvas.mpl_connect("key_press_event", delete_peaks)
