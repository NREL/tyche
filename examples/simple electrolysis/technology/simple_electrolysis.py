"""
Simple electrolysis.
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

  # Scale the reference values.
  return np.stack([np.multiply(parameter[6], np.divide(scale, parameter[5]))])


def fixed_cost(scale, parameter):
  """
  Fixed cost function.

  Parameters
  ----------
  scale : float
    The scale of operation.
  parameter : array
    The technological parameterization.
  """

  # Scale the reference values.
  return np.stack([np.multiply(parameter[7], np.divide(scale, parameter[5]))])


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

  # Moles of input.
  water       = np.divide(input[0], parameter[2])
  electricity = np.divide(input[1], parameter[3])

  # Moles of output.
  output = np.minimum(water, electricity)

  # Grams of output.
  oxygen   = np.multiply(output, parameter[0])
  hydrogen = np.multiply(output, parameter[1])

  # Package results.
  return np.stack([oxygen, hydrogen])


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
