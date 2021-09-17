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
    _cap = parameter[5]

    # Stack the costs for each category into a single array that we return.
    return np.stack([_cap
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
  _fix = parameter[6]

  # Stack the costs for each category into a single array that we return.
  return np.stack([_fix
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

  _jet = parameter[12]
  _gas = parameter[10]
  _dsl = parameter[9]
  _ppn = parameter[11]
  _ddgs = parameter[7]
  _elec = parameter[8]

  # Stack the output for each category into a single array that we return.
  return np.stack([_jet,
                   _gas,
                   _dsl,
                   _ppn,
                   _ddgs,
                   _elec
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
  ghg_foss_ann = parameter[0]

  # jet fuel LHV (MJ/gal)
  lhv = parameter[1]

  # Discount rate, Unitless
  dr = parameter[2]
  # Depreciation period for all equipment except utilities, Units: years
  dp = parameter[3]
  # Income tax rate, Units: years
  tr = parameter[4]
  # total capital cost, Units: USD
  cap = parameter[5]
  # Annual fixed (non-input) costs, Units: USD/year
  fix = parameter[6]

  # co-product amounts
  ddgs = parameter[7]
  elec = parameter[8]
  dsl = parameter[9]
  gas = parameter[10]
  ppn = parameter[11]
  jet = parameter[12]

  # co-product prices
  ddgs_p = parameter[13]
  elec_p = parameter[14]
  dsl_p = parameter[15]
  gas_p = parameter[16]
  ppn_p = parameter[17]

  # input prices
  fd_p = parameter[18]
  mat_p = parameter[19]

  # input amounts
  fd = input_raw[0]
  mat = input_raw[1]

  # equipment lifetime
  els = lifetime[0]

  mjsp_bench = parameter[20]
  ghg_bench = parameter[21]

  # FOSSIL GHG: kg CO2-eq/gal SAF
  ghg_foss = ghg_foss_ann / (jet * lhv)

  # MINIMUM FUEL SELLING PRICE: USD/gal SAF

  # total project investment, Units: USD
  tpi = cap

  # depreciation costs, units: USD/year
  dc = cap / dp

  # operating costs, units: USD/year
  oc = fd * fd_p + mat * mat_p + fix

  # tpi discount factor, Units: unitless
  df_tpi = (dr * (1 + dr) ** els) / ((1 + dr) ** els - 1)

  # total revenue from SAF sales, Units: USD/year
  br = ((1 - tr) * oc - tr * dc + df_tpi * tpi) / (1 - tr)

  # revenue from co-product sales, Units: USD/year
  cr = ddgs * ddgs_p + elec * elec_p + dsl * dsl_p + gas * gas_p + ppn * ppn_p

  # MJSP, Units: USD/gal SAF
  mjsp = (br + cr) / output[0]

  # Package results.
  return np.stack([ghg_bench - ghg_foss,
                   mjsp_bench - mjsp,
                   mjsp,
                   ghg_foss
  ])