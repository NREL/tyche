"""
Simplified representation of sustainable aviation fuel (SAF) production from
the hydroprocessed esters and fatty acids (HEFA) biorefinery concept. Either a
biomass-derived oil or waste oil may be used as feedstock.
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
    _cap_rectifier = parameter[10]
    _cap_electrolysis = parameter[11]
    _cap_bos1 = parameter[12]
    _cap_compressor = parameter[13]
    _cap_cavern = parameter[14]
    _cap_bos2 = parameter[15]
    _cap_fuel_cell = parameter[16]
    _cap_inverter = parameter[17]
    _cap_bos3 = parameter[18]

    capital_cost = _cap_rectifier + _cap_electrolysis + _cap_bos1 + _cap_compressor + _cap_cavern + _cap_bos2 + _cap_fuel_cell + _cap_inverter + _cap_bos3


    # Stack the costs for each category into a single array that we return.
    return np.stack([capital_cost
    ])

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
  _fixed_rectifier = parameter[19]
  _fixed_electrolysis = parameter[20]
  _fixed_bos1 = parameter[21]
  _fixed_compressor = parameter[22]
  _fixed_cavern = parameter[23]
  _fixed_bos2 = parameter[24]
  _fixed_fuel_cell = parameter[25]
  _fixed_inverter = parameter[26]
  _fixed_bos3 = parameter[27]

  fixed_cost = _fixed_rectifier + _fixed_electrolysis + _fixed_bos1 + _fixed_compressor + _fixed_cavern + _fixed_bos2 + _fixed_fuel_cell + _fixed_inverter + _fixed_bos3



  # Stack the costs for each category into a single array that we return.
  return np.stack([fixed_cost
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

  efficiency_rectifier = parameter[0]
  conversion_factor_electrolysis = parameter[1]
  efficiency_electrolysis = parameter[2]
  efficiency_compress = parameter[3]
  efficiency_cavern = parameter[4]
  conversion_factor_fuel_cell = parameter[5]
  efficiency_factor_fuel_cell = parameter[6]
  efficiency_inverter = parameter[7]

  ac_electricity_in = input[0]

  dc_electricity1 = efficiency_rectifier*ac_electricity_in
  hydrogen1 = dc_electricity1*conversion_factor_electrolysis*efficiency_electrolysis
  hyrogen_compressed = hydrogen1*efficiency_compress
  hyrogen_released = hyrogen_compressed*efficiency_cavern
  dc_electricity2 = hyrogen_released*conversion_factor_fuel_cell*efficiency_factor_fuel_cell
  ac_electricity_out = dc_electricity2*efficiency_inverter




  # Stack the output for each category into a single array that we return.
  return np.stack([ac_electricity_out
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

  # annual fossil GHG emissions, Units: kg CO2-eq/year
  total_ghg = parameter[8]*output[0]
  jobs = parameter[9]
  #LCOS cost per year $/kwh
  LCOS = cost/output[0]

  # Package results.
  return np.stack([LCOS,
    jobs,
    total_ghg
  ])