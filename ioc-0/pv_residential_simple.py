import os
import sys
sys.path.insert(0, os.path.abspath("../src"))

import numpy  as np
import pandas as pd
import tyche  as ty


investments = ty.Investments("data/pv_residential_simple")
designs     = ty.Designs("data/pv_residential_simple")
designs.compile()

tranche_results = investments.evaluate_tranches(designs, sample_count = 25)

evaluator = ty.Evaluator(investments.tranches, tranche_results.summary)

optimizer = ty.EpsilonConstraintOptimizer(evaluator)

q = optimizer.max_metrics(verbose = 0)
q

optimizer.opt_slsqp(
  "LCOE"                                                       ,
  total_amount = 3e6                                           ,
  min_metric   = pd.Series([40], name="Value", index = ["GHG"]),
  verbose      = 0                                             ,
)
