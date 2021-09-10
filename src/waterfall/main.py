print('Hello World!')

import os
import sys

tyche_dir = os.path.abspath("../..")
data_dir = os.path.join(tyche_dir,"tutorial","data")

sys.path.insert(0, os.path.join(tyche_dir,"src"))  # import tyche module
sys.path.insert(0, os.path.join(tyche_dir,"src","technology"))  # import technology functions

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

import saf_v1

# Define inputs.
loc = os.path.join(data_dir,"saf")
target_metric = ["Reduction in MJSP", "Reduction in Jet GHG"][0]
total_amount = 5000000

# Compute investments.
investments = ty.Investments(loc)

designs = ty.Designs(loc)
designs.compile()

tranche_results = investments.evaluate_tranches(designs, sample_count=100)

evaluator = ty.Evaluator(investments.tranches, tranche_results.summary)

optimizer = ty.EpsilonConstraintOptimizer(evaluator)

# Run optimizer.
optimum = optimizer.maximize_slsqp(
    metric = target_metric,
    total_amount = total_amount,
)
amounts = pd.DataFrame(optimum.amounts)
value = pd.DataFrame(evaluator.evaluate(amounts))