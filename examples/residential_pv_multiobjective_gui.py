import os
import sys
sys.path.insert(0, os.path.abspath("../src"))

import tyche as ty


designs     = ty.Designs("../data/residential_pv_multiobjective")
investments = ty.Investments("../data/residential_pv_multiobjective")

designs.compile()

tranche_results = investments.evaluate_tranches(designs, sample_count = 500)


e = ty.Evaluator(investments.tranches, tranche_results.summary)

w = ty.DecisionWindow(e)

w.mainloop()
