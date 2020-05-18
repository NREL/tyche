# Biorefinery model with four processing steps


# All of the computations must be vectorized, so use `numpy`.
import numpy as np


# Capital-cost function.
def capital_cost(scale, parameter):
    return np.stack([
        parameter[3],
        parameter[4],
        parameter[5],
        parameter[6],
    ])


# Fixed-cost function.
def fixed_cost(scale, parameter):
    return np.stack([
        parameter[7],
        parameter[8],
    ])


# Production function.
def production(scale, capital, lifetime, fixed, input, parameter):

    # input efficiency (preprocessing efficiency) is accounted for in Designs.py
    # ditto output efficiency (separation efficiency)
    # so only fermentation efficiency (parameter[0]) and conversion efficiency
    # (parameter[1]) is seen in this equation
    out = input[0] * parameter[0] * parameter[1]

    # Package results.
    return out


# Metrics function.
def metrics(scale, capital, lifetime, fixed, input_raw, input, output_raw, output, cost, parameter):

    return np.vstack([parameter[2]])
