"""
Simple residential PV.
"""


# All of the computations must be vectorized, so use `numpy`.
import numpy as np


def discount(rate, time):
  """
  Discount factor over a time period.

  Parameters
  ----------
  rate : float
    The discount rate per time period.
  time : int
    The number of time periods.
  """
  return 1 / (1 + rate)**time


def npv(rate, time):
  """
  Net present value of constant cash flow.

  Parameters
  ----------
  rate : float
    The discount rate per time period.
  time : int
    The number of time periods.
  """
  return (1 - 1 / (1 + rate)**(time + 1)) / (1 - 1 / (1 + rate))


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

  # For readability, copy the parameter vectors to named variables.
  dr  = parameter[ 0]
  ins = parameter[ 1]
  ssz = parameter[ 2]
  mcc = parameter[ 3]
  mlt = parameter[ 4]
  mef = parameter[ 5]
  icc = parameter[11]
  ilt = parameter[12]
  irc = parameter[13]
  bcc = parameter[16]
  blr = parameter[17]
  bpr = parameter[18]
  bca = parameter[19]
  boh = parameter[20]

  # System module capital cost. 
  smcxa = ssz * mcc 

  # System inverter capital cost.
  sicxa = ins * ssz * mef * icc

  # One inverter replacement.
  rsicxa1 = (mlt > ilt) * (mlt < 2 * ilt) * \
            (discount(dr, ilt) - (2 * ilt - mlt) / ilt * discount(dr, mlt))

  # Two inverter replacements.
  rsicxa2 = (mlt > 2 * ilt) * (mlt < 3 * ilt) * \
            (discount(dr, ilt) + discount(dr, 2 * ilt) - (3 * ilt - mlt) / ilt * discount(dr, mlt))

  # Capital cost of all inverters.
  # FIXME: Generalize to an arbitrary number of inverter replacements.
  sicxa = sicxa * (1 + irc * (rsicxa1 + rsicxa2))

  # System BOS hardware cost.
  sbh = bcc * ssz

  # System BOS soft costs for labor, permitting, and customers.
  sbs = blr + bpr + bca

  # System overhead costs.
  soh = boh * (smcxa + sicxa + sbh + sbs)

  # Return the capital costs.
  return np.stack([
    smcxa          , # module
    sicxa          , # inverters
    sbh + sbs + soh, # balance of system
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

  # For readability, copy the parameter vectors to named variables.
  dr  = parameter[ 0]
  ins = parameter[ 1]
  ssz = parameter[ 2]
  mlt = parameter[ 4]
  mef = parameter[ 5]
  mom = parameter[ 7]

  # System lifetime overhead costs.
  return np.stack([
    mom * ins / 1000 * ssz * mef * npv(dr, mlt)
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

  # For readability, copy the parameter vectors to named variables.
  ins = parameter[ 1]
  ssz = parameter[ 2]
  mlt = parameter[ 4]
  mef = parameter[ 5]
  map = parameter[ 6]
  mdr = parameter[ 8]
  mcf = parameter[ 9]
  msl = parameter[10]
  ief = parameter[14]

  # System lifetime energy conversion.
  return np.stack([
    ins / 1000 * 24 * 365 * ssz * map * mcf * mef * ief * (1 - msl) * npv(mdr / (1 - mdr), mlt)
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

  # For readability, copy the parameter vectors to named variables.
  blr = parameter[17]

  # Levelized cost of energy.
  return np.stack([
    0.106125 - cost / output[0]            , # delta LCOE from base
    blr - 2000.077451                      , # delta labor expenses from base
    0.4490564e-3 * output[0] - 82.676202217, # delta GHG from base
  ])
