# Simple electrolysis.


# Production function.
def production(capital, fixed, inputs, parameters):

  # Moles of inputs.
  water       = inputs[0] / parameters[2]
  electricity = inputs[1] / parameters[3]

  # Moles of output.
  output = min(water, electricity)

  # Grams of output.
  oxygen   = output * parameters[0]
  hydrogen = output * parameters[1]

  # Package results.
  return [oxygen, hydrogen]


# Metrics function.
def metrics(capital, fixed, inputs, outputs, parameters):

  # Trivial jobs calculation.
  jobs = parameters[4]

  # Package results.
  return [jobs]
