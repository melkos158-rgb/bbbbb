import pandas as pd

def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna()
    return df
