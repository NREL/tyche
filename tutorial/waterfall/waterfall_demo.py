"""
Minimum working example to run tyche and generate waterfall plot input.
Options are read from a json file that must include:
  data_loc : string or list
    path to data location (likely within tutorial/data/)
  technology_model : string 
    file in src/technology where cost, production, metric functions are defined.
  sample_count : int
  total_amount : float
  max_amount : float
  target_metric : string
  technology (optional) : string
"""
inp_loc = os.path.join("tutorial","waterfall","saf_waterfall.json")

import os
import sys

sys.path.insert(0, os.path.abspath("src"))  # import tyche module
sys.path.insert(0, os.path.abspath(os.path.join("src","technology")))

import json as json
import numpy as np
import pandas as pd
import tyche as ty

# Import technology functions
with open(inp_loc) as f:  args = json.load(f)
if type(args['data_loc'])==list:  args['data_loc'] = os.path.join(*args['data_loc'])
exec('import ' + args['technology_model'])

# Compute investments.
investments = ty.Investments(args['data_loc'])

designs = ty.Designs(args['data_loc'])
designs.compile()

tranche_results = investments.evaluate_tranches(designs, sample_count=args['sample_count'])

summary = tranche_results.summary[
    tranche_results.summary.index.get_level_values('Technology') == args['technology']
] if 'technology' in args.keys() else tranche_results.summary

evaluator = ty.Evaluator(investments.tranches, summary)

optimizer = ty.EpsilonConstraintOptimizer(evaluator)

# Limit the maximum investment amount for each category to the same input value.
max_amount = pd.Series(
    [args['max_amount']] * len(evaluator.categories),
    index = evaluator.categories,
)

# Run optimizer.
optimum = optimizer.maximize_slsqp(
    metric = args['target_metric'],
    total_amount = args['total_amount'],
    max_amount = max_amount,
)

# Define waterfall object and generate output.
w = ty.Waterfall(
  amounts = optimum.amounts,
  evaluator = evaluator,
  data = args['data_loc'],
  metric = args['target_metric'],
)

w.cascade_permutations()