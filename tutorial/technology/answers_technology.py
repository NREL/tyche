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
