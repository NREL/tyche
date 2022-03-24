import os
import sys

sys.path.insert(1, os.path.abspath('/Users/tghosh/OneDrive - NREL/work_NREL/tyche/src/'))
#sys.path.insert(1, os.path.abspath('C:/Users/tghosh/Documents/GitHub/tyche/src/'))


import numpy             as np
import matplotlib.pyplot as pl
import pandas            as pd
import seaborn           as sb
import tyche             as ty

'''
 SAM BALDWIN
answers_designs = ty.Designs("answers")
answers_designs.indices.reset_index("Index").sort_values(["Type", "Offset"])
answers_designs.results
answers_designs.designs.xs("Reference", level = "Scenario", drop_level = False).reset_index(["Variable", "Index"]).sort_values(["Variable", "Index"])
answers_designs.parameters.xs("Reference", level = "Scenario", drop_level = False).reset_index("Parameter").sort_values("Offset")
answers_designs.functions

# All of the computations must be vectorized, so use `numpy`.
import numpy as np


def capital_cost(scale, parameter):
  """
  Capital cost function.

  Parameters
  ----------
  scale : float
    The scale of operation.
  parameter : array
    The technological parameterization.
  """

  # We aren't varying the wind sheer exponent.
  alpha = 0.16

  # It is handy to copy the elements of the parameter array into meaningful variable names.
  rho   = parameter[0]
  delta = parameter[1]
  tau   = parameter[2]
  beta  = parameter[3]
  mu    = parameter[4]

  # Compute the rotor diamter, hub height, and machine rating.
  r = 70 * scale**(1 / (2 + 3 * alpha))
  h = 65 * scale**(1 / (2 + 3 * alpha))
  m = 1500 * scale

  # Compute the components of capital cost.
  rotor = 1.6 * r**2.8 - 60000 * rho
  drive = 900 * m**delta
  tower = 0.015 * r**2.8 * h**tau
  bos   = 250 * beta * m

  # Stack the costs for each category into a single array that we return.
  return np.stack([
      rotor,
      drive,
      tower,
      bos,
  ])


def fixed_cost(scale, parameter):
  """
  Capital cost function.

  Parameters                                           
  ----------
  scale : float
    The scale of operation.
  parameter : array
    The technological parameterization.
  """

  # We aren't varying the wind sheer exponent.
  alpha = 0.16

  # It is handy to copy the elements of the parameter array into meaningful variable names.
  rho   = parameter[0]
  delta = parameter[1]
  tau   = parameter[2]
  beta  = parameter[3]
  mu    = parameter[4]

  # Compute the rotor diamter, hub height, and machine rating.
  r = 70 * scale**(1 / (2 + 3 * alpha))
  h = 65 * scale**(1 / (2 + 3 * alpha))
  m = 1500 * scale

  # Compute the components of fixed cost.
  replacement            = 10.6 * m
  operations_maintenance = 20 * mu * m
  land_lease             = 3.5 * m

  # Stack the costs for each category into a single array that we return.
  return np.stack([
      replacement,
      operations_maintenance,
      land_lease
  ])


def production(scale, capital, lifetime, fixed, input, parameter):
  """
  Production function.

  Parameters
  ----------
  scale : float
    The scale of operation.
  capital : array
    Capital costs.
  lifetime : float
    Technology lifetime.
  fixed : array
    Fixed costs.
  input : array
    Input quantities. 
  parameter : array
    The technological parameterization.
  """

  # We aren't varying the wind sheer exponent.
  alpha = 0.16

  # It is handy to copy the elements of the parameter array into meaningful variable names.
  rho   = parameter[0]
  delta = parameter[1]
  tau   = parameter[2]
  beta  = parameter[3]
  mu    = parameter[4]

  # Compute the production of electricity.
  electricity = 4312 * scale / 0.3282

  # Stack the output for each category into a single array that we return.
  return np.stack([
      electricity,
  ])


def metrics(scale, capital, lifetime, fixed, input_raw, input, output_raw, output, cost, parameter):
  """
  Metrics function.

  Parameters
  ----------
  scale : float
    The scale of operation.
  capital : array
    Capital costs.
  lifetime : float
    Technology lifetime.
  fixed : array
    Fixed costs.
  input_raw : array
    Raw input quantities (before losses).
  input : array
    Input quantities. 
  output_raw : array
    Raw output quantities (before losses).
  output : array
    Output quantities. 
  cost : array
    Costs.
  parameter : array
    The technological parameterization.
  """

  # We aren't varying the wind sheer exponent.
  alpha = 0.16

  # It is handy to copy the elements of the parameter array into meaningful variable names.
  rho   = parameter[0]
  delta = parameter[1]
  tau   = parameter[2]
  beta  = parameter[3]
  mu    = parameter[4]

  # Compute the metrics.
  lcoe = cost / output[0] / 1000
  cf = output[0] / output_raw[0]
  aep = output[0]

  # Package results.
  return np.stack([
    cost,
    lcoe,
    cf  ,
    aep ,
  ])



example_capital = capital_cost(1, [0, 0.9, 1, 1, 1])

example_fixed = fixed_cost(1, [0, 0.9, 1, 1, 1])

example_production = production(
    1,
    example_capital,
    [8.6, 8.6, 8.6],
    example_fixed,
    [0],
    [0, 0.9, 1, 1, 1],
)

example_metrics = metrics(
    1,
    example_capital,
    [8.6, 8.6, 8.6],
    example_fixed,
    [0],
    [0],
    example_production,
    example_production * 0.3282,
    sum(example_capital / 8.6) + sum(example_fixed),
    [0, 0.9, 1, 1, 1],
)

'''

answers_designs = ty.Designs("answers")

sys.path.insert(1, os.path.abspath('/Users/tghosh/OneDrive - NREL/work_NREL/tyche/tutorial/'))

answers_designs.compile()

answers_reference = answers_designs.evaluate_scenarios(
    sample_count=2
).xs(
    "Reference",
    level = "Scenario",
    drop_level = False
)

answers_experts = answers_designs.evaluate_scenarios(
    sample_count=2
).xs(
    "Casual Rotor R&D",
    level = "Scenario",
    drop_level = False
)



     
sb.violinplot(
    answers_reference.xs(
        ("Wind Turbine", "Reference", "Metric", "LCOE"),
        level = ("Technology", "Scenario", "Variable", "Index")
    )["Value"]
).set(xlabel = "LCOE [%/kWh]")




answers_designs.parameters.iloc[
    answers_designs.parameters.index.get_level_values(2).isin(
        ["Rotor design", "Drive design", "Tower design"]
    )
]


answers_experts = answers_designs.evaluate_scenarios(
    sample_count=10
)

answers_experts.to_csv('answers_expert.csv')

sb.violinplot(
    y = "Scenario",
    x = "Value",
    data = answers_experts.xs(
        ("Wind Turbine", "Metric", "LCOE"),
        level = ("Technology", "Variable", "Index")
    ).reset_index()
).set(xlabel = "LCOE [%/kWh]")






answers_investments = ty.Investments("answers")

answers_investments.tranches.to_csv('answers_transches.csv')


answers_investments.tranches.xs(
    "Base Case",
    drop_level = False
).reset_index(
).sort_values(
    ["Category", "Amount"]
).set_index(
    ["Category", "Tranche"]
)

    
tranche_results = answers_investments.evaluate_tranches(answers_designs, sample_count=2)
res = tranche_results.amounts.reset_index().sort_values(["Category", "Amount"]).set_index(["Category", "Tranche"])
tranche_results.metrics.to_csv('tranche-results.csv')
z = tranche_results.summary.xs("LCOE", level = "Index", drop_level = False)




z_reference = np.mean(z.xs("Base Case")["Value"])
z["Value"] = z_reference - z["Value"]
z = z[z.index.get_level_values(0) != "Base Case"]

z.to_csv('normalized-z.csv')



evaluator = ty.Evaluator(answers_investments.tranches[answers_investments.tranches.index.get_level_values(0) != "Base Case"], z)



optimizer = ty.EpsilonConstraintOptimizer(evaluator)

'''
optimum = optimizer.opt_slsqp(
    metric = "LCOE",
    sense = 'max',
    total_amount = 5000000,
    verbose = 0,
    maxiter = 10
)

print(optimum)
'''

import time
t = time.time()
optimum = optimizer.opt_milp(
    metric = "LCOE",
    sense = 'max',
    total_amount = 5000000,
    verbose = 0,
)

print(time.time() - t)
