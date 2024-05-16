import os

from matplotlib.lines import Line2D

from src.exception import CustomException
from src.spectra import Spectrum


def add_spectrum(curve: Line2D) -> tuple[Spectrum, int]:
    """Creates a Spectrum object."""
    try:
        sp = Spectrum(curve)
        sp_id = sp.id
        return sp, sp_id
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
