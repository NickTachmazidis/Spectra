"""Canvas class for the main app."""

import seaborn as sns
from matplotlib.backend_bases import LocationEvent
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from PyQt5 import QtCore

# Set style for plotting
sns.set_style(
    "darkgrid",
    {
        "xtick.color": "#999999",
        "ytick.color": "#999999",
        "xtick.labelsize": 0.5,
        "ytick.labelsize": 0.5,
        "font.family": "serif",
        "axes.grid": True,
    },
)


class Canvas(FigureCanvasQTAgg):
    """Canvas class for the main app."""

    def __init__(self, parent=None, width=5, height=5, dpi=160) -> None:
        """Initialize the figure and the axes."""
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(Canvas, self).__init__(self.fig)

        def onframe(event: LocationEvent) -> None:
            """Make the cursor invisible."""
            self.setCursor(QtCore.Qt.BlankCursor)

        self.fig.canvas.mpl_connect("figure_enter_event", onframe)

        # Adjust canvas size
        self.fig.subplots_adjust(
            top=0.941, bottom=0.096, left=0.043, right=0.99, hspace=0.2, wspace=0.2
        )

        self.resize_canvas()

    def resize_canvas(self) -> None:
        """Adjust the canvas size."""
        width, height = self.size().width(), self.size().height()
        self.fig.set_size_inches(width / self.fig.dpi, height / self.fig.dpi)
        self.fig.tight_layout(pad=1)
        self.draw()

    def resizeEvent(self, event) -> None:
        """Handle resize event to adjust canvas."""
        super(Canvas, self).resizeEvent(event)
        self.resize_canvas()