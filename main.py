import sys
import os

from PyQt5 import QtWidgets, QtCore, uic
import pandas as pd
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from itertools import count

from canvas import Canvas
from functions import Funcs
from settings import Settings

# Change PATH to the folder where the files will be
PATH = './Git Projects/Spectra/Version 2'
os.chdir(PATH) 

class Main(QtWidgets.QMainWindow, Funcs):

    def __init__(self):
        super(Main, self).__init__()
        # Load UI
        uic.loadUi('./UI/main_ui.ui', self)
        
        # Initiate Canvas and Toolbar
        self.canvas = Canvas(self, width=10, height=18, dpi=120)
        self.toolbar = NavigationToolbar2QT(self.canvas,self)
       
        self.df_settings = self.read_json('settings.json')

        # Initialize variables       
        self.x  = [1,2,3]
        self.y  = [1,2,3]
        self.title  = ''
        self.xlabel = ''
        self.ylabel = ''
        self.x_rev  = False
        self.y_rev  = False
        self.legend = False
        self.label  = 'demo'
        self.count = count()

        self.load_list  = []
        self.labels     = ['None']
        self.added      = ['']
        self.curves     = dict()

        # Plot a a demo line
        df = pd.DataFrame({'x':self.x,'y':self.y}, dtype='float')
        self.plot(df, self.label, 'Load')
        
        # My_peaks DataFrame
        self.df_p = pd.DataFrame(columns=['p_x','p_y'])
        
        # Data Structures
        self.undo_stack = [('Load','', self.canvas.axes.lines[-1])]
        self.redo_stack = []

        # Add Canvas and Toolbar to the Layout
        self.verticalLayout_3.insertWidget(0,self.canvas)
        self.verticalLayout_3.insertWidget(1,self.toolbar)

        # Buttons
        self.button_load.clicked.connect(lambda: self.load())
        self.button_load.setShortcut(self.add_setting("Shortcuts.Load"))
        
        self.button_clear_table.clicked.connect(self.clear_peaks_table)
        self.button_save_table.clicked.connect(self.save_table)

        self.button_lbl.clicked.connect(lambda: self.add_label())
        self.button_peaks.clicked.connect(lambda: self.peaks_find())
        self.button_peaks.setShortcut(self.add_setting("Shortcuts.Peaks"))
        self.button_save_as.clicked.connect(lambda: self.save_as())
        self.button_save_as.setShortcut(self.add_setting("Shortcuts.Save_As"))
        self.button_settings.clicked.connect(lambda: self.open_settings())
        self.button_settings.setShortcut(self.add_setting("Shortcuts.Settings"))
        self.button_add_plot.clicked.connect(lambda: self.add_plot())
        self.button_add_plot.setShortcut(self.add_setting("Shortcuts.Add_Plot"))
        self.button_baseline.clicked.connect(lambda: self.baseline())
        self.button_baseline.setShortcut(self.add_setting("Shortcuts.Baseline"))
        self.button_savgol.clicked.connect(lambda: self.smoothing())
        self.button_savgol.setShortcut(self.add_setting("Shortcuts.Smoothing"))
        self.button_edit.clicked.connect(lambda: self.edit_form())
        self.button_edit.setShortcut(self.add_setting("Shortcuts.Edit"))
        self.button_reverse_y.clicked.connect(lambda: self.reverse_y())
        self.button_reverse_y.setShortcut(self.add_setting("Shortcuts.Reverse_Y"))
        self.button_reverse_x.clicked.connect(lambda: self.reverse_x())
        self.button_reverse_x.setShortcut(self.add_setting("Shortcuts.Reverse_X"))
        self.button_normalize_z.clicked.connect(lambda: self.norm_z())
        self.button_normalize_z.setShortcut(self.add_setting("Shortcuts.Normalize_Z"))
        self.button_normalize.clicked.connect(lambda: self.norm_min_max())
        self.button_normalize.setShortcut(self.add_setting("Shortcuts.Normalize"))
        self.button_undo.clicked.connect(lambda: self.undo())
        self.button_undo.setShortcut(self.add_setting("Shortcuts.Undo"))
        self.button_redo.clicked.connect(lambda: self.redo())
        self.button_redo.setShortcut(self.add_setting("Shortcuts.Redo"))
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
        # self.show()           # uncomment for small window and comment showMaximized
        self.showMaximized()
        
        # Initialize Settings
        self.settings = Settings()
        self.settings.closed[object].connect(self.settings_closed)
        
        # Manual Peaks
        def onclick(event):
            # Add marks for peaks with left double click
            if event.button == 1 and event.dblclick: 
                new_row = pd.DataFrame({'p_x': event.xdata, 'p_y': event.ydata},
                                        index=[str(next(self.count))])
                self.df_p = self.df_p.append(new_row)
                self.df_p_plot()
                self.undo_stack.append(('New_my_peak', new_row))
                self.canvas_update()
        
        self.canvas.mpl_connect('button_press_event', onclick)

        def keypress(event):
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

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    app.exec_()