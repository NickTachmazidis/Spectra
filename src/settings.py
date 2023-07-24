# Core
import sys
# GUI
from PyQt5 import QtWidgets, uic
# Configurations
from omegaconf import OmegaConf
# src
from .gui.functions import Funcs

class Settings(QtWidgets.QMainWindow, Funcs):

    def __init__(self, settings):
        super().__init__()
        uic.loadUi('./src/UI/settings.ui', self)
        self.curves: dict()
        self.actions: bool = False

        # Settings
        self.settings = settings
        
        # Buttons
        self.button_ok.clicked.connect(lambda: self.ok())
        self.button_cancel.clicked.connect(lambda: self.cancel())
        
        # Tab1: General
        self.lineEdit_dir.setText(self.settings.general.path)
        self.lineEdit_dir.textChanged.connect(self.changed_text)
        self.lineEdit_sep.setText(self.settings.general.sep)
        self.lineEdit_sep.textChanged.connect(self.changed_text)
        
        # Tab2: Curves
        self.dropdown_curves.activated.connect(self.dropdown_text_changed)
        # self.lineEdit_label
        # self.ls_dropdown
        # self.lineEdit_lw.setText(str(self.add_setting("Curves.lw")))
        # self.lineEdit_color
        # self.dropdown_mrkr
        # self.lineEdit_mrkr_size
        # self.lineEdit_mrkr_fcolor
        # self.lineEdit_mrkr_ecolor
        
        # Tab3: Functions
        # Savgol Smoothing
        self.lineEdit_window_length.setText(str(self.settings.smooth.window_length))
        self.lineEdit_window_length.textChanged.connect(self.changed_text)
        self.lineEdit_polyorder.setText(str(self.settings.smooth.polyorder))
        self.lineEdit_polyorder.textChanged.connect(self.changed_text)
        self.lineEdit_deriv.setText(str(self.settings.smooth.deriv))
        self.lineEdit_deriv.textChanged.connect(self.changed_text)
        self.lineEdit_delta.setText(str(self.settings.smooth.delta))
        self.lineEdit_delta.textChanged.connect(self.changed_text)
        self.lineEdit_axis.setText(str(self.settings.smooth.axis))
        self.lineEdit_axis.textChanged.connect(self.changed_text)
        
        # Peaks
        self.lineEdit_height.setText(str(self.settings.peaks.height))
        self.lineEdit_height.textChanged.connect(self.changed_text)
        self.lineEdit_threshold.setText(str(self.settings.peaks.threshold))
        self.lineEdit_threshold.textChanged.connect(self.changed_text)
        self.lineEdit_distance.setText(str(self.settings.peaks.distance))
        self.lineEdit_distance.textChanged.connect(self.changed_text)
        self.lineEdit_prominence.setText(str(self.settings.peaks.prominence))
        self.lineEdit_prominence.textChanged.connect(self.changed_text)
        self.lineEdit_width.setText(str(self.settings.peaks.width))
        self.lineEdit_width.textChanged.connect(self.changed_text)
        
        # Baseline
        self.lineEdit_lam.setText(str(self.settings.baseline.lam))
        self.lineEdit_lam.textChanged.connect(self.changed_text)
        self.lineEdit_p.setText(str(self.settings.baseline.p))
        self.lineEdit_p.textChanged.connect(self.changed_text)
        self.lineEdit_niter.setText(str(self.settings.baseline.niter))
        self.lineEdit_niter.textChanged.connect(self.changed_text)
        
        # Tab4: Shortcuts
        self.lineEdit_load.setText(str(self.settings.shortcuts.load))
        self.lineEdit_load.textChanged.connect(self.changed_text)
        self.lineEdit_baseline.setText(str(self.settings.shortcuts.baseline))
        self.lineEdit_baseline.textChanged.connect(self.changed_text)
        self.lineEdit_smoothing.setText(str(self.settings.shortcuts.smoothing))
        self.lineEdit_smoothing.textChanged.connect(self.changed_text)
        self.lineEdit_peaks.setText(str(self.settings.shortcuts.peaks))
        self.lineEdit_peaks.textChanged.connect(self.changed_text)
        self.lineEdit_add_plot.setText(str(self.settings.shortcuts.add_plot))
        self.lineEdit_add_plot.textChanged.connect(self.changed_text)
        self.lineEdit_normalize.setText(str(self.settings.shortcuts.normalize))
        self.lineEdit_normalize.textChanged.connect(self.changed_text)
        self.lineEdit_normalize_z.setText(str(self.settings.shortcuts.normalize_z))
        self.lineEdit_normalize_z.textChanged.connect(self.changed_text)
        self.lineEdit_reverse_x.setText(str(self.settings.shortcuts.reverse_x))
        self.lineEdit_reverse_x.textChanged.connect(self.changed_text)
        self.lineEdit_reverse_y.setText(str(self.settings.shortcuts.reverse_y))
        self.lineEdit_reverse_y.textChanged.connect(self.changed_text)
        self.lineEdit_edit.setText(str(self.settings.shortcuts.edit))
        self.lineEdit_edit.textChanged.connect(self.changed_text)
        self.lineEdit_save_as.setText(str(self.settings.shortcuts.save_as))
        self.lineEdit_save_as.textChanged.connect(self.changed_text)
        self.lineEdit_settings.setText(str(self.settings.shortcuts.settings))
        self.lineEdit_settings.textChanged.connect(self.changed_text)
        self.lineEdit_undo.setText(str(self.settings.shortcuts.undo))
        self.lineEdit_undo.textChanged.connect(self.changed_text)
        self.lineEdit_redo.setText(str(self.settings.shortcuts.redo))
        self.lineEdit_redo.textChanged.connect(self.changed_text)

    def changed_text(self, text: str) -> None:
        # General
        if self.lineEdit_dir.text() == text:
            self.settings.general.path = str(text)
        elif self.lineEdit_sep.text() == text:
            self.settings.general.sep = str(text)
        # Curves
        elif self.lineEdit_lw.text() == text:
            self.settings.general.lw = float(text)
        # Functions
        # Savgol Smoothing
        elif self.lineEdit_window_length.text() == text:
            self.settings.smooth.window_length = int(text)
        elif self.lineEdit_polyorder.text() == text:
            self.settings.smooth.polyorder = int(text)
        elif self.lineEdit_deriv.text() == text:
            self.settings.smooth.deriv = int(text)
        elif self.lineEdit_deriv.text() == text:
            self.settings.smooth.delta = float(text)
        elif self.lineEdit_delta.text() == text:
            self.settings.smooth.axis = int(text)
        # Peaks
        elif self.lineEdit_height.text() == text:
            self.settings.peaks.height = int(text)
        elif self.lineEdit_threshold.text() == text:
            self.settings.peaks.threshold = int(text)
        elif self.lineEdit_distance.text() == text:
            self.settings.peaks.distance = int(text)
        elif self.lineEdit_prominence.text() == text:
            self.settings.peaks.prominence = float(text)
        elif self.lineEdit_width.text() == text:
            self.settings.peaks.width = int(text)
        # Baseline
        elif self.lineEdit_lam.text() == text:
            self.settings.baseline.lam = int(text)
        elif self.lineEdit_p.text() == text:
            self.settings.baseline.p = float(text)
        elif self.lineEdit_niter.text() == text:
            self.settings.baseline.niter = int(text)
        # Shortcuts    
        elif self.lineEdit_load.text() == text:
            self.settings.shortcuts.load = str(text)    
        elif self.lineEdit_baseline.text() == text:
            self.settings.shortcuts.baseline = str(text)
        elif self.lineEdit_smoothing.text() == text:
            self.settings.shortcuts.smoothing = str(text)
        elif self.lineEdit_peaks.text() == text:
            self.settings.shortcuts.peaks = str(text)
        elif self.lineEdit_add_plot.text() == text:
            self.settings.shortcuts.add_plot = str(text)
        elif self.lineEdit_normalize.text() == text:
            self.settings.shortcuts.normalize = str(text)
        elif self.lineEdit_normalize_z.text() == text:
            self.settings.shortcuts.normalize_z = str(text)
        elif self.lineEdit_reverse_x.text() == text:
            self.settings.shortcuts.reverse_x = str(text)
        elif self.lineEdit_reverse_y.text() == text:
            self.settings.shortcuts.reverse_y = str(text)
        elif self.lineEdit_edit.text() == text:
            self.settings.shortcuts.edit = str(text)
        elif self.lineEdit_save_as.text() == text:
            self.settings.shortcuts.save_as = str(text)
        elif self.lineEdit_settings.text() == text:
            self.settings.shortcuts.settings = str(text)
        elif self.lineEdit_undo.text() == text:
            self.settings.shortcuts.undo = str(text)
        elif self.lineEdit_redo.text() == text:
            self.settings.shortcuts.redo = str(text)
        self.actions = True
        
    def update_dropdown(self, data) -> None:
        self.dropdown_curves.clear() 
        self.dropdown_curves.addItems(
            [i.label() for i in data.values() if i.tristate == 1])
        self.dropdown_spectrum_properties(list(data.values())[0])
        self.curves = data

    def dropdown_text_changed(self,text) -> None:
        text = self.dropdown_curves.currentText()
        for i in self.curves.values():
            if text == i.label():
                self.dropdown_spectrum_properties(i)

    def dropdown_spectrum_properties(self, spectrum) -> None:
        self.lineEdit_label.setText(spectrum.label())
        self.lineEdit_lw.setText(str(spectrum.lw()))
        self.lineEdit_color.setText(spectrum.color)
        self.lineEdit_mrkr_size.setText(str(spectrum.mrkr_size()))
        self.lineEdit_mrkr_fcolor.setText(spectrum.mrkr_face())
        self.lineEdit_mrkr_ecolor.setText(spectrum.mrkr_edge())

    def ok(self) -> None:
        if self.actions:
            """ save new parameters to the "config.yaml" """
            conf = OmegaConf.create(self.settings)
            OmegaConf.save(config=conf, f='./src/conf/config.yaml')
        self.close()

    def cancel(self) -> None:
        if self.actions:
            conf = OmegaConf.load('./src/conf/original_settings.yaml')
            self.settings = conf
        self.close()

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = Settings()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()