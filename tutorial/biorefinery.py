import os
import sys
sys.path.insert(1, os.path.abspath("../src"))
import numpy             as np
import matplotlib.pyplot as pl
import pandas            as pd
import seaborn           as sb
import tyche             as ty


def post(a,b):
    a.to_csv(b+'.csv')


my_designs = ty.Designs("data/biorefinery_v1/")
my_designs.indices.reset_index("Index").sort_values(["Type", "Offset"])
post(my_designs.results,'results')
my_designs.designs.reset_index(["Variable", "Index"]).sort_values(["Variable", "Index"])
post(my_designs.designs,'designs')
my_designs.parameters.reset_index("Parameter").sort_values("Scenario")
post(my_designs.parameters,'parameters')

post(my_designs.functions,'functions')
my_investments = ty.Investments("data/biorefinery_v1")
post(my_investments.investments,'investments')
post(my_investments.tranches,'tranches')


my_designs.compile()
investment_results = my_investments.evaluate_investments(my_designs, sample_count=1)
tranche_results = my_investments.evaluate_tranches(my_designs, sample_count=1)

post(my_designs.results,'design_result')
post(investment_results.summary,'investment_summary')
post(tranche_results.summary,'tranche_summary')

evaluator = ty.Evaluator(my_investments.tranches, tranche_results.summary)
#evaluator2 = ty.Evaluator(my_investments.investments, investment_results.summary)

_wide = evaluator.evaluate_corners_wide(np.mean).reset_index()





'''
g = sb.boxplot(
    x="Investment",
    y="Value",
    data=investment_results.metrics.xs(
        "Total GHG",
        level="Index"
    ).groupby(["Investment", "Sample"]).aggregate(np.sum).reset_index()[["Investment", "Value"]],
    order=[
        "No R&D"   ,
        "Low R&D"  ,
        "Moderate R&D",
        "High R&D"  ,
    ]
)

'''
optimizer = ty.EpsilonConstraintOptimizer(evaluator)



q = optimizer.optimum_metrics(verbose = 0,
                             sense = {'Fossil GHG': 'min',
                                     'Jobs': 'max',
                                     'MFSP': 'min',
                                     'Total GHG': 'min'})

#%%

slsqp_result = optimizer.opt_slsqp(
    "MFSP"                                                       ,
    sense = 'min'                                                ,
    total_amount = 3e8                                           ,
    verbose      = 0                                             ,
)
print(slsqp_result[3])
print(slsqp_result[2])




diffev_result = optimizer.opt_diffev(
    "MFSP"                                                       ,
    sense = 'min'                                                ,
    total_amount = 3e8                                           ,
    verbose      = 0                                             ,
)
print(diffev_result[3])
print(diffev_result[2])

#%%


pwlinear_result = optimizer.opt_milp(
    "MFSP",
    sense='min',
    total_amount = 3e8,
    verbose = 0
)

print(pwlinear_result.metrics)
print(pwlinear_result.amounts)
print(pwlinear_result.solve_time)