"""
Template for technology model file.

Corresponds to Technology A in the template decision context.
"""

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
  # Stack the capital cost values into a single array to return.
  return np.stack([parameter[0] * scale**0.6,
                   parameter[1] * scale**0.6,
                   parameter[2] * scale**0.6])


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
  # Fixed costs are being modeled as a fraction of the
  # total capital cost
  # Stack the fixed cost values into a single array to return.
  return np.stack([0.1 * (parameter[0] + parameter[1] + parameter[2]) * scale])


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
  # Stack the calculated output values into a single array to return.
  return np.stack([parameter[8] * input[0],
                   parameter[9] * input[1],
                   parameter[10] * input[0]])


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
  _annualized_cost = capital[0] + capital[1] + capital[2] + fixed*lifetime + input_price[0] * input[0] + input_price[1] * input[1] + input_price[2] * input[2]
  _labor_per_unit_F = (parameter[6] * output[0] + parameter[7] * (output[1] + output[2]))/output[0]
  _impact_per_unit_F = (parameter[3] * input_raw[0] + parameter[4] * input_raw[1] + parameter[5] + input_raw[2]) / output[0]
  # Stack the metric values into a single array to return.
  return np.stack([_annualized_cost,
                   _labor_per_unit_F,
                   _impact_per_unit_F])
