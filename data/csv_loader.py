import pandas as pd
from io import BytesIO


def load_csv(file) -> pd.DataFrame:
    if hasattr(file, "read"):
        return pd.read_csv(file)
    return pd.read_csv(file)
