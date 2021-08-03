"""
Phase-1 model to estimate the cost, energy, and emissions associated with a 
particular vehicle/transport technology. 
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
  
  # Unpack variables.   
  glider                    = parameter[0]
  fuel_converter_variable   = parameter[1]
  fuel_converter_fixed      = parameter[2]
  fuel_storage_variable     = parameter[3]
  fuel_storage_fixed        = parameter[4]
  battery_variable          = parameter[5]
  battery_fixed             = parameter[6]
  battery_power_cost        = parameter[7]
  edt_variable              = parameter[8]
  edt_fixed                 = parameter[9]
  plug                      = parameter[10]
  
  fuel_converter_size       = parameter[12]
  fuel_storage_size         = parameter[14]
  battery_size              = parameter[16]
  battery_power             = parameter[18]
  edt_size                  = parameter[19]
  
  markup                    = parameter[25]
  
  # Calculate component costs. 
  glider            = glider * markup
  fuel_converter    = (fuel_converter_fixed + fuel_converter_variable * fuel_converter_size) * markup
  fuel_storage      = (fuel_storage_fixed + fuel_storage_variable * fuel_storage_size) * markup
  battery           = (battery_fixed + battery_variable * battery_size + battery_power * battery_power_cost) * markup
  edt               = (edt_fixed + edt_variable * edt_size) * markup

  # Stack the costs for each category into a single array that we return.
  return np.stack([
      glider, 
      fuel_converter, 
      fuel_storage, 
      battery,
      edt, 
      plug
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
  
  fixed_costs = parameter[24]           # $/mile
  fixed_costs = fixed_costs * scale     # $/yr
  
  # Stack the costs for each category into a single array that we return.
  return np.stack([
      fixed_costs
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

  # Stack the output for each category into a single array that we return.
  return np.stack([
      scale
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

  # Package results.
  return np.stack([

  ])
