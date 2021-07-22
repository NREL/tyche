"""
Template for technology functions.
"""


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

  # It is handy to copy the elements of the parameter array into meaningful variable names.
  a = parameter[0]
  b = parameter[1]
    
  # Here are some example computations:
  capital_cost_category_1 = scale * a
  capital_cost_category_2 = scale * b

  # Stack the costs for each category into a single array that we return.
  return np.stack([
      capital_cost_category_1,
      capital_cost_category_2,
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

  # It is handy to copy the elements of the parameter array into meaningful variable names.
  a = parameter[0]
  b = parameter[1]
    
  # Here are some example computations:
  fixed_cost_category_1 = scale * a
  fixed_cost_category_2 = scale * b
  fixed_cost_category_3 = scale * np.sqrt(a * b)

  # Stack the costs for each category into a single array that we return.
  return np.stack([
      fixed_cost_category_1,
      fixed_cost_category_2,
      fixed_cost_category_3,
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

  # It is handy to copy the elements of the parameter array into meaningful variable names.
  a = parameter[0]
  b = parameter[1]
    
  # Here are some example (meaningless) computations:
  output_category_1 = scale * capital / lifetime
  output_category_2 = a * b
  output_category_3 = lifetime + input
  output_category_4 = scale * np.sqrt(a * b)

  # Stack the output for each category into a single array that we return.
  return np.stack([
      output_cost_category_1,
      output_cost_category_2,
      output_cost_category_3,
      output_cost_category_4,
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

  # Hydrogen output.
  hydrogen = output[1]

  # Cost of hydrogen.
  cost1 = np.divide(cost, hydrogen)

  # Jobs normalized to hydrogen.
  jobs = np.divide(parameter[4], hydrogen)

  # GHGs associated with water and electricity.
  water       = np.multiply(input_raw[0], parameter[8])
  electricity = np.multiply(input_raw[1], parameter[9])
  co2e = np.divide(np.add(water, electricity), hydrogen)

  # Package results.
  return np.stack([cost1, jobs, co2e])
