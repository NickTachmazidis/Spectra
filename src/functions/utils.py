import os

from PyQt5.QtWidgets import QFileDialog

import pandas as pd
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from src.classes.labels import Label
from src.exceptions.exception import CustomException
from src.classes.spectra import Spectrum

def save_as(curves: dict, sep: str) -> None:
    try:
        dfs = []
        for i in curves.values():
            if i.tristate == 1:
                title = i.label
                df = pd.DataFrame({"x": i.x_data, "y": i.y_data})
                if i.peaks:
                    df["peaks_x"] = pd.Series(i.peaks_object.get_xdata())
                    df["peaks_y"] = pd.Series(i.peaks_object.get_ydata())
            dfs.append((title, df))

        direc = str(
            QFileDialog.getExistingDirectory(None, "Select Directory")
        )

        sep = "," if sep is None or len(sep) > 1 else sep

        if direc:
            for df in dfs:
                path = check_path(direc, df[0])
                df[1].to_csv(path, sep=sep, index=False)

    except Exception as e:
        raise CustomException(e)


def get_file(path: str) -> str:
    """Popup dialog for file loading."""
    try:
        input_file = QFileDialog.getOpenFileName(
            parent=None,
            caption="Choose files",
            directory=path,
            filter="Data file (*.csv)",
        )[0]
        return input_file
    except Exception as e:
        raise CustomException(e)

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
