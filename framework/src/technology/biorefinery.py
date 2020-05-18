# Biorefinery model with four processing steps


# All of the computations must be vectorized, so use `numpy`.
import numpy as np


# Production function.
def production(capital, fixed, input, parameter):

    # input efficiency (preprocessing efficiency) is accounted for in Designs.py
    # ditto output efficiency (separation efficiency)
    # so only fermentation efficiency (parameter[0]) and conversion efficiency
    # (parameter[1]) is seen in this equation
    out = input[0] * parameter[0] * parameter[1]

    # Package results.
    return out


# Metrics function.
def metrics(capital, fixed, input, outputs, parameter):

    return np.vstack([parameter[2]])