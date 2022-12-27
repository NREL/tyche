"""
Simple pv utility-scale module example.  Inspired by Kavlak et al. Energy Policy 123 (2018) 700–710.
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

    # Unit conversions.
    um_to_cm = 0.0001
    kg_to_g = 1000

    # Si materials cost.
    si_costs = np.divide(parameter[0]*parameter[1]*parameter[2]*parameter[3]*parameter[4],
                        parameter[5]
                    )
    si_costs = np.divide(np.multiply(um_to_cm, si_costs), kg_to_g)

    # Non-Si materials cost.
    non_si_costs = parameter[0]*parameter[1]*parameter[6]

    # Plant-size dependent costs (non-materials cost).
    plant_scale = np.divide(parameter[8], parameter[9])
    plant_costs = parameter[0]*parameter[7]*np.power(plant_scale, parameter[10])
                        
                    

    # Sum component costs.
    out = np.sum([si_costs, non_si_costs, plant_costs])
    # Package results.
    return np.stack([out])


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

    # Currently, no fixed costs in the model.
    return np.stack([0])


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

    # Module electricity (kWh) production.
    cm2_per_m2 = 10000

    kWh_per_day = np.divide(
                        np.prod(
                            [
                                input[0],
                                parameter[0],
                                parameter[1],
                                parameter[11]
                            ]
                        ),
                        np.prod([parameter[12], cm2_per_m2])
                    )

    num = np.multiply(input[0],np.multiply(np.multiply(parameter[0],parameter[1]),parameter[11]))
    dem = np.multiply(parameter[12], cm2_per_m2)
    kWh_per_day = num/dem
    kwh_per_module = np.prod([kWh_per_day, 365, lifetime])

    # Package results.
    return np.stack([kwh_per_module])


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

    # kWh output over lifetime.
    kwh = output[0]

    # LCOE ($/kWh).
    lcoe = np.divide(cost, kwh)

    # GHGs saved by displacing grid electricity.
    co2e = np.multiply(kwh, parameter[13])

    # Package results.
    return np.stack([lcoe, co2e])
