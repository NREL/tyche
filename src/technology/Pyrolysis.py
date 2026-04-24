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
    FP_design_param = parameter[0]
    VU_design_param = parameter[1]
    Condensation_design_param = parameter[2]
    PS_design_param = parameter[3]
    BOS_design_param = parameter[10]

    # Placeholder equations. 
    # Adjusting the design parameter will reduce capex in that category up to 95%.
    Fast_Pyrolysis_capex = 112878000 - (0.95 * 112878000 * (1-FP_design_param))
    Vapor_Upgrading_capex = 73724000 - (0.95 * 73724000 * (1-VU_design_param))
    Condensation_capex = 18425000 - (0.95 * 18425000 * (1-Condensation_design_param))
    Product_Separation_capex = 42786000 - (0.95 * 42786000 * (1-PS_design_param))
    BOS_capex = 958684 - (0.95 * 958684 * (1- BOS_design_param))

    # Stack the costs for each category into a single array that we return.
    return np.stack([Fast_Pyrolysis_capex,
                     Vapor_Upgrading_capex,
                     Condensation_capex,
                     Product_Separation_capex,
                     BOS_capex
    ])

def fixed_cost(scale, parameter):
    """
    Capital cost function.

    Parameters
    ----------
    scale : float
        The scale of operation.
    parameter : array
        The technological parameterization.
    """

    FP_design_param = parameter[0]
    VU_design_param = parameter[1]
    Condensation_design_param = parameter[2]
    PS_design_param = parameter[3]
    BOS_design_param = parameter[10]


    fixed_costs = 39617000 #$/year

  # Stack the costs for each category into a single array that we return.
    return np.stack([
        fixed_costs
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
    FP_design_param = parameter[0]
    VU_design_param = parameter[1]
    Condensation_design_param = parameter[2]
    PS_design_param = parameter[3]
    jet_conversion_factor = parameter[4] #unitless; kg jet per kg biomass
    jet_fuel_energy_content = parameter[5] #MJ/kg
    diesel_energy_content = 45.8 #MJ/kg
    gasoline_energy_content = 45.6 #MJ/kg
    diesel_conversion_factor = parameter[8] #unitless
    gasoline_conversion_factor = parameter[9] #unitless
    biomass_flow = input[0] #lb/h
     
    # Jet efficiency factors for each component at base (scales with jet conversion factor given in parameters)
    # Placeholder values - update as needed
    base_FP_efficiency = 0.2
    base_VU_efficiency = 0.8
    base_Condensation_efficiency = 0.9
    base_PS_efficiency = 0.85
    total_base_efficiency = base_FP_efficiency*base_VU_efficiency*base_Condensation_efficiency*base_PS_efficiency

    # Setting the base efficiencies so that total base efficiency is equal to the jet conversion factor specified in parameters.
    base_scale_factor = jet_conversion_factor/total_base_efficiency 

    base_FP_efficiency = base_FP_efficiency * base_scale_factor
    base_VU_efficiency = base_VU_efficiency * base_scale_factor
    base_Condensation_efficiency = base_Condensation_efficiency * base_scale_factor
    base_PS_efficiency = base_PS_efficiency * base_scale_factor

    # Maximum theoretical efficiencies for each component
    # Placeholder values - update as needed
    max_FP_efficiency = 0.5
    max_VU_efficiency = 0.9
    max_Condensation_efficiency = 0.95
    max_PS_efficiency = 0.9

    # Jet fuel efficiency adjusted based on design parameter:
    # Efficiencies for each component are an exponential approach function.
    FP_jet_efficency = max_FP_efficiency - (max_FP_efficiency-base_FP_efficiency)*np.exp(-10*(1-FP_design_param))
    VU_jet_efficency = max_VU_efficiency - (max_VU_efficiency-base_VU_efficiency)*np.exp(-10*(1-VU_design_param))
    Condensation_jet_efficency = max_Condensation_efficiency - (max_Condensation_efficiency-base_Condensation_efficiency)*np.exp(-10*(1-Condensation_design_param))
    PS_jet_efficency = max_PS_efficiency - (max_PS_efficiency-base_PS_efficiency)*np.exp(-10*(1-PS_design_param))
    
    total_jet_efficiency = FP_jet_efficency * VU_jet_efficency * Condensation_jet_efficency * PS_jet_efficency
    jet_output = biomass_flow * total_jet_efficiency * 0.4535924 #lb to kg # units of kg/h

    # Diesel and gasoline efficiencies are set as a fraction of biomass not converted to jet.
    # This means they decrease as jet efficiency increases.
    diesel_scale_factor = (1-total_jet_efficiency)/(1-total_base_efficiency)

    diesel_output = biomass_flow * diesel_scale_factor * diesel_conversion_factor * 0.4535924 #lb to kg # units of kg/h
    gasoline_output = biomass_flow * diesel_scale_factor * gasoline_conversion_factor * 0.4535924 #lb to kg # units of kg/h

    # Stack the output for each category into a single array that we return.
    # Multiplied by 8000 to get annual.
    return np.stack([jet_output * 8000,
                     gasoline_output * 8000,
                     diesel_output* 8000                     
    ]) #units of kg/year


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
  FP_design_param = parameter[0]
  VU_design_param = parameter[1]
  Condensation_design_param = parameter[2]
  PS_design_param = parameter[3]
  jet_conversion_factor = parameter[4] #unitless
  jet_fuel_energy_content = parameter[5] #MJ/kg
  diesel_conversion_factor = parameter[8] #unitless
  gasoline_conversion_factor = parameter[9] #unitless
  ghg_ef = parameter[6] #gco2eq./MJ
  biomass_flow = input[0] #lb/h
  hydrogen_flow = input[1] #lb/h
  steam_flow = input[2] #lb/h
  catalyst_flow = input[3] #lb/h
  biomass_price = input_price[0] #$/lb
  hydrogen_price = input_price[1]
  steam_price = input_price[2]
  catalyst_price = input_price[3]
  job_factor = parameter[7]

  # Adjusting amount of catalyst needed with FP investment
  catalyst_flow_adjusted = catalyst_flow*VU_design_param
  # Annual fossil GHG emissions, Units: g CO2-eq/year
  biomass_flow_kg_h = biomass_flow * 0.4535924 #lb to kg
  biomass_flow_kg_year = biomass_flow_kg_h * 8000
  jet_kg_produced_per_year = output[0]
  jet_energy_produced = jet_kg_produced_per_year * jet_fuel_energy_content #MJ/year
  jet_ghg_from_burn = jet_energy_produced * ghg_ef  #gCO2-eq/year
  
  gasoline_kg_produced_per_year = output[1]
  diesel_kg_produced_per_year = output[2]

  # Jobs - assuming that number of jobs scales exponentially with technology development
  # With a random factor in exp differentiating each component - update as needed
  total_jobs = job_factor*(np.exp(1*(1-FP_design_param)) + np.exp(1*(1-VU_design_param)) + np.exp(1*(1.2-Condensation_design_param)) + np.exp(1.5*(1-PS_design_param)))
  # GHGs
  total_carbon_efficiency = (jet_kg_produced_per_year*0.82 + 
                             gasoline_kg_produced_per_year*0.9 + 
                             diesel_kg_produced_per_year*0.8)/(biomass_flow_kg_year*0.5) #factors are the carbon % by mass
  # Now assuming all lost carbon is CO2 [not true, can update with fracton of char]
  total_carbon_lost_kg = (1-total_carbon_efficiency)*biomass_flow_kg_year
  total_co2_lost_kg = total_carbon_lost_kg * 3.6 #assuming all C is oxidised to CO2
  total_co2_lost_g = total_co2_lost_kg * 1000
  
  total_GHG_per_jet = (jet_ghg_from_burn + total_co2_lost_g)/jet_kg_produced_per_year

  # Total cost per year
  # Note that using using numpy sum function gives unexpected results. Use native sum.
  # Scaling fixed costs with jobs
  fixed_costs = fixed[0] + fixed[0]*(total_jobs/job_factor)*0.15

  total_cost_yearly = sum(capital)/lifetime[0] + fixed_costs + 8000*(biomass_flow*biomass_price + 
                                                              hydrogen_flow*hydrogen_price + 
                                                              steam_flow*steam_price + 
                                                              catalyst_flow_adjusted*catalyst_price
                                                              ) #$/year
  total_cost_per_kg = total_cost_yearly/jet_kg_produced_per_year

  # Package results.
  return np.stack([total_cost_per_kg,
                   total_GHG_per_jet,
                   total_jobs/jet_kg_produced_per_year
                   
  ])