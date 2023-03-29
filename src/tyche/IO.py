"""
I/O utilities for Tyche.
"""

import os     as os
import importlib as il

from inspect import getmembers, isfunction
from numpy import arange

from .DataManager import DesignsDataset, FunctionsDataset, IndicesDataset, InvestmentsDataset, ParametersDataset, ResultsDataset, TranchesDataset


def check_tables(
  path,
  name
  ):
    """
    Perform validity checks on input datasets.

    All checks are run before this method terminates; that is, data errors are found
    all at once rather than one at a time from several calls to this method. A list of
    errors found is printed if any check fails. The errors include a summary of the check
    and identify the dataset that needs to be changed.

    Parameters
    ----------
    path:str
      Path to directory of datasets
    name:str
      Name of datasets file (XLSX)
    
    Returns
    -------
    Boolean: True if data is valid, False otherwise
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
        ('Data Validation: Technology names are inconsistent. Check in '
        f'designs, indices, parameters, and results.\n{_odd_tech_set}\n')
      )
    
    # Cross-check: Lifetime-Index set in designs dataset must equal the
    # Capital-Index set in indices dataset
    # The set of levels in the Index index level that have the Variable 
    # index level Lifetime
    _des_idx = designs.index.to_frame()
    _ind_idx = indices.index.to_frame()
    _odd_cap_set = set(
      _des_idx.Index[_des_idx.Variable == 'Lifetime']
      ).symmetric_difference(
        set(_ind_idx.Index[_ind_idx.Type == 'Capital'])
      )
    if len(_odd_cap_set) != 0:
      check_list.append(
        ('Data Validation: Capital types are inconsistent. Check in designs'
        f' and indices.\n{_odd_cap_set}\n')
      )
    
    # Cross-check: Category-Tranche combinations in investments must be a subset of
    # the Category-Tranche combinations in tranches
    _inv_idx = investments.index.to_frame()
    _tra_idx = tranches.index.to_frame()
    _odd_cattra_set = set(
      [i + '-' + j for i, j in _inv_idx[['Category','Tranche']].values]
    ).difference(
      set([i + '-' + j for i, j in _tra_idx[['Category','Tranche']].values])
    )
    if len(_odd_cattra_set) != 0:
      check_list.append(
        ('Data Validation: Category-Tranche combinations are inconsistent. Check '
        f'in investments and tranches.\n{_odd_cattra_set}\n')
      )

    # Cross-check: Technology-Tranche values in designs must be exactly the
    # set of Technology-Tranche values in parameters
    _par_idx = parameters.index.to_frame()
    _odd_tectra_set = set(
      [i + '-' + j for i, j in _des_idx[['Technology','Tranche']].values]
    ).symmetric_difference(
      set([i + '-' + j for i, j in _par_idx[['Technology','Tranche']].values])
    )

    if len(_odd_tectra_set) != 0:
      check_list.append(
        ('Data Validation: Technology-Tranche combinations are inconsistent. '
        f'Check in designs and parameters.\n{_odd_tectra_set}\n')
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
        ('Data Validation: Variable column in designs has unexpected '
        f'value(s).\n{_des_var_set}\n')
      )

    # Designs check: Every Technology-Tranche combination must have
    # the same Index levels within each mandatory Variable
    # Designs check: Every Technology-Tranche combination must have
    # all mandatory Variables
    # Get a list of all Technology-Tranche combinations in Designs
    _des_tectra = list(set([i[:2] for i in designs.index.values]))    
    # Get the set (no duplicates) of all Variable-Value combinations across 
    # all Tech-Tra combinations
    _var_val_set = set([i[2:] for i in designs.index.values])
    for _j in _des_tectra:
      _des_tectra_var_set = set([i[2] for i in designs.index.values if i[:2] == _j])
      _des_tectra_varval_set = set([i[2:] for i in designs.index.values if i[:2] == _j])
      # Check if the Tech-Tranche combo is missing any mandatory Variables
      _odd_des_tectra_var_set = set(
        ['Input', 'Input efficiency', 'Input price',
        'Lifetime', 'Output efficiency', 'Output price', 'Scale']
        ).difference(
          _des_tectra_var_set
        )
      # Check if the Tech-Tranche combo is missing any Variable Indexes
      _odd_des_tectra_varval_set = _var_val_set.difference(
        _des_tectra_varval_set
      )
      if len(_odd_des_tectra_var_set) != 0:
        check_list.append(
          (f'Data Validation: Technology-Tranche combination {_j} has '
          f'missing mandatory Variables. Check in designs.\n{_odd_des_tectra_var_set}\n')
        )
      if len(_odd_des_tectra_varval_set) != 0:
        check_list.append(
          (f'Data Validation: Technology-Tranche combination {_j} has'
          f' missing Variable Indexes. Check in designs.\n{_odd_des_tectra_varval_set}\n')
        )

    # Functions check: All unique entries under Model must be a .py file containing the
    # methods defined in the Capital, Fixed, Production, and Metrics columns
    # For every technology model,
    for _tech, _meta in functions.iterrows():
      # First check that the model exists as a .py file in the correct location
      if os.path.exists('../' + _meta['Model'] + '.py'):
        # If the file does exist, use a try/except structure to attempt import
        try:
          _model = il.import_module("." + _meta["Model"], package="technology")
        except ImportError:
          check_list.append(
            (f'Data Validation: Technology model {_tech} is not importable.\n')
          )
        # If the model imported successfully, compare the set of methods
        # within the model to the set of methods named in the Functions dataset
        # The set of methods within the model must contain all elements of the set of
        # methods named in the Functions dataset, BUT can also contain additional methods
        _odd_model_funs = set(_meta[2:-1].values).difference(
          set(
            [f[0] for f in getmembers(_model, isfunction)]
          )
        )
        # If the two sets of method names don't match, append to check_list
        if len(_odd_model_funs) != 0:
          check_list.append(
            (f'Data Validation: Technology model {_tech} has inconsistent methods. '
            f'Revise the Functions dataset or the {_tech} model (.py).\n{_odd_model_funs}\n')
          )
      # If the file does not exist, add the missing file to check_list and exit the loop
      else:
        check_list.append(
          (f'Data Validation: Technology model {_tech} (.py) does not exist in '
          'the technology directory.\n')
        )
    
    # Indices check: Type column contains exactly Capital, Input, Output, Metric
    _ind_type_odd = set(
      [i[1] for i in indices.index.values]
      ).symmetric_difference(
        set(
          ['Capital', 'Input', 'Output', 'Metric']
        )
      )
    if len(_ind_type_odd) != 0:
      check_list.append(
        (f'Data Validation: Type column in Indices is missing values or '
        f'has unexpected values.\n{_ind_type_odd}\n')
      )
    
    # Indices check: Offset values within each Type must be sequential integers
    # beginning at zero.
    # Step 1: Check that all Offset values are integers using column dtype
    if indices.Offset.dtype != 'int':
      check_list.append(
        (f'Data validation: Offset values in Indices must be integers.\n')
      )
    else:
      # Step 2: If all Offsets are integers, check for sequential values
      _ind_val = indices.Offset.reset_index()
      _ind_val_odd = []
      for _y in _ind_val.Technology.unique():
        _ind_val_odd.append([
          set(
            arange(len(_ind_val.Index[(_ind_val.Technology==_y) & (_ind_val.Type==_t)]))
          ).symmetric_difference(
            set(_ind_val.Offset[(_ind_val.Technology==_y) & (_ind_val.Type==_t)])
          ) for _t in ['Capital', 'Input', 'Output', 'Metric']
        ])
      _ind_val_odd_flat = [item for sublist in _ind_val_odd for item in sublist]

      if any([len(i) for i in _ind_val_odd_flat]) != 0:
        check_list.append(
          (f'Data Validation: Check that Offset values in Indices are '
          'sequential integers beginning at zero, within each Type.\n')
        )

    # Cross-check: The Index values for Output Type in the indices dataset, 
    # the Index values for Output Variable in results, and the Output 
    # efficiency (and Output price) Variable values in designs must be identical.
    _out_val_odd = [
      set(
        [i[2] for i in indices.index.values if i[1] == 'Output']
      ).symmetric_difference(
        set(
          [j[2] for j in results.index.values if j[1] == 'Output']
        )
      ),
        set(
          [j[2] for j in results.index.values if j[1] == 'Output']
        ).symmetric_difference(
          set(
            [k[3] for k in designs.index.values if k[2] in {'Output price','Output efficiency'}]
          )
        )
    ]

    if any([len(i) for i in _out_val_odd]) != 0:
      check_list.append(
        (f'Data Validation: Output Index values {_out_val_odd} are inconsistent in one of '
        f'indices, results, and designs.\n')
      )

    # Cross-check: The index values for Input Type in the indices dataset must match 
    # the Index values for Input, Input price, and Input efficiency Variable in designs.
    _inp_val_odd = set(
        [i[2] for i in indices.index.values if i[1] == 'Input']
      ).symmetric_difference(
        set(
          [j[3] for j in designs.index.values if j[2] in {'Input', 'Input price', 'Input efficiency'}]
        )
      )
    
    if len(_inp_val_odd) != 0:
      check_list.append(
        (f'Data Validation: Input Index values {_inp_val_odd} are inconsistent in either '
        'indices or in designs.\n')
      )

    # Parameters check: Offset values within every Tech-Tranche combo must be 
    # sequential integers beginning at zero
    # Step 1: Check that all Offset values are integers using column dtype
    if parameters.Offset.dtype != 'int':
      check_list.append(
        (f'Data validation: Offset values in Parameters must be integers.\n')
      )
    else:
      # Step 2: If all Offsets are integers, check for sequential values
      _par_off_val = parameters.Offset.reset_index()
      _par_off_val_odd = list()
      for _t in _par_off_val.Technology.unique().tolist():
        for _r in _par_off_val.Tranche.unique().tolist():
          _par_off_val_odd = _par_off_val_odd + \
            [set(
              arange(len(_par_off_val.Offset[(_par_off_val.Technology==_t) & (_par_off_val.Tranche==_r)]))
              ).symmetric_difference(
                set(
                  _par_off_val.Offset[(_par_off_val.Technology==_t) & (_par_off_val.Tranche ==_r)]
                )
              )
            ]
    if any([len(i) for i in _par_off_val_odd]) != 0:
      check_list.append(
        ('Data Validation: Check that Offset values in Parameters are '
        'sequential integers beginning at zero, within each Technology-Tranche '
        'combination.\n')
      )           

    # Parameters check: Every Parameter Offset must be the same across 
    # all Technology-Tranche combinations
    # Get a list of all Technology-Tranche combinations in Parameters
    parameters.sort_index(inplace=True)
    _par_tectra_paroff = [
      parameters.loc[i,'Offset'] for i in list(
        set([j[:2] for j in parameters.index.values])
      )
    ]
    for _j in arange(len(_par_tectra_paroff)):
      if _j < len(_par_tectra_paroff)-1:
        if not _par_tectra_paroff[_j].equals(_par_tectra_paroff[_j+1]):
          check_list.append(
            ('Data Validation: Parameter Offsets are inconsistent. Check '
            f'in Parameters.\n{_par_tectra_paroff[_j]}\n')
          )
    
    # Results check: Every Technology must have a result where both the Variable
    # and the Index are "Cost".
    for _i in results.index.to_frame().Technology.unique():
      if len([j[1:] for j in results.index if (j[1:] == ('Cost','Cost')) & (j[0] == _i)]) != 1:
        check_list.append(
          (f'Data Validation: Technology {_i} in Results needs a row where both '
          'the Variable and the Index are "Cost".\n')
        )

    # Tranches check: Within every Category, the Amounts for each Tranche must be unique
    _tra_amt_unique = [
      tranches.reset_index().groupby('Category').Amount.count()[i] != tranches.reset_index().groupby('Category').Amount.nunique()[i] 
      for i in arange(tranches.index.to_frame().Category.nunique())
    ]
    if any(_tra_amt_unique):
      check_list.append(
        (f'Data Validation: Category {tranches.index.to_frame().Category.unique()[_tra_amt_unique][0]}'
        ' in Tranches has duplicate Amounts.\n')
      )

    # Cross-check: Metric Index values are identical in results and in indices
    _met_odd_val = set(
      [i[2] for i in indices.index.values if i[1] == 'Metric']
      ).symmetric_difference(
        set(
          [j[2] for j in results.index.values if j[1] == 'Metric']
        )
      )
    
    if len(_met_odd_val) != 0:
      check_list.append(
        (f'Data Validation: Metric Index values {_met_odd_val} are inconsistent either '
        'in results or in indices.\n')
      )

    if len(check_list) != 0:
      for i in check_list: print(i)
      return False
    else:
      return True

