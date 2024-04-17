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
    _cap = parameter[0]

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
  _fix = parameter[2]

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

  conversion_factor = parameter[2]
  stover_flow = input[0]
  _jet = conversion_factor*stover_flow

  # Stack the output for each category into a single array that we return.
  return np.stack([_jet
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
  total_cost = capital[0]/lifetime[0] + fixed[0] + input[0]*input_price[0] + input[1]*input_price[1]

  # Package results.
  return np.stack([total_cost,
    jobs,
    total_ghg
  ])