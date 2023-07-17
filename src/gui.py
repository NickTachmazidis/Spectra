# Core
from itertools import count
from typing import List
# GUI
from PyQt5 import QtCore, QtWidgets, uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
# Data/visualisation
import pandas as pd
import seaborn as sns
# src
from .functions import Funcs
from .settings import Settings
from .spectra import Spectrum

# Set style for plotting
sns.set_style("darkgrid",{
        'xtick.color':'#999999',
        'ytick.color':'#999999',
        'xtick.labelsize': .5,
        'ytick.labelsize': .5,
        'font.family':'serif',
        'axes.grid': True})

class Canvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=5, dpi=160):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(Canvas, self).__init__(fig)
        
        def onframe(event):
            # make cursor invisible
            self.setCursor(QtCore.Qt.BlankCursor)

        fig.canvas.mpl_connect('figure_enter_event',onframe)
        
        # Adjust canvas size
        fig.subplots_adjust(top=0.941,
                            bottom=0.096,
                            left=0.043,
                            right=0.99,
                            hspace=0.2,
                            wspace=0.2)

class Main(QtWidgets.QMainWindow, Funcs):

    def __init__(self, settings):
        super().__init__()
        # Load UI
        uic.loadUi('./src/UI/main.ui', self)
        
        # Initiate Canvas and Toolbar
        self.canvas = Canvas(self, width=10, height=18, dpi=120)
        self.toolbar = NavigationToolbar2QT(self.canvas,self)
       
        # Initiate the settings from ./conf/config.yaml
        self.settings = settings

        # Initialize variables       
        self.x: List[float] = [1,2,3]
        self.y: List[float] = [1,2,3]
        self.title: str  = ''
        self.xlabel: str = ''
        self.ylabel: str = ''
        self.x_rev: bool = False
        self.y_rev: bool = False
        self.legend: bool = False
        self.label: str = 'demo'
        self.count = count()

        self.load_list: List[Spectrum] = []
        self.labels: List[str] = ['None']
        self.added: List[str] = ['']
        self.curves = dict()

        # Plot a a demo line
        self.plot_demo()
        
        # Initialize My_peaks DataFrame
        self.df_p = pd.DataFrame(columns=['p_x','p_y'])
        
        # Undo-Redo stacks
        self.undo_stack = [('Load','', self.canvas.axes.lines[-1])]
        self.redo_stack = []

        # Add Canvas and Toolbar to the Layout
        self.verticalLayout_3.insertWidget(0,self.canvas)
        self.verticalLayout_3.insertWidget(1,self.toolbar)

        # Buttons
        self.button_load.clicked.connect(lambda: self.load())
        self.button_load.setShortcut(self.settings.shortcuts.load)

        self.button_clear_table.clicked.connect(self.clear_peaks_table)
        
        self.button_save_table.clicked.connect(self.save_table)
        
        self.button_lbl.clicked.connect(lambda: self.add_label())
        
        self.button_peaks.clicked.connect(lambda: self.peaks_find())
        self.button_peaks.setShortcut(self.settings.shortcuts.peaks)
        self.button_save_as.clicked.connect(lambda: self.save_as())
        self.button_save_as.setShortcut(self.settings.shortcuts.save_as)
        self.button_settings.clicked.connect(lambda: self.open_settings())
        self.button_settings.setShortcut(self.settings.shortcuts.settings)
        self.button_add_plot.clicked.connect(lambda: self.add_plot())
        self.button_add_plot.setShortcut(self.settings.shortcuts.add_plot)
        self.button_baseline.clicked.connect(lambda: self.baseline())
        self.button_baseline.setShortcut(self.settings.shortcuts.baseline)
        self.button_savgol.clicked.connect(lambda: self.smoothing())
        self.button_savgol.setShortcut(self.settings.shortcuts.smoothing)
        self.button_edit.clicked.connect(lambda: self.edit_form())
        self.button_edit.setShortcut(self.settings.shortcuts.edit)
        self.button_reverse_y.clicked.connect(lambda: self.reverse_y())
        self.button_reverse_y.setShortcut(self.settings.shortcuts.reverse_y)
        self.button_reverse_x.clicked.connect(lambda: self.reverse_x())
        self.button_reverse_x.setShortcut(self.settings.shortcuts.reverse_x)
        self.button_normalize_z.clicked.connect(lambda: self.norm_z())
        self.button_normalize_z.setShortcut(self.settings.shortcuts.normalize_z)
        self.button_normalize.clicked.connect(lambda: self.norm_min_max())
        self.button_normalize.setShortcut(self.settings.shortcuts.normalize)
        self.button_undo.clicked.connect(lambda: self.undo())
        self.button_undo.setShortcut(self.settings.shortcuts.undo)
        self.button_redo.clicked.connect(lambda: self.redo())
        self.button_redo.setShortcut(self.settings.shortcuts.redo)
        self.button_change.clicked.connect(lambda: self.prom_change())

        # Tables
        self.table.cellClicked.connect(self.chkbox_clicked)
        
        # Spinboxes & Checkbox
        self.doubleSpinBox_y_axis.valueChanged.connect(
                    lambda: self.spinbox_value_changed('y'))
        self.doubleSpinBox_x_axis.valueChanged.connect(
                    lambda: self.spinbox_value_changed('x'))
        self.legend_checkBox.stateChanged.connect(lambda: self.add_legend())

        # Show Window
        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas.setFocus()
        self.show()           # uncomment for small window and comment showMaximized
        # self.showMaximized()
        
        # Initialize Settings
        self.settings_ui = Settings(self.settings)
        
        # Manual Peaks
        def onclick(event) -> None:
            # Add marks for peaks with left double click
            if event.button == 1 and event.dblclick: 
                new_row = pd.DataFrame({'p_x': event.xdata, 'p_y': event.ydata},
                                        index=[str(next(self.count))])
                # self.df_p = self.df_p.append(new_row)
                self.df_p = pd.concat([self.df_p,new_row])                
                self.df_p_plot()
                self.undo_stack.append(('New_my_peak', new_row))
                self.canvas_update()
        
        self.canvas.mpl_connect('button_press_event', onclick)

        def keypress(event) -> None:
            # Delete peaks with control+delete
            if event.key == 'ctrl+delete':
                if not self.df_p.empty:
                    last = self.df_p.tail(1)
                    self.df_p = self.df_p.drop(last.index).reset_index(drop=True)
                    self.undo_stack.append(('Delete_my_peak', last, None))
                    self.update_peaks_table()
                    self.canvas.axes.collections[-1].remove()
            self.canvas_update()

        self.canvas.mpl_connect('key_press_event',keypress)