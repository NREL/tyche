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
  
  markup                    = parameter[27]
  
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
  
  # Unpack variables.
  fuel_storage_size         = parameter[14]
  battery_size              = parameter[16]
  dwell_time_cost           = parameter[21]
  dwell_rate                = parameter[22]
  dwell_type                = parameter[23]
  dwell_bool                = parameter[24]
  maintenence_cost          = parameter[25]
  other_fixed_cost          = parameter[26]
  
  carbon_intensity          = parameter[28]
  carbon_price              = parameter[29]
  carbon_price_bool         = parameter[30]
  fuel_efficiency           = parameter[31]                         # FIXME: duplicate of input[1]
  
  # Compute direct (non-fuel) fixed costs.
  maintenence_cost  = maintenence_cost * scale                      # $/yr
  other_fixed_cost  = other_fixed_cost * scale                      # $/yr
  
  # Compute indirect costs.
  # Dwell time costs.
  if dwell_type: 
      dwell_size = battery_size
  else: 
      dwell_size = fuel_storage_size
  
  cost_per_refueling    = (dwell_size / dwell_rate / 60) * dwell_time_cost      # 60 mins/hour; simple linear refueling approximation
  range_miles           = dwell_size / (fuel_efficiency * 33.7)                 # 33.7 kWh/gge
  n_refuelings          = scale / range_miles
  dwell_cost            = n_refuelings * cost_per_refueling * dwell_bool
  
  # Carbon costs.
  energy = scale * fuel_efficiency                                  # gge/yr
  carbon = energy * carbon_intensity / 1e6                          # 1e6 gram/tonne
  carbon_cost = carbon * carbon_price * carbon_price_bool
  
  # Sum fixed costs.
  fixed_cost = maintenence_cost + other_fixed_cost + dwell_cost + carbon_cost
  
  # Stack the costs for each category into a single array that we return.
  return np.stack([
      fixed_cost                                                    # $/yr
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
  
  # Unpack variables. 
  glider_wt                 = parameter[11]
  fuel_converter_wt         = parameter[13]
  fuel_storage_wt           = parameter[15]
  battery_wt                = parameter[17]
  edt_wt                    = parameter[20]
  
  carbon_intensity          = parameter[28]
  fuel_efficiency           = parameter[31]                         # FIXME: duplicate of input[1]
  
  # Compute LCOD.
  lcod = cost
  
  # Compute upfront purchase price (MSRP). 
  msrp = cost * scale * lifetime
  
  # Compute total (undiscounted) lifetime cost. 
  lifetime_cost = lcod * scale * lifetime               # Could make lifetime a CRF to discount to NPV.

  # Compute vehicle weight.
  weight = glider_wt + fuel_converter_wt + fuel_storage_wt + battery_wt + edt_wt
  
  # Compute lifetime energy usage.
  energy = scale * lifetime * fuel_efficiency
  
  # Compute greenhouse gas emissions. 
  ghg = carbon_intensity * energy

  # Package results.
  return np.stack([
      lcod, msrp, lifetime_cost, weight, energy, ghg
  ])
