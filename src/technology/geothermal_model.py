"""
Geothermal model.
"""

# All of the computations must be vectorized, so use `numpy`.
from matplotlib import scale
import numpy as np


def capital_cost(scale, parameter, atb):
    """
    Capital cost function.

    Parameters
    ----------
    scale : float
      The scale of operation.
    atb : object
      ATB data object.

    Returns
    -------
    array
      Capital costs.
    """
    # ATB CAPEX equation
    # CFF: Construction Finance Factor (unitless, calculated in the ATB workbook)
    # OCC: Overnight capital cost ($/ kW)
    # GCC: Grid Connection Cost ($/ kW)
    # CAPEX = CFF * (OCC + GCC)
    # CAPEX, OCC, and GCC are reported in the extracted ATB data

    # occ = scale * atb.extract_values(parameter = 'OCC') 
    occ = scale * parameter[5]
    gcc = scale * atb.extract_values(parameter = 'GCC') 
    capex = scale * atb.extract_values(parameter = 'CAPEX') 

    # TODO: check if we need this value
    # cff = capex / (occ + gcc)

    return np.stack([occ, gcc, capex])

def fixed_cost(scale, parameter, atb):
  """
  Fixed cost function.

  Parameters
  ----------
  scale : float
    The scale of operation.
  atb : object
    ATB data object.

  Returns
  -------
  array
    Capital costs.
  """
  # From ATB fixed O&M equation
  # FOM: Fixed O&M ($/ kW-yr)
  fom = scale * atb.extract_values(parameter = 'Fixed O&M') 

  return np.stack([fom])


def production(scale, capital, lifetime, fixed, input, parameter, atb):
  """
  Production function.

  Parameters
  ----------
  scale : float
    The scale of operation.
  """
  # MWh of electricity (per year)
  plant_capacity = input[0]  # in MW 
  net_capacity_factor = atb.extract_values(parameter = 'CF')

  electricity_output = scale * plant_capacity * net_capacity_factor * 8760
  return np.stack([electricity_output])


def metrics(scale, capital, lifetime, fixed, input_raw, input, input_price, output_raw, output, cost, parameter, atb):
  """
  Metrics function.

  Parameters
  ----------
  scale : float
  The scale of operation.
  lcoe : float
    levelized cost of electricity
  """

  # read tyche parameters
  ptc = parameter[0] # Premium Tax Credit
  pff = parameter[1] # PFF Tax credits
  cff = parameter[2] # Construction Finance Factor
  crp = parameter[3] # Capital Recovery Period
  net_capacity_factor = parameter[4] # capacity factor

  # read atb parameters
  capital_recovery_factor = atb.extract_values(parameter = 'CRF')
  overnight_capital_cost = atb.extract_values(parameter = 'OCC')
  grid_connection_cost = atb.extract_values(parameter = 'GCC')
  fixed_om = atb.extract_values(parameter = 'Fixed O&M')
  variable_om = atb.extract_values(parameter = 'Variable O&M')
  # net_capacity_factor = atb.extract_values(parameter = 'CF')

  occ = scale * parameter[5]
  lcoe = scale * (((capital_recovery_factor * pff * cff * (overnight_capital_cost * 1 + grid_connection_cost) + fixed_om) * 1000 / (net_capacity_factor * 8760)) + variable_om + 0 - ptc)

  return np.stack([lcoe, occ])
