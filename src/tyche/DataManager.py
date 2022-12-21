#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on October 10 2022.

Uses code from Feedstock Production Emissions to Air Model (FPEAM) Copyright
(c) 2018 Alliance for Sustainable Energy, LLC; Noah Fisher.
Builds on functionality in the FPEAM's Data.py.
Unmodified FPEAM code is available at https://github.com/NREL/fpeam.

@author: rhanes
"""
import sys
import pandas as pd


class Data(pd.DataFrame):
  """
  Data representation.

  Specific datasets are created as child classes with
  defined column names, data types, and backfilling values. Creating child
  classes removes the need to define column names etc when the classes are
  called to read data from files.
  """

  COLUMNS = []

  INDEX_COLUMNS = []

  def __init__(
    self,
    fpath,
    columns,
    index_columns,
    sheet,
    backfill = False,
  ):
    """
    Store file IO information into self.

    Parameters
    ----------
    fpath
        Filepath location of data to be read in

    columns
        List of columns to backfill
    
    index_columns
      List of column indexes to use as row labels

    sheet
        Name of sheet to read in

    backfill
        Boolean flag: perform backfilling with datatype-specific value
    """
    _df = (
      pd.DataFrame({})
      if fpath is None
      else self.load(fpath=fpath, columns=columns, index_columns = index_columns, sheet=sheet)
    )

    super().__init__(data=_df)

    self.source = fpath

    _valid = self.validate()

    try:
      assert _valid is True
    except AssertionError:
      if fpath is not None:
        print(f"{__name__} failed validation")
        raise

    if backfill:
      for _column in self.COLUMNS:
        if _column["backfill"] is not None:
          self.backfill(column=_column["name"], value=_column["backfill"])

  @staticmethod
  def load(fpath, columns, index_columns=None, header=0, sheet=None):
    """
    Load data from a text file at <fpath>. Check and set column names.

    See pandas.read_table() help for additional arguments.

    Parameters
    ----------
    fpath: [string]
        file path to CSV file or SQLite database file

    columns: [dict]
        {name: type, ...}

    header: [int]
        0-based row index containing column names

    sheet: [str]
        Specify the name of the sheet to be read in.
        If no sheet name is provided, the first sheet is read.

    Returns
    -------
    DataFrame
    """
    try:
      _df = pd.read_excel(
        io = fpath,
        sheet_name = sheet,
        dtype = columns,
        usecols = columns.keys(),
        index_col = index_columns,
        header = header,
      )
    except ValueError as _e:
      print(f"DataManager: Unexpected column(s) found in {fpath}, {sheet}")
      raise _e

    else:
      return _df

  def backfill(self, column, value=0):
    """
    Replace NaNs in <column> with <value>.

    Parameters
    ----------
    column: [string]
        Name of column with NaNs to be backfilled

    value: [any]
        Value for backfill

    Returns
    -------
    DataFrame with [column] backfilled with [value]
    """
    _dataset = str(type(self)).split("'")[1]

    if not value:
      print(f"DataManager: No backfill value provided for {column}")
      sys.exit(1)

    if isinstance(column, str):
      if self[column].isna().any():
        # count the missing values
        _count_missing = sum(self[column].isna())
        # count the total values
        _count_total = self[column].__len__()

        # fill the missing values with specified value
        self[column].fillna(value, inplace=True)

        # log a warning with the number of missing values
        print(
          f"{_count_missing} of {_count_total} data values in"
          f" {_dataset}.{column} were backfilled as {value}"
        )

    elif isinstance(column, list):
      # if any values are missing,
      for _c in column:
        if self[_c].isna().any():
          # count the missing values
          _count_missing = sum(self[_c].isna())
          # count the total values
          _count_total = self[_c].__len__()

          # fill the missing values with specified value
          self[_c].fillna(value, inplace=True)

          # log a warning with the number of missing values
          print(
            f"{_count_missing} of {_count_total} data values in"
            f" {_dataset}.{_c} were backfilled as {value}"
          )

    return self

  def validate(self):
    """
    Check that data are not empty.

    Return False if empty and True otherwise.

    Returns
    -------
    Boolean flag
    """
    _name = type(self).__name__

    _valid = True

    if self.empty:
      print(f"DataManager: No data provided for {_name}")
      _valid = False

    return _valid

  def __enter__(self):
    """Return self."""
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    """Process exceptions."""
    if exc_type is not None:
      print(f"{exc_type}\n{exc_val}\n{exc_tb}")
      _out = False
    else:
      _out = self

    return _out


class DesignsDataset(Data):
  """
  Read in and process the designs dataset.
  """

  COLUMNS = (
    {"name": "Technology", "type": str, "index": True,  "backfill": None},
    {"name": "Scenario"  , "type": str, "index": True,  "backfill": None},
    {"name": "Variable"  , "type": str, "index": True,  "backfill": None},
    {"name": "Index"     , "type": str, "index": True,  "backfill": None},
    {"name": "Value"     , "type": str, "index": False, "backfill": None},
    {"name": "Units"     , "type": str, "index": False, "backfill": None},
    {"name": "Notes"     , "type": str, "index": False, "backfill": None}
  )

  INDEX_COLUMNS = [0, 1, 2, 3]

  def __init__(
    self,
    fpath = None,
    columns = {d["name"]: d["type"] for d in COLUMNS},
    index_columns = INDEX_COLUMNS,
    sheet = "designs",
    backfill = False,
  ):
    """Initialize designs data frame."""
    super().__init__(
      fpath = fpath,
      columns = columns,
      index_columns = index_columns,
      sheet = sheet,
      backfill = backfill,
    )


class FunctionsDataset(Data):
  """
  Read in and process the functions dataset.
  """

  COLUMNS = (
    {"name": "Technology", "type": str, "index": True,  "backfill": None},
    {"name": "Style"     , "type": str, "index": False, "backfill": None},
    {"name": "Model"     , "type": str, "index": False, "backfill": None},
    {"name": "Capital"   , "type": str, "index": False, "backfill": None},
    {"name": "Fixed"     , "type": str, "index": False, "backfill": None},
    {"name": "Production", "type": str, "index": False, "backfill": None},
    {"name": "Metrics"   , "type": str, "index": False, "backfill": None},
    {"name": "Notes"     , "type": str, "index": False, "backfill": None}
  )

  INDEX_COLUMNS = [0]

  def __init__(
    self,
    fpath = None,
    columns = {d["name"]: d["type"] for d in COLUMNS},
    index_columns = INDEX_COLUMNS,
    sheet = "functions",
    backfill = False,
  ):
    """Initialize functions data frame."""
    super().__init__(
      fpath = fpath,
      columns = columns,
      index_columns = index_columns,
      sheet = sheet,
      backfill = backfill,
    )


class IndicesDataset(Data):
  """
  Read in and process the indices dataset.
  """

  COLUMNS = (
    {"name": "Technology" , "type": str, "index": True,  "backfill": None},
    {"name": "Type"       , "type": str, "index": True,  "backfill": None},
    {"name": "Index"      , "type": str, "index": True,  "backfill": None},
    {"name": "Offset"     , "type": int, "index": False, "backfill": None},
    {"name": "Description", "type": str, "index": False, "backfill": None},
    {"name": "Notes"      , "type": str, "index": False, "backfill": None}
  )

  INDEX_COLUMNS = [0, 1, 2]

  def __init__(
    self,
    fpath,
    columns = {d["name"]: d["type"] for d in COLUMNS},
    index_columns = INDEX_COLUMNS,
    sheet = "indices",
    backfill = False,
  ):
    """Initialize indices data frame."""
    super().__init__(
      fpath = fpath,
      columns = columns,
      index_columns = index_columns,
      sheet = sheet,
      backfill = backfill,
    )


class InvestmentsDataset(Data):
  """
  Read in and process the investments dataset.
  """

  COLUMNS = (
    {"name": "Investment", "type": str, "index": True,  "backfill": None},
    {"name": "Category"  , "type": str, "index": True,  "backfill": None},
    {"name": "Tranche"   , "type": str, "index": True,  "backfill": None},
    {"name": "Notes"     , "type": str, "index": False, "backfill": None},
  )

  INDEX_COLUMNS = [0, 1, 2]

  def __init__(
    self,
    fpath = None,
    columns = {d["name"]: d["type"] for d in COLUMNS},
    index_columns = INDEX_COLUMNS,
    sheet = "investments",
    backfill = False,
  ):
    """Initialize investments data frame."""
    super().__init__(
      fpath = fpath,
      columns = columns,
      index_columns = index_columns,
      sheet = sheet,
      backfill = backfill,
    )


class ParametersDataset(Data):
  """
  Read in and process the parameters dataset.
  """

  COLUMNS = (
    {"name": "Technology", "type": str, "index": True,  "backfill": None},
    {"name": "Scenario"  , "type": str, "index": True,  "backfill": None},
    {"name": "Parameter" , "type": str, "index": True,  "backfill": None},
    {"name": "Offset"    , "type": int, "index": False, "backfill": None},
    {"name": "Value"     , "type": str, "index": False, "backfill": None},
    {"name": "Units"     , "type": str, "index": False, "backfill": None},
    {"name": "Notes"     , "type": str, "index": False, "backfill": None}
  )

  INDEX_COLUMNS = [0, 1, 2]

  def __init__(
    self,
    fpath = None,
    columns = {d["name"]: d["type"] for d in COLUMNS},
    index_columns = INDEX_COLUMNS,
    sheet = "parameters",
    backfill = False,
  ):
    """Initialize parameters data frame."""
    super().__init__(
      fpath = fpath,
      columns = columns,
      index_columns = index_columns,
      sheet = sheet,
      backfill = backfill,
    )


class ResultsDataset(Data):
  """
  Read in and process the results dataset.
  """

  COLUMNS = (
    {"name": "Technology", "type": str, "index": True,  "backfill": None},
    {"name": "Variable"  , "type": str, "index": True,  "backfill": None},
    {"name": "Index"     , "type": str, "index": True,  "backfill": None},
    {"name": "Units"     , "type": str, "index": False, "backfill": None},
    {"name": "Notes"     , "type": str, "index": False, "backfill": None}
  )

  INDEX_COLUMNS = [0, 1, 2]

  def __init__(
    self,
    fpath = None,
    columns = {d["name"]: d["type"] for d in COLUMNS},
    index_columns = INDEX_COLUMNS,
    sheet = "results",
    backfill = False,
  ):
    """Initialize results data frame."""
    super().__init__(
      fpath = fpath,
      columns = columns,
      index_columns = index_columns,
      sheet = sheet,
      backfill = backfill,
    )


class TranchesDataset(Data):
  """
  Read in and process the tranches dataset.
  """

  COLUMNS = (
    {"name": "Category", "type": str, "index": True,  "backfill": None},
    {"name": "Tranche" , "type": str, "index": True,  "backfill": None},
    {"name": "Scenario", "type": str, "index": True,  "backfill": None},
    {"name": "Amount"  , "type": str, "index": False, "backfill": None},
    {"name": "Notes"   , "type": str, "index": False, "backfill": None}
  )

  INDEX_COLUMNS = [0, 1, 2]

  def __init__(
    self,
    fpath = None,
    columns = {d["name"]: d["type"] for d in COLUMNS},
    index_columns = INDEX_COLUMNS,
    sheet = "tranches",
    backfill = False,
  ):
    """Initialize tranches data frame."""
    super().__init__(
      fpath = fpath,
      columns = columns,
      index_columns = index_columns,
      sheet = sheet,
      backfill = backfill,
    )