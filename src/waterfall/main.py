# # exec(open("src/waterfall/main.py").read())

# !!!! to-do: define a function that will do the whole thing, given:
#   - path to tyche directory
#   - path to io directory
#   - id of current simulation



def get_dir(regex):
    return re.match(regex, os.getcwd()).group(1)


def read_args(file, tyche_directory):
    # Read options.
    # with open(os.path.join(io_dir,"inp.json")) as f:
    with open(file) as f:
        args = json.load(f)

    args['permutation'] = np.array(args['permutation'])-1
    args['Index'] = args['target_metric']
    args['loc'] = os.path.join(
        tyche_directory,
        *args['loc'] if type(args['loc'])==list else args['loc'],
    )
    return args


def add_to(dic, df):
    df['Index'] = dic['Index']
    df['Technology'] = dic['Technology']
    df['Permutation'] = dic['permutation']
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
    return zero_investments(amounts, np.setdiff1d(np.arange(0,len(amounts)), idx))


def zero_investments(amounts, idx):
    """
    Set investment amounts to zero.

    Parameters
    ----------
    amounts : DataFrame
      Investment amounts
    idx : array
      Integer indices
    """
    index_names = amounts.index.names
    amounts = amounts.reset_index()
    amounts.loc[idx,'Amount'] = 0
    return amounts.set_index(index_names)


def evaluate_investment(amounts, idx, directory):
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
    amounts = select_investments(amounts, idx)
    print("Evaluating investments:\n")
    print(amounts)

    value = pd.DataFrame(evaluator.evaluate(amounts))
    value.to_csv(_save_values(idx, directory))
    return value


def increment_investments(amounts, order, directory):
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
    N = len(amounts)
    [evaluate_investment(amounts, order[:ii], directory) for ii in np.arange(0,N+1)]
    return None


def _save_values(idx, directory):
    """
    Format path to output value file.

    Parameter
    ---------
    idx : array
      integer indices
    """
    idx = ''.join([str(x) for x in idx]) if len(idx) > 0 else 'none'
    path = os.path.join(directory,'values-' + idx + '.csv')
    print("Saving to: " + path + "\n\n")
    return path


import os
import sys
import re as re

tyche_dir = get_dir(r"(.*/tyche)")
waterfall_dir = os.path.join(tyche_dir,"src","waterfall")
data_dir = os.path.join(tyche_dir,"tutorial","data")
io_dir = os.path.join(waterfall_dir,"data","213")

sys.path.insert(0, os.path.join(tyche_dir,"src"))  # import tyche module
sys.path.insert(0, os.path.join(tyche_dir,"src","technology"))

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


# !!!! to-do: define a function that will do the whole thing, given:
#   - path to tyche directory
#   - path to io directory
#   - id of current simulation


args = read_args(os.path.join(io_dir,"inp.json"), tyche_dir)


# Import technology functions
exec('import ' + args['technology_model'])


# Compute investments.
investments = ty.Investments(args['loc'])

designs = ty.Designs(args['loc'])
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
amounts.to_csv(os.path.join(io_dir,"amounts.csv"))


# Increment investments.
increment_investments(amounts, args['permutation'], io_dir)