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


def read_table(path, name, dtypes, index):
  """
  Read a data table from a file.

  Parameters
  ----------
  path : str
    The path to the folder.
  name : str
    The filename for the table.
  dtypes : array
    The column types.
  index : array
    The index.
  """

  return pd.read_csv(
    os.path.join(path, name),
    sep="\t",
    index_col=index, converters=dtypes
  ).sort_index()
