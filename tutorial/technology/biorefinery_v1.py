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

    Returns
    -------
    Total capital cost for one biorefinery (USD/biorefinery)
    """
    # "original" biorefinery scale
    o_scale = parameter[10]

    # scaling factor for equipment costs
    scale_factor = parameter[11]

    pre = parameter[3] * (scale / o_scale) ** scale_factor
    fer = parameter[4] * (scale / o_scale) ** scale_factor
    con = parameter[5] * (scale / o_scale) ** scale_factor
    sep = parameter[6] * (scale / o_scale) ** scale_factor
    utl = parameter[7] * (scale / o_scale) ** scale_factor

    return np.stack([pre, fer, con, sep, utl])


def fixed_cost(scale, parameter):
    """
    Fixed cost function.

    Parameters
    ----------
    scale : float [Unused]
      The scale of operation.
    parameter : array
      The technological parameterization.

    Returns
    -------
    total fixed costs for one biorefinery (USD/year)
    """
    o_scale = parameter[10]

    rnt = parameter[8] * (scale / o_scale)
    ins = parameter[9] * (scale / o_scale)

    return np.stack([rnt, ins])


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

    Returns
    -------
    output_raw
        Ideal/theoretical production of each technology output: biofuel at
        gals/year
    """

    theor_yield = parameter[12]
    feedstock = input[0] * scale

    # theoretical biofuel yield w/out any efficiency losses
    output_raw = theor_yield * feedstock

    return np.stack([output_raw])



def metrics(scale, capital, lifetime, fixed, input_raw, input, output_raw, output, cost, parameter):
    """
    Metrics function.

    Parameters
    ----------
    scale : float
      The scale of operation. Unitless
    capital : array
      Capital costs. Units: USD/biorefinery
    lifetime : float
      Technology lifetime. Units: year
    fixed : array
      Fixed costs. Units: USD/year
    input_raw : array
      Raw input quantities (before losses). Units: metric ton feedstock/year
    input : array
      Input quantities. Units: metric ton feedstock/year
    output_raw : array
      Raw output quantities (before losses). Units: gal biofuel/year
    output : array
      Output quantities. Units: gal biofuel/year
    cost : array
      Costs.
    parameter : array
      The technological parameterization. Units vary; given in comments below
    """

    # JOBS: person-hours/gal biofuel
    # parameter[2] units: person-hours/year
    # output units: gal biofuel/year
    emp = parameter[2] / output

    # FOSSIL GHG: kg CO2-eq/gal biofuel
    # parameter[0] units: kg CO2-eq/year
    # output units: gal biofuel/year
    ghg_foss = parameter[0] / output

    # TOTAL GHG: kg CO2-eq/gal biofuel
    # parameter[0] and parameter[1] units: kg CO2-eq/year
    # output units: gal biofuel/year
    ghg_tot = (parameter[0] + parameter[1]) / output

    return np.stack([emp, ghg_foss, ghg_tot])
