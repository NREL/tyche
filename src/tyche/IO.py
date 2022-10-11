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
    
    # If there are any technologies that DON'T appear in all four
    # datasets, add an error message to the check_list.
    if len(_odd_tech_set) != 0:
      check_list.append(        
        (f'Data Validation: Technology names {_odd_tech_set} are inconsistent. '
        'Check in designs, indices, parameters, and results.')
      )
    
    # Cross-check: Lifetime-Index set in designs dataset must equal the
    # Capital-Index set in indices dataset
    # The set of levels in the Index index level that have the Variable index level Lifetime
    _des_idx = designs.index.to_frame()
    _ind_idx = indices.index.to_frame()
    _odd_cap_set = set(
      _des_idx.Index[_des_idx.Variable == 'Lifetime']
      ).symmetric_difference(
        set(_ind_idx.Index[_ind_idx.Type == 'Capital'])
      )

    if len(_odd_cap_set) != 0:
      check_list.append(
        f'Data Validation: Capital types {_odd_cap_set} are inconsistent. Check in designs and indices.'
      )
    
    # Cross-check: Category-Tranche combinations in investments must be a subset of
    # the Category-Tranche combinations in tranches
    _inv_idx = investments.index.to_frame()
    _tra_idx = tranches.index.to_frame()
    _odd_cattra_set = set(
      [i + '-' + j for i, j in _inv_idx[['Category','Tranche']].values]
    ).symmetric_difference(
      set([i + '-' + j for i, j in _tra_idx[['Category','Tranche']].values])
    )

    if len(_odd_cattra_set) != 0:
      check_list.append(
        (f'Data Validation: Category-Tranche combinations {_odd_cattra_set} are'
        ' inconsistent. Check in investments and tranches.')
      )

    # @TODO Update return values once fully implemented
    if len(check_list) != 0:
      for i in check_list: print(i)
      return False
    else:
      return True

