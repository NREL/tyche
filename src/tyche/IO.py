"""
I/O utilities for Tyche.
"""

import os     as os
import pandas as pd

from itertools import groupby

from .DataManager import DesignsDataset, FunctionsDataset, IndicesDataset, InvestmentsDataset, ParametersDataset, ResultsDataset, TranchesDataset


def check_tables(
  path,
  name
  ):
    """
    Perform validity checks on input datasets.

    Parameters
    ----------
    path:str
      Path to directory of datasets
    name:str
      Name of datasets file (XLSX)
    
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
        (f'Data Validation: Capital types {_odd_cap_set} are inconsistent. '
        'Check in designs and indices.')
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

    # Cross-check: Technology-Scenario values in designs must be exactly the
    # set of Technology-Scenario values in parameters
    _par_idx = parameters.index.to_frame()
    _odd_tecsce_set = set(
      [i + '-' + j for i, j in _des_idx[['Technology','Scenario']].values]
    ).symmetric_difference(
      set([i + '-' + j for i, j in _par_idx[['Technology','Scenario']].values])
    )

    if len(_odd_tecsce_set) != 0:
      check_list.append(
        (f'Data Validation: Technology-Scenario combinations {_odd_tecsce_set} are'
        ' inconsistent. Check in designs and parameters.')
      )

    # Designs check: Variable index levels are exactly Input, Input efficiency,
    # Input price, Lifetime, Output efficiency, Output price, Scale
    # Check if something's in designs Variable index levels that shouldn't be
    _des_var_set = set(
      i for i in designs.index.get_level_values('Variable')
      ).difference(
        set(
          ['Input', 'Input efficiency', 'Input price',
          'Lifetime', 'Output efficiency', 'Output price', 'Scale']
        )
      )

    if len(_des_var_set) != 0:
      check_list.append(
        (f'Data Validation: Variable column in designs has unexpected '
        f'value(s) {_des_var_set}')
      )

    # Designs check: Every Technology-Scenario combination must have
    # all mandatory Variables
    # Get a list of all Technology-Scenario combinations in Designs
    _des_tecsce = list(set([i[:2] for i in designs.index.values]))


    # Designs check: Every Technology-Scenario combination must have
    # the same Index levels within each mandatory Variable
    # Get the set (no duplicates) of all Variable-Value combinations across all Tech-Sce combinations
    _var_val_set = set([i[2:] for i in designs.index.values])
    for _j in _des_tecsce:
      _des_tecsce_varval_set = set([i[2:] for i in designs.index.values if i[:2] == _j])
      # Check if the Tech-Scen combo is missing any Variable Values
      _odd_des_tecsce_varval_set = _var_val_set.difference(
        _des_tecsce_varval_set
      )
      if len(_odd_des_tecsce_varval_set) != 0:
        check_list.append(
          (f'Data Validation: Technology-Scenario combination {_j} has'
          f' missing Variable values: {_odd_des_tecsce_varval_set}. Check in designs.')
        )

    # @TODO Update return values once fully implemented
    if len(check_list) != 0:
      for i in check_list: print(i)
      return False
    else:
      return True

