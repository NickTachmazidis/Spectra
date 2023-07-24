from PyQt5 import QtCore 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import seaborn as sns

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