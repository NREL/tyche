"""
Small modular reactor technology model file

This file acts as a bridge to the ACCERT model, included in this repo as a marimo notebook.
"""

import numpy as np

from nuclear_stride import calculate_final_result

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
  # See the input dataset for parameter definitions, units, and ranges
  all_results = calculate_final_result(
    reactor_type = 'Concept B',
    n_th = parameter[15],
    f_22 = parameter[19],
    f_2321 = parameter[20],
    land_cost_per_acre_0 = parameter[5],
    RB_grade_0 = parameter[10],
    BOP_grade_0 = parameter[9],
    num_orders = parameter[14],
    design_completion_0 = parameter[1],
    ae_exp_0 = parameter[3],
    N_AE = parameter[16],
    ce_exp_0 = parameter[4],
    N_cons = parameter[18],
    mod_0 = parameter[11],
    Design_Maturity_0 = parameter[0],
    proc_exp_0 = parameter[2],
    N_proc = parameter[17],
    standardization_0 = parameter[12],
    interest_rate_0 = parameter[8],
    startup_0 = parameter[13],
    om_fixed = parameter[22],
    om_variable = parameter[21],
    spent_fuel_cost = parameter[23],
  )
  # Stack the capital cost values into a single array to return.
  # The second element of the tuple returned by calculate_final_result is the
  # total overnight capital cost for the entire reactor.
  return np.stack(all_results[1])


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
  all_results = calculate_final_result(
    reactor_type = 'Concept B',
    n_th = parameter[15],
    f_22 = parameter[19],
    f_2321 = parameter[20],
    land_cost_per_acre_0 = parameter[5],
    RB_grade_0 = parameter[10],
    BOP_grade_0 = parameter[9],
    num_orders = parameter[14],
    design_completion_0 = parameter[1],
    ae_exp_0 = parameter[3],
    N_AE = parameter[16],
    ce_exp_0 = parameter[4],
    N_cons = parameter[18],
    mod_0 = parameter[11],
    Design_Maturity_0 = parameter[0],
    proc_exp_0 = parameter[2],
    N_proc = parameter[17],
    standardization_0 = parameter[12],
    interest_rate_0 = parameter[8],
    startup_0 = parameter[13],
    om_fixed = parameter[22],
    om_variable = parameter[21],
    spent_fuel_cost = parameter[23],
  )
  
  return np.stack(all_results[4])


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
  all_results = calculate_final_result(
    reactor_type = 'Concept B',
    n_th = parameter[15],
    f_22 = parameter[19],
    f_2321 = parameter[20],
    land_cost_per_acre_0 = parameter[5],
    RB_grade_0 = parameter[10],
    BOP_grade_0 = parameter[9],
    num_orders = parameter[14],
    design_completion_0 = parameter[1],
    ae_exp_0 = parameter[3],
    N_AE = parameter[16],
    ce_exp_0 = parameter[4],
    N_cons = parameter[18],
    mod_0 = parameter[11],
    Design_Maturity_0 = parameter[0],
    proc_exp_0 = parameter[2],
    N_proc = parameter[17],
    standardization_0 = parameter[12],
    interest_rate_0 = parameter[8],
    startup_0 = parameter[13],
    om_fixed = parameter[22],
    om_variable = parameter[21],
    spent_fuel_cost = parameter[23],
  )
  # Return: MWh electricity produced in a year
  # Accounts for capacity factor
  return np.stack(all_results[5])


def metrics(scale, capital, lifetime, fixed, input_raw, input, input_price, output_raw, output, cost, parameter):
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
  all_results = calculate_final_result(
    reactor_type = 'Concept B',
    n_th = parameter[15],
    f_22 = parameter[19],
    f_2321 = parameter[20],
    land_cost_per_acre_0 = parameter[5],
    RB_grade_0 = parameter[10],
    BOP_grade_0 = parameter[9],
    num_orders = parameter[14],
    design_completion_0 = parameter[1],
    ae_exp_0 = parameter[3],
    N_AE = parameter[16],
    ce_exp_0 = parameter[4],
    N_cons = parameter[18],
    mod_0 = parameter[11],
    Design_Maturity_0 = parameter[0],
    proc_exp_0 = parameter[2],
    N_proc = parameter[17],
    standardization_0 = parameter[12],
    interest_rate_0 = parameter[8],
    startup_0 = parameter[13],
    om_fixed = parameter[22],
    om_variable = parameter[21],
    spent_fuel_cost = parameter[23],
  )
  # Metrics: construction duration (months), levelized net overnight capital cost,
  # levelized net capital investment, total overnight cost per kWe, total capital
  # investment cost per kWh
  return np.stack([all_results[3],
                   all_results[1],
                   all_results[2],
                   all_results[6],
                   all_results[7]])
