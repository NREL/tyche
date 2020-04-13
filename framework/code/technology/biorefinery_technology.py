# Biorefinery model with four processing steps


# All of the computations must be vectorized, so use `numpy`.
import numpy as np


# Production function.
def production(capital, fixed, input, parameter):

  # Package results.
  return 1.0


# Metrics function.
def metrics(capital, fixed, input, outputs, parameter):

    return np.vstack([parameter[2]])