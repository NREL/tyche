import os
import sys
sys.path.insert(0, os.path.abspath("../src"))

import numpy  as np
import pandas as pd
import tyche  as ty


designs     = ty.Designs("../data/residential_pv_multiobjective")
designs.compile()
investments = ty.Investments("../data/residential_pv_multiobjective")

tranche_results = investments.evaluate_tranches(designs, sample_count = 25)

e = ty.Evaluator(investments.tranches, tranche_results.summary)

ecm = ty.EpsilonConstraintMinimizer(e)

q = ecm.max_metrics()
q


w = ty.DecisionWindow(e)
w.mainloop()
