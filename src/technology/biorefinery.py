"""
Biorefinery model with four processing steps.
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
    return np.stack([
        parameter[3],
        parameter[4],
        parameter[5],
        parameter[6],
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
    return np.stack([
        parameter[7],
        parameter[8],
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

    # input efficiency (preprocessing efficiency) is accounted for in Designs.py
    # ditto output efficiency (separation efficiency)
    # so only fermentation efficiency (parameter[0]) and conversion efficiency
    # (parameter[1]) is seen in this equation
    out = input[0] * parameter[0] * parameter[1]

    # Package results.
    return out


def metrics(scale, capital, lifetime, fixed, input_raw, input, output_raw, output, cost, parameter):
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

    return np.vstack([parameter[2]])
