import os

from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from src.classes.labels import Label
from src.exception import CustomException
from src.spectra import Spectrum

def label_options(label: str) -> tuple[str, str]:
    """Retrieves the x, y label values."""
    x, y = Label.return_value(label)
    return x, y

def get_handles(ax: Axes) -> list[Line2D]:
    handles, _ = ax.get_legend_handles_labels()
    handles = [i for i in handles if not (i.get_label() == "cursor" or i.get_label().startswith("peak_"))]
    return handles

def add_spectrum(curve: Line2D) -> Spectrum:
    """Creates a Spectrum object."""
    try:
        sp = Spectrum(curve)
        return sp
    except Exception as e:
        raise CustomException(e)


def check_path(file: str, title: str) -> str:
    """Checks if file name exist.
    If the name exists it appends a unique number,
    incrementing one at a time.
    """
    path = os.path.join(file, f"{title}.csv")
    counter = 1
    while os.path.exists(path):
        path = os.path.join(file, f"{title}_({str(counter)}).csv")
        counter += 1
    return path
