"""Generic proccessing functions used in the GUI app."""

from matplotlib.lines import Line2D
import pandas as pd

from ..exceptions.exception import CustomException

def csv_to_dataframe(
    input_file: str,
    sep: str,
    engine: str
    ) -> tuple[pd.DataFrame, str]:
    """Converts the CSV file to a pd.DataFrame object."""
    try:
        label = input_file.split("/")[-1].replace(".csv", "")
        df = pd.read_csv(input_file, sep=sep, engine=engine, dtype="float")
        return df, label
    except Exception as e:
        raise CustomException(e)
