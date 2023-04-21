from itertools import count
import numpy as np

class Spectrum():
    # Initialize count Iterator
    newid = count()

    def __init__(self, curve):
        # ID
        self.id                  = next(Spectrum.newid)
        # Data
        self.curve               = curve
        self.x_data              = self.curve.get_xdata()
        self.y_data              = self.curve.get_ydata()
        # State
        self.loaded              = False
        self.tristate            = 1 # -1 tristate, 0 unchecked, 1 checked
        # Data proccessing
        self.y_orig              = np.copy(self.y())
        self.y_smooth            = None
        self.y_baseline          = None
        self.y_normalized        = None
        self.y_normalized_z      = None
        # Peaks
        self.peaks               = False
        self.peaks_object        = None
        self.peaks_color         = None
        # Styles
        self.linewidth           = self.curve.get_lw()
        self.linestyle           = self.curve.get_ls()
        self.drawstyle           = self.curve.get_drawstyle() 
        self.color               = self.curve.get_color()
        self.marker              = self.curve.get_marker()
        self.marker_size         = self.curve.get_markersize()
        self.marker_edge_color   = self.curve.get_markeredgecolor()
        self.marker_edge_width   = self.curve.get_markeredgewidth()
        self.marker_face_color   = self.curve.get_markerfacecolor()
        self.picker              = self.curve.set_pickradius(True)
            
    def label(self):
        return self.curve.get_label()

    def x(self):
        return self.curve.get_xdata()

    def y(self):
        return self.curve.get_ydata()

    def line(self):
        return self.curve

    def visible(self):
        self.curve.set_visible(True)
        self.curve.set_color(self.color)
        self.tristate = 1

    def invisible(self):
        self.curve.set_visible(False)
        self.tristate = 0

    def disabled(self):
        self.curve.set_visible(True)
        self.curve.set_color('grey')
        self.tristate = -1

    def delete_peaks(self):
        self.peaks        = False
        self.peaks_object = None

    def add_peaks(self, peaks_obj):
        self.peaks        = True
        self.peaks_object = peaks_obj

    def lw(self):
        return self.linewidth

    def color(self):
        return self.color

    def mrkr_size(self):
        return self.marker_size

    def mrkr_face(self):
        return self.marker_face_color

    def mrkr_edge(self):
        return self.marker_edge_color