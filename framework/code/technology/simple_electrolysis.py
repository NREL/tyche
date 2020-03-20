# Simple electrolysis.

import numpy as np


# Production function.
def production(capital, fixed, input, parameter):

  # Moles of input.
  water       = np.divide(input[0], parameter[2])
  electricity = np.divide(input[1], parameter[3])

  # Moles of output.
  output = np.minimum(water, electricity)

  # Grams of output.
  oxygen   = np.multiply(output, parameter[0])
  hydrogen = np.multiply(output, parameter[1])

  # Package results.
  return np.vstack([oxygen, hydrogen])


# Metrics function.
def metrics(capital, fixed, input, outputs, parameter):

  # Trivial jobs calculation.
  jobs = parameter[4]

  # Package results.
  return np.vstack([jobs])
