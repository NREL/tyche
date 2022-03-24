
import os
import sys
sys.path.insert(0, os.path.abspath(".."))

import numpy             as np
import matplotlib.pyplot as pl
import pandas            as pd
import seaborn           as sb
import tkinter           as tk
import tyche             as ty

def aggregate_over(ser, idx, statistic = np.mean):
    ser = ser.astype("float64")
    idx_res = list(set(ser.index.names.copy()) - set(idx))
    return ser.groupby(idx_res).aggregate(statistic)


designs = ty.Designs("../../data/residential_pv_multiobjective")
investments = ty.Investments("../../data/residential_pv_multiobjective")
designs.compile()

tranche_results = investments.evaluate_tranches(designs, sample_count=50)

evaluator = ty.Evaluator(investments.tranches, tranche_results.summary)
example_investments = evaluator.max_amount / 2
evaluation = evaluator.evaluate(example_investments)

met = "GHG"

area = example_investments.astype("float64").rename({"Amount": "Value"}, axis='columns')
y = pd.DataFrame(aggregate_over(evaluation, ['Sample']).xs(met, level="Index"))
x = abs(area / y)

print(x)
print(y)

pd.merge(x,y)

# root = tk.Tk()
# canvas = tk.Canvas(root, width=400, height=400)
# canvas.pack()
# canvas.create_rectangle(0,0,100,10,fill='red')
# canvas.create_rectangle(200,200,100,10,fill='blue')
# root.mainloop()