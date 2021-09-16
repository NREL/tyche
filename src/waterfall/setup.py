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
    # args['uuid'] = _uuid(args)
    # args['output_dir'] = os.path.join(
    #     tyche_directory,
    #     'src', 'waterfall', 'data',
    #     str(args['uuid']),
    # )

    # if not os.path.isdir(args['output_dir']): os.mkdir(args['output_dir'])

    # _save_args(args) !!!! not working

    return args


tyche_dir = os.path.abspath("")
waterfall_dir = os.path.join(tyche_dir,"src","waterfall")
data_dir = os.path.join(tyche_dir,"tutorial","data")
input_dir = os.path.join(waterfall_dir,"data","_inp")

args = read_args(os.path.join(input_dir,"saf_camelina_mjsp_213.json"), tyche_dir)


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