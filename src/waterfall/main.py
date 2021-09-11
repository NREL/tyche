# # exec(open("src/waterfall/main.py").read())


import os
import sys
import re as re

sys.path.insert(0, os.path.abspath("src"))  # import tyche module
sys.path.insert(0, os.path.abspath(os.path.join("src","technology")))

import json as json
import numpy as np
import pandas as pd
import seaborn as sb
import tyche as ty
import uuid as uuid

from base64 import b64encode
from datetime import datetime
from io import BytesIO
from matplotlib.figure import Figure


def read_args(file, tyche_directory):
    # Read options.
    with open(file) as f:
        args = json.load(f)
    
    args['Order'] = np.array(args['Order'])-1
    args['Index'] = args['target_metric']

    args['data_dir'] = os.path.join(
        tyche_directory,
        *args['data_dir'] if type(args['data_dir'])==list else args['data_dir'],
    )

    # Define the output path for any evaluations made. If this directory does not already
    # exist, create it. Then save the input arguments to this directory.
    args['uuid'] = _uuid(args)
    args['output_dir'] = os.path.join(
        tyche_directory,
        'src', 'waterfall', 'data',
        str(args['uuid']),
    )

    if not os.path.isdir(args['output_dir']): os.mkdir(args['output_dir'])

    # _save_args(args) !!!! not working

    return args


def _save_args(dic, file="args.json"):
    dic = dic.copy()
    dic['Order'] = list(dic['Order']-1)
    dic['uuid'] = str(dic['uuid'])

    # with open(os.path.join(dic['output_dir'], file), 'w') as f:
    #     json.dump(dic, f)
    
    return dic


def add_to(dic, df, key_list=['Index','Technology','Order']):
    for k in key_list: df[k] = dic[k]
    return df


def select_investments(amounts, idx):
    """
    Invest in *only* the given indices. Set all other amounts to zero.

    Parameters
    ----------
    amounts : DataFrame
      Investment amounts
    idx : array
      Integer indices
    """
    return zero_values(amounts, np.setdiff1d(np.arange(0,len(amounts)), idx))


def zero_values(df, idx, column='Amount'):
    """
    Set investment amounts to zero.

    Parameters
    ----------
    df : DataFrame
      Investment amounts
    idx : array
      Integer indices
    column : 'Amount'
      name of column of values to set to zero
    """
    index_names = df.index.names
    df = df.reset_index()
    df.loc[idx,column] = 0
    return df.set_index(index_names)


def evaluate_investment(args, idx):
    """
    Evaluate investments in only the given indices.

    Parameters
    ----------
    amounts : DataFrame
      Investment amounts
    idx : array
      Integer indices for current investment
    directory : string
      Path to IO directory
    """
    amounts = select_investments(args['amounts'], idx)
    print("Evaluating investments:\n")
    print(amounts)

    value = pd.DataFrame(evaluator.evaluate(amounts))
    value.to_csv(_save_as("value", args, idx))
    return value


def increment_investments(args):
    """
    Evaluate investments for the given amounts in the indicated order and save the results.

    Parameters
    ----------
    amounts : DataFrame
      Investment amounts
    order : array
      Integer indices indicating investment order
    directory : string
      Path to IO directory
    """
    order = args['Order']
    N = len(order)

    [evaluate_investment(args, order[:ii]) for ii in np.arange(0,N+1)]
    return None


def _save_as(name, args, idx=''):
    """
    Format path to output value file.

    Parameter
    ---------
    name : string
    args : dict
    directory : string
    """
    if type(idx)==np.ndarray:
        idx = ''.join([str(x) for x in idx+1])
        idx = idx.ljust(len(args['Order']), '0')

    file = '_'.join([x for x in [name, idx] if len(x)>0]) + '.csv'

    print("Saving to: " + args['output_dir'] + "/\n\t" + file + "\n\n")
    return os.path.join(args['output_dir'], file)


def _uuid(args, key_list=['Index','Technology','Order','sample_count','total_amount']):
    id_str = ' '.join([str(args[k]) for k in key_list if k in args.keys()])
    return uuid.uuid3(uuid.NAMESPACE_DNS, id_str)


# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
# tyche_dir = get_dir(r"(.*/tyche)")
tyche_dir = os.path.abspath("")
waterfall_dir = os.path.join(tyche_dir,"src","waterfall")
data_dir = os.path.join(tyche_dir,"tutorial","data")
input_dir = os.path.join(waterfall_dir,"data","_inp")

args = read_args(os.path.join(input_dir,"213.json"), tyche_dir)


# Import technology functions
exec('import ' + args['technology_model'])


# Compute investments.
investments = ty.Investments(args['data_dir'])

designs = ty.Designs(args['data_dir'])
designs.compile()

tranche_results = investments.evaluate_tranches(designs, sample_count=args['sample_count'])

summary = tranche_results.summary[
    tranche_results.summary.index.get_level_values('Technology') == args['Technology']
] if 'Technology' in args.keys() else tranche_results.summary


evaluator = ty.Evaluator(investments.tranches, summary)
metric_list = evaluator.metrics

optimizer = ty.EpsilonConstraintOptimizer(evaluator)


# Run optimizer.
optimum = optimizer.maximize_slsqp(
    metric = args['target_metric'],
    total_amount = args['total_amount'],
)

# Save the optimal investment amounts.
amounts = pd.DataFrame(optimum.amounts)
amounts = add_to(args, amounts)
amounts.to_csv(_save_as("amounts", args))
args['amounts'] = amounts

# Increment investments.
increment_investments(args)