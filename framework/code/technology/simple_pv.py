# Simple pv module example.
# Inspired by Kavlak et al. Energy Policy 123 (2018) 700–710


# All of the computations must be vectorized, so use `numpy`.
import numpy as np


# Capital-cost function.
def capital_cost(scale, parameter):
    """Function to calculate the capital cost of the PV module"""

    # Si materials cost.
    si_costs = np.divide(np.prod(parameter[0:4]), parameter[5])

    # Non-Si materials cost.
    non_si_costs = np.prod([parameter[0], parameter[1], parameter[6]])

    # Plant-size dependent costs (non-materials cost).
    plant_scale = np.divide(parameter[8], parameter[9])
    plant_costs = np.prod(
                        [
                            parameter[0],
                            parameter[7],
                            np.power(plant_scale, parameter[10])
                        ]
                    )

    # Sum component costs.
    out = np.sum([si_costs, non_si_costs, plant_costs])
    
    # Package results.
    return np.stack([out])


# Fixed-cost function.
def fixed_cost(scale, parameter):
    """Function to calculate fixed costs of the PV module"""

    # Currently, no fixed costs in the model.
    return np.stack([0])


# Production function.
def production(scale, capital, lifetime, fixed, input, parameter):
    """Function to compute the electricity output from the module"""

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

    kwh_per_module = np.prod([kWh_per_day, 365, lifetime])

    # Package results.
    return np.stack([kwh_per_module])


# Metrics function.
def metrics(scale, capital, lifetime, fixed, input_raw, input, output_raw, output, cost, parameter):
    """Function to calculate metrics for the PV module"""

    # kWh output over lifetime.
    kwh = output[0]

    # LCOE ($/kWh).
    lcoe = np.divide(cost, kwh)

    # GHGs saved by displacing grid electricity.
    co2e = np.multiply(kwh, parameter[13])

    # Package results.
    return np.stack([lcoe, co2e])
