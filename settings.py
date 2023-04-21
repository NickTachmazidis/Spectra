from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal
from functions import Funcs
import sys

class Settings(QtWidgets.QMainWindow, Funcs):
    closed = pyqtSignal(object) # signal to send the changed settings
    
    def __init__(self):
        super(Settings, self).__init__()
        uic.loadUi('./UI/settings_ui.ui', self)
        self.curves = dict()

        # Settings
        self.df_settings = self.read_json('settings.json')
        self.actions = self.df_settings.copy()
        # Buttons
        self.button_ok.clicked.connect(lambda: self.ok())
        self.button_cancel.clicked.connect(self.close)
        # Tab1: General
        self.lineEdit_dir.setText(str(self.add_setting("General.dir")))
        self.lineEdit_dir.textChanged.connect(self.changed_text)
        self.lineEdit_sep.setText(str(repr(self.add_setting("General.sep"))))
        self.lineEdit_sep.textChanged.connect(self.changed_text)
        # Tab2: Curves
        self.dropdown_curves.activated.connect(self.dropdown_text_changed)
        # Tab3: Functions
        # Savgol Smoothing
        self.lineEdit_window_length.setText(str(self.add_setting("Smooth.window_length")))
        self.lineEdit_window_length.textChanged.connect(self.changed_text)
        self.lineEdit_polyorder.setText(str(self.add_setting("Smooth.polyorder")))
        self.lineEdit_polyorder.textChanged.connect(self.changed_text)
        self.lineEdit_deriv.setText(str(self.add_setting("Smooth.deriv")))
        self.lineEdit_deriv.textChanged.connect(self.changed_text)
        self.lineEdit_delta.setText(str(self.add_setting("Smooth.delta")))
        self.lineEdit_delta.textChanged.connect(self.changed_text)
        self.lineEdit_axis.setText(str(self.add_setting("Smooth.axis")))
        self.lineEdit_axis.textChanged.connect(self.changed_text)
        # Peaks
        self.lineEdit_height.setText(str(self.add_setting("Peaks.height")))
        self.lineEdit_height.textChanged.connect(self.changed_text)
        self.lineEdit_threshold.setText(str(self.add_setting("Peaks.threshold")))
        self.lineEdit_threshold.textChanged.connect(self.changed_text)
        self.lineEdit_distance.setText(str(self.add_setting("Peaks.distance")))
        self.lineEdit_distance.textChanged.connect(self.changed_text)
        self.lineEdit_prominence.setText(str(self.add_setting("Peaks.prominence")))
        self.lineEdit_prominence.textChanged.connect(self.changed_text)
        self.lineEdit_width.setText(str(self.add_setting("Peaks.width")))
        self.lineEdit_width.textChanged.connect(self.changed_text)
        # Baseline
        self.lineEdit_lam.setText(str(self.add_setting("Baseline.lam")))
        self.lineEdit_lam.textChanged.connect(self.changed_text)
        self.lineEdit_p.setText(str(self.add_setting("Baseline.p")))
        self.lineEdit_p.textChanged.connect(self.changed_text)
        self.lineEdit_niter.setText(str(self.add_setting("Baseline.niter")))
        self.lineEdit_niter.textChanged.connect(self.changed_text)
        # Tab4: Shortcuts
        self.lineEdit_load.setText(str(self.add_setting("Shortcuts.Load")))
        self.lineEdit_load.textChanged.connect(self.changed_text)
        self.lineEdit_baseline.setText(str(self.add_setting("Shortcuts.Baseline")))
        self.lineEdit_baseline.textChanged.connect(self.changed_text)
        self.lineEdit_smoothing.setText(str(self.add_setting("Shortcuts.Smoothing")))
        self.lineEdit_smoothing.textChanged.connect(self.changed_text)
        self.lineEdit_peaks.setText(str(self.add_setting("Shortcuts.Peaks")))
        self.lineEdit_peaks.textChanged.connect(self.changed_text)
        self.lineEdit_add_plot.setText(str(self.add_setting("Shortcuts.Add_Plot")))
        self.lineEdit_add_plot.textChanged.connect(self.changed_text)
        self.lineEdit_normalize.setText(str(self.add_setting("Shortcuts.Normalize")))
        self.lineEdit_normalize.textChanged.connect(self.changed_text)
        self.lineEdit_normalize_z.setText(str(self.add_setting("Shortcuts.Normalize_Z")))
        self.lineEdit_normalize_z.textChanged.connect(self.changed_text)
        self.lineEdit_reverse_x.setText(str(self.add_setting("Shortcuts.Reverse_X")))
        self.lineEdit_reverse_x.textChanged.connect(self.changed_text)
        self.lineEdit_reverse_y.setText(str(self.add_setting("Shortcuts.Reverse_Y")))
        self.lineEdit_reverse_y.textChanged.connect(self.changed_text)
        self.lineEdit_edit.setText(str(self.add_setting("Shortcuts.Edit")))
        self.lineEdit_edit.textChanged.connect(self.changed_text)
        self.lineEdit_save_as.setText(str(self.add_setting("Shortcuts.Save_As")))
        self.lineEdit_save_as.textChanged.connect(self.changed_text)
        self.lineEdit_settings.setText(str(self.add_setting("Shortcuts.Settings")))
        self.lineEdit_settings.textChanged.connect(self.changed_text)
        self.lineEdit_undo.setText(str(self.add_setting("Shortcuts.Undo")))
        self.lineEdit_undo.textChanged.connect(self.changed_text)
        self.lineEdit_redo.setText(str(self.add_setting("Shortcuts.Redo")))
        self.lineEdit_redo.textChanged.connect(self.changed_text)

    def changed_text(self,text):
        # General
        if self.lineEdit_dir.text() == text:
            self.actions["General.dir"] = text
        elif self.lineEdit_sep.text() == text:
            self.actions["General.sep"] = text
        # Functions
        # Savgol Smoothing
        elif self.lineEdit_window_length.text() == text:
            self.actions["Smoothing.window_length"] = text
        elif self.lineEdit_polyorder.text() == text:
            self.actions["Smoothing.polyorder"] = text
        elif self.lineEdit_deriv.text() == text:
            self.actions["Smooth.deriv"] = text
        elif self.lineEdit_deriv.text() == text:
            self.actions["Smooth.delta"] = text
        elif self.lineEdit_delta.text() == text:
            self.actions["Smooth.axis"] = text
        # Peaks
        elif self.lineEdit_height.text() == text:
            self.actions["Peaks.height"] = text
        elif self.lineEdit_threshold.text() == text:
            self.actions["Peaks.threshold"] = text
        elif self.lineEdit_distance.text() == text:
            self.actions["Peaks.distance"] = text
        elif self.lineEdit_prominence.text() == text:
            self.actions["Peaks.prominence"] = text
        elif self.lineEdit_width.text() == text:
            self.actions["Peaks.width"] = text
        # Baseline
        elif self.lineEdit_lam.text() == text:
            self.actions["Baseline.lam"] = text
        elif self.lineEdit_p.text() == text:
            self.actions["Baseline.p"] = text
        elif self.lineEdit_niter.text() == text:
            self.actions["Baseline.niter"] = text
        # Shortcuts    
        elif self.lineEdit_load.text() == text:
            self.actions["Shortcuts.Load"] = text    
        elif self.lineEdit_baseline.text() == text:
            self.actions["Shortcuts.Baseline"] = text
        elif self.lineEdit_smoothing.text() == text:
            self.actions["Shortcuts.Smoothing"] = text
        elif self.lineEdit_peaks.text() == text:
            self.actions["Shortcuts.Peaks"] = text
        elif self.lineEdit_add_plot.text() == text:
            self.actions["Shortcuts.Add_Plot"] = text
        elif self.lineEdit_normalize.text() == text:
            self.actions["Shortcuts.Normalize"] = text
        elif self.lineEdit_normalize_z.text() == text:
            self.actions["Shortcuts.Normalize_Z"] = text
        elif self.lineEdit_reverse_x.text() == text:
            self.actions["Shortcuts.Reverse_X"] = text
        elif self.lineEdit_reverse_y.text() == text:
            self.actions["Shortcuts.Reverse_Y"] = text
        elif self.lineEdit_edit.text() == text:
            self.actions["Shortcuts.Edit"] = text
        elif self.lineEdit_save_as.text() == text:
            self.actions["Shortcuts.Save_As"] = text
        elif self.lineEdit_settings.text() == text:
            self.actions["Shortcuts.Settings"] = text
        elif self.lineEdit_undo.text() == text:
            self.actions["Shortcuts.Undo"] = text
        elif self.lineEdit_redo.text() == text:
            self.actions["Shortcuts.Redo"] = text
        
    def update_dropdown(self, data):
        self.dropdown_curves.clear() 
        self.dropdown_curves.addItems([i.label() for i in data.values() if i.tristate == 1])
        self.dropdown_spectrum_properties(list(data.values())[0])
        self.curves = data

    def dropdown_text_changed(self,text):
        text = self.dropdown_curves.currentText()
        for i in self.curves.values():
            if text == i.label():
                self.dropdown_spectrum_properties(i)

    def dropdown_spectrum_properties(self, spectrum):
        self.lineEdit_label.setText(spectrum.label())
        self.lineEdit_lw.setText(str(spectrum.lw()))
        self.lineEdit_color.setText(spectrum.color)
        self.lineEdit_mrkr_size.setText(str(spectrum.mrkr_size()))
        self.lineEdit_mrkr_fcolor.setText(spectrum.mrkr_face())
        self.lineEdit_mrkr_ecolor.setText(spectrum.mrkr_edge())

    def ok(self):
        if not self.df_settings.compare(self.actions).empty:
            self.actions.to_json('settings.json', orient='records')
            self.closed.emit(self.actions) # send the changed settings
        self.close()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Settings()
    w.show()
    app.exec_()