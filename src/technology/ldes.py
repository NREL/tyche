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
    _cap_rectifier = parameter[9]
    _cap_electrolysis = parameter[10]
    _cap_bos1 = parameter[11]
    _cap_compressor = parameter[12]
    _cap_cavern = parameter[13]
    _cap_bos2 = parameter[14]
    _cap_fuel_cell = parameter[15]
    _cap_inverter = parameter[16]
    _cap_bos3 = parameter[17]

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
  _fixed_rectifier = parameter[18]
  _fixed_electrolysis = parameter[19]
  _fixed_bos1 = parameter[20]
  _fixed_compressor = parameter[21]
  _fixed_cavern = parameter[22]
  _fixed_bos2 = parameter[23]
  _fixed_fuel_cell = parameter[24]
  _fixed_inverter = parameter[25]
  _fixed_bos3 = parameter[26]

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

  effiency_rectifier = parameter[0]
  conversion_factor_electrolysis = parameter[1]

  conversion_factor_compress = parameter[3]
  conversion_factor_cavern = parameter[4]
  conversion_factor_bos2 = parameter[5]
  conversion_factor_fuel_cell = parameter[6]
  conversion_factor_inverter = parameter[7]
  conversion_factor_bos3 = parameter[8]

  ac_electricity_in = input[0]

  dc_electricity1 = efficiency_rectifier*ac_electricity_in
  hydrogen1 = dc_electricity1 * conversion_factor_electrolysis * efficiency_electrolysis
  hyrogen_compressed = 




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
  ghg_foss_ef = parameter[4]
  energy_produced = parameter[3]*output[0]
  total_ghg = ghg_foss_ef * energy_produced
  jobs = parameter[5]
  #Total cost per year
  total_cost = capital[0]/lifetime[0] + fixed[0] + input[0]*input_price[0] - output[0]*output_price[0]

  # Package results.
  return np.stack([total_cost,
    jobs,
    total_ghg
  ])