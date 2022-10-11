"""
I/O utilities for Tyche.
"""

import os     as os
import pandas as pd

from .DataManager import DesignsDataset, FunctionsDataset, IndicesDataset, InvestmentsDataset, ParametersDataset, ResultsDataset, TranchesDataset


def check_tables(
  path,
  name
  ):
    """
    Perform validity checks on input datasets.

    Parameters
    ----------
    path
    name

    Returns
    -------
    Boolean: True if data is valid, False otherwise

    Raises
    ------
    Exceptions TBD when the data fails checks
    """
    check_list = []

    # Get the datasets as distinct DataFrames.
    # The DataManager performs column name checks and enforces data types.
    indices     = IndicesDataset(    os.path.join(path, name))
    functions   = FunctionsDataset(  os.path.join(path, name))
    designs     = DesignsDataset(    os.path.join(path, name))
    parameters  = ParametersDataset( os.path.join(path, name))
    results     = ResultsDataset(    os.path.join(path, name))
    tranches    = TranchesDataset(   os.path.join(path, name))
    investments = InvestmentsDataset(os.path.join(path, name))

    # Cross-check: Identical sets of Technology across designs, indices,
    # parameters, and results datasets
    _odd_tech_set = set(designs.index.get_level_values('Technology')
      ).symmetric_difference(
        set(indices.index.get_level_values('Technology'))
      ).symmetric_difference(
        set(parameters.index.get_level_values('Technology'))
      ).symmetric_difference(
        set(results.index.get_level_values('Technology'))
      )
    
    # If the set of technologies that DOESN'T appear in all four datasets
    # is not empty, add an error message to the check_list
    if len(_odd_tech_set) != 0:
      check_list.append(        
        f'Data Checks: Technology names {_odd_tech_set} are inconsistent.'
        )
    
    # Cross-check: Lifetime-Index set in designs dataset must equal the
    # Capital-Index set in indices dataset

    # @TODO Update return values once fully implemented
    if len(check_list) != 0:
      for i in check_list: print(i + '\n')
      return False
    else:
      return True

