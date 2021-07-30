#!/usr/bin/env python
# coding: utf-8

import os
import sys
sys.path.insert(0, os.path.abspath("../../src"))

import numpy             as np
import matplotlib.pyplot as pl
import pandas            as pd
import seaborn           as sb
import tyche             as ty

from copy            import deepcopy


designs = ty.Designs("../data/pv_residential_simple")
investments = ty.Investments("../data/pv_residential_simple")
designs.compile()

tranche_results = investments.evaluate_tranches(designs, sample_count=50)
print(tranche_results.amounts)

evaluator = ty.Evaluator(investments.tranches, tranche_results.summary)
optimizer = ty.EpsilonConstraintOptimizer(evaluator)

metric_max = optimizer.max_metrics()
print(metric_max)

investment_max = 3e6

metric_min = pd.Series([40, 0], name = "Value", index = ["GHG", "Labor"])
print(metric_min)


# Use SLSQP.
optimum = optimizer.maximize_slsqp(
    "LCOE"                       ,
    total_amount = investment_max,
    min_metric   = metric_min    ,
    statistic    = np.mean       ,
)

print(optimum.exit_message)

print(np.round(optimum.amounts))

print(optimum.metrics)


# Use Piecewise-Linear MILP.

optimum = optimizer.pwlinear_milp(
    "LCOE"                       ,
    total_amount = investment_max,
    min_metric   = metric_min    ,
    statistic    = np.mean       ,
)

print(optimum.exit_message)

print(np.round(optimum.amounts))

print(optimum.metrics)
