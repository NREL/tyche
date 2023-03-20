"""
Template for technology model file.

Corresponds to Technology B in the template decision context.
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
  return np.stack((parameter[0] * scale**0.6,
                   parameter[1] * scale**0.6,
                   parameter[2] * scale**0.6,
                   parameter[3] * scale**0.6,
                   parameter[4] * scale**0.6))


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
  # total capital cost.  
  # Stack the fixed cost values into a single array to return.
  return np.stack(0.1 * (parameter[0] + parameter[1] + parameter[2] + parameter[3] + parameter[4]) * scale)


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
  return np.stack((parameter[13] * parameter[14] * input[2],
                   parameter[14] * input[1],
                   parameter[14] * input[2]))


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
  _annualized_cost_per_unit_F = (capital[0] + capital[1] + capital[2] + capital[3] + capital[4] + fixed*lifetime[0] + input_price[0] * input_raw[0] + input_price[1] * input_raw[1] + input_price[2] * input_raw[2])/output[0] - parameter[15]
  _labor_per_unit_F = (parameter[8] * output_raw[0] + parameter[9] * (output_raw[1] + output_raw[2]))/output[0] - parameter[16]
  _impact_per_unit_F = (parameter[5] * input_raw[0] + parameter[6] * input_raw[1] + parameter[7] * input_raw[2]) / output[0] - parameter[17]
  _overall_efficiency = output[0] / (input_raw[0] + input_raw[1] + input_raw[2]) - parameter[18]
  # Stack the metric values into a single array to return.
  return np.stack((_annualized_cost_per_unit_F,
                   _labor_per_unit_F,
                   _impact_per_unit_F,
                   _overall_efficiency))
