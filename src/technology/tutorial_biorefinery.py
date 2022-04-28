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



def metrics(scale, capital, lifetime, fixed, input_raw, input, input_price, output_raw, output, cost, parameter):
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
    input_price : array`
        Array of input prices. Various units.
    output_raw : array
      Raw output quantities (before losses). Units: gal biofuel/year
    output : array
      Output quantities. Units: gal biofuel/year
    cost : array
      Costs.
    parameter : array
      The technological parameterization. Units vary; given in comments below
    """

    # annual fossil GHG emissions, Units: kg CO2-eq/year
    ghg_foss_ann = parameter[0]
    # annual biogenic GHG emissions, Units: kg CO2-eq/year
    ghg_bio_ann  = parameter[1]
    # Annual person-hours required, Units: person-hours/year
    emp_ann      = parameter[2]
    # Preprocessing capital cost, Units: USD
    pre_cap      = parameter[3]
    # Fermentation capital cost, Units: USD
    fer_cap      = parameter[4]
    # Conversion capital cost, Units: USD
    con_cap      = parameter[5]
    # Separations capital cost, Units: USD
    sep_cap      = parameter[6]
    # Utilities capital cost, Units: USD
    utl_cap      = parameter[7]
    # Annual rent, Units: USD/year
    rnt_ann      = parameter[8]
    # Annual insurance, Units: USD/year
    ins_ann      = parameter[9]
    # Discount rate, Unitless
    dr           = parameter[13]
    # Depreciation period for all equipment except utilities, Units: years
    dp           = parameter[14]
    # Depreciation period for utilities, Units: years
    dpu          = parameter[15]
    # Income tax rate, Units: years
    tr           = parameter[16]
    # equipment lifetime
    els          = lifetime[0]

    # JOBS: person-hours/gal biofuel
    # parameter[2] units: person-hours/year
    # output units: gal biofuel/year
    emp = emp_ann / output

    # FOSSIL GHG: kg CO2-eq/gal biofuel
    # parameter[0] units: kg CO2-eq/year
    # output units: gal biofuel/year
    ghg_foss = ghg_foss_ann / output

    # TOTAL GHG: kg CO2-eq/gal biofuel
    # parameter[0] and parameter[1] units: kg CO2-eq/year
    # output units: gal biofuel/year
    ghg_tot = (ghg_foss_ann + ghg_bio_ann) / output

    # MINIMUM FUEL SELLING PRICE: USD/gal biofuel
    # total project investment, Units: USD
    # sum of all capital costs
    tpi = pre_cap + fer_cap + con_cap + sep_cap + utl_cap

    # depreciation costs, units: USD/year
    dc = (pre_cap + fer_cap + con_cap + sep_cap) / dp + utl_cap / dpu

    # operating costs, units: USD/year
    oc = input_raw[0] * input_price[0] + input_raw[1] * input_price[1] + rnt_ann + ins_ann

    # tpi discount factor, Units: unitless
    df_tpi = (dr * (1 + dr) ** els) / ((1 + dr) ** els - 1)

    # total revenue from biofuel sales, Units: USD/year
    br = ((1 - tr) * oc - tr * dc + df_tpi * tpi) / (1 - tr)

    # MFSP, Units: USD/gal biofuel
    mfsp = br / output

    return np.stack([emp, ghg_foss, ghg_tot, mfsp])
