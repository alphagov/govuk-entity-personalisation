import pandas as pd


def reshape_df(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """
    Reshapes dataframe so it is in a 'nice'/relatively 'tidy' format

    :param df: Dataframe to reshape.
    :param col_name: Name to give the embedding column.
    :return: Reshaped dataframe for easy storing/using.
    """
    try:
        df = df.transpose()
        df[col_name] = df.values.tolist()
        df = df.rename_axis('word').reset_index()
        return df[['word', col_name]]
    except Exception as error:
        print(f"Cause: {error}")
