"""
I/O utilities for Tyche.
"""

import os     as os
import pandas as pd


def make_table(dtypes, index):
  """
  Make a data frame from column types and an index.

  Parameters
  ----------
  dtypes : array
    The column types.
  index : array
    The index.
  """

  return pd.DataFrame(
    {k: [v()] for k, v in dtypes.items()},
    index=index
  ).iloc[0:0]


def read_table(path, name, sheet, dtypes, index):
  """
  Read a data table from a sheet in an Excel file.

  Parameters
  ----------
  path : str
    The path to the folder.
  name : str
    The filename for the datasets.
  sheet : str
    The sheet name to read.
  dtypes : array
    The column types.
  index : array
    The index.
  """

  return pd.read_excel(
    os.path.join(path, name),
    sheet_name=sheet,
    converters=dtypes
    ).set_index(
        keys=index
    ).sort_index()
