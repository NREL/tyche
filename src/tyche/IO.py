import os     as os
import pandas as pd


def make_table(dtypes, index):
    return pd.DataFrame(
        {k: [v()] for k, v in dtypes.items()},
        index=index
    ).iloc[0:0]


def read_table(path, name, dtypes, index):
    return pd.read_csv(
        os.path.join(path, name),
        sep="\t",
        index_col=index, converters=dtypes
    ).sort_index()
