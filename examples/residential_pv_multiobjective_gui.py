import os
import sys
sys.path.insert(0, os.path.abspath("../src"))

import numpy  as np
import pandas as pd
import tyche  as ty


investments = ty.Investments("../data/residential_pv_multiobjective")
designs     = ty.Designs("../data/residential_pv_multiobjective")
designs.compile()

tranche_results = investments.evaluate_tranches(designs, sample_count = 25)

evaluator = ty.Evaluator(investments.tranches, tranche_results.summary)

w = ty.DecisionWindow(evaluator)
w.mainloop()
