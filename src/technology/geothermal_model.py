"""
Geothermal model.
"""

# All of the computations must be vectorized, so use `numpy`.
from matplotlib import scale
import numpy as np


def capital_cost(scale, atb):
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

    occ = scale * atb.extract_values(parameter = 'OCC') 
    gcc = scale * atb.extract_values(parameter = 'GCC') 
    capex = scale * atb.extract_values(parameter = 'CAPEX') 

    # TODO: check if we need this value
    # cff = capex / (occ + gcc)

    return np.stack([occ, gcc, capex])

def fixed_cost(scale, atb):
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
