# Residential PV


#  CAPITAL
#
#  systemModuleCapital   = capital[0[ # $/system
#  systemInverterCapital = capital[1] # $/system
#  systemBalanceCapital  = capital[2] # $/system

#  FIXED
#
#  systemFixed = fixed[0] # $/system

#  INPUTS
#
#  strategicMetals = input[0] # g/system

#  OUTPUTS
#
#  lifetimeEnergy = output[0] # kWh/system
#  hazardousWaste = output[1] # g/system
#  greenhouseGas  = output[2] # gCO2e/system

#  METRICS
#
#  levelizedCapacityCost = metric[0] # $/Wdc
#  levelizedEnergyCost   = metric[1] # $/kWh
#  greenhouseGas         = metric[2] # gCO2e/kWh
#  strategicMetal        = metric[3] # g/kWh
#  hazardousWaste        = metric[4] # g/kWh
#  specificYield         = metric[5] # hr/yr
#  moduleEfficiency      = metric[6] # %/100
#  moduleLifetime        = metric[7] # yr

#  PARAMETERS
#
#  discountRate            = parameter[ 0] # 1/yr
#  insolation              = parameter[ 1] # W/m^2
#  systemSize              = parameter[ 2] # m^2
#  moduleCapitalCost       = parameter[ 3] # $/m^2
#  moduleLifetime          = parameter[ 4] # yr
#  moduleEfficiency        = parameter[ 5] # %/100
#  moduleAperture          = parameter[ 6] # %/100
#  moduleFixedCost         = parameter[ 7] # $/kW/yr
#  moduleDegradationRate   = parameter[ 8] # 1/yr
#  locationCapacityFactor  = parameter[ 9] # %/100
#  moduleSoilingLoss       = parameter[10] # %/100
#  inverterCapitalCost     = parameter[11] # $/W
#  inverterLifetime        = parameter[12] # yr
#  inverterReplacementCost = parameter[13] # %/100
#  inverterEfficiency      = parameter[14] # %/100
#  hardwareCapitalCost     = parameter[15] # $/m^2
#  installationLaborCost   = parameter[16] # $/system
#  permittingCost          = parameter[17] # $/system
#  customerAcquisitionCost = parameter[18] # $/system
#  installerOverheadCost   = parameter[19] # %/100
#  hazardousWasteContent   = parameter[20] # g/m^2
#  greenhouseGasOffset     = parameter[21] # gCO2e/kWh
#  benchmarkLCOC           = parameter[22] # $/Wdc
#  benchmarkLCOE           = parameter[23] # $/kWh

# All of the computations must be vectorized, so use `numpy`.
import numpy as np


# Discount at a rate for a time.
def discount(rate, time):
  return 1 / (1 + rate)**time


# Net present value of constant cash flow.
def npv(rate, time):
  return (1 - 1 / (1 + rate)**(time + 1)) / (1 - 1 / (1 + rate))


# Nominal module energy production.
def module_power(parameter):
  insolation       = parameter[ 1] # W/m^2
  systemSize       = parameter[ 2] # m^2
  moduleEfficiency = parameter[ 5] # %/100
  return (insolation / 1000) * systemSize * moduleEfficiency


# Performance ratio for the system.
def performance_ratio(parameter):
  moduleLifetime         = parameter[ 4] # yr
  moduleAperture         = parameter[ 6] # %/100
  moduleDegradationRate  = parameter[ 8] # 1/yr
  moduleSoilingLoss      = parameter[10] # %/100
  inverterEfficiency     = parameter[14] # %/100
  return (
    moduleAperture
    * inverterEfficiency
    * (1 - moduleSoilingLoss)
    * npv(moduleDegradationRate / (1 - moduleDegradationRate), moduleLifetime)
    / moduleLifetime
  )


# Specific yield for the system.
def specific_yield(parameter):
  locationCapacityFactor = parameter[ 9] # %/100
  return 8760 * locationCapacityFactor * performance_ratio(parameter)


# Capital-cost function.
def capital_cost(scale, parameter):

  # For readability, copy the parameter vectors to named variables.
  discountRate            = parameter[ 0] # 1/yr
  insolation              = parameter[ 1] # W/m^2
  systemSize              = parameter[ 2] # m^2
  moduleCapitalCost       = parameter[ 3] # $/m^2
  moduleLifetime          = parameter[ 4] # yr
  moduleEfficiency        = parameter[ 5] # %/100
  inverterCapitalCost     = parameter[11] # $/W
  inverterLifetime        = parameter[12] # yr
  inverterReplacementCost = parameter[13] # %/100
  hardwareCapitalCost     = parameter[15] # $/m^2
  installationLaborCost   = parameter[16] # $/system
  permittingCost          = parameter[17] # $/system
  customerAcquisitionCost = parameter[18] # $/system
  installerOverheadCost   = parameter[19] # %/100

  # System module capital cost. 
  systemModuleCapital = systemSize * moduleCapitalCost 

  # System inverter capital cost.
  systemInverterCapital = insolation * systemSize * moduleEfficiency * inverterCapitalCost

  # One inverter replacement.
  inverterReplacement1 = (
    (moduleLifetime > inverterLifetime)
    * (moduleLifetime < 2 * inverterLifetime)
    * (
      discount(discountRate, inverterLifetime) -
      (2 * inverterLifetime - moduleLifetime)
      / inverterLifetime
      * discount(discountRate, moduleLifetime)
    )
  )

  # Two inverter replacements.
  inverterReplacement2 = (
    (moduleLifetime > 2 * inverterLifetime)
    * (moduleLifetime < 3 * inverterLifetime)
    * (
      discount(discountRate, inverterLifetime)
      + discount(discountRate, 2 * inverterLifetime)
      - (3 * inverterLifetime - moduleLifetime)
      / inverterLifetime
      * discount(discountRate, moduleLifetime)
    )
  )

  # Capital cost of all inverters.
  # FIXME: Generalize to an arbitrary number of inverter replacements.
  systemInverterCapital = systemInverterCapital * (1 + inverterReplacementCost * (
    inverterReplacement1 + inverterReplacement2
  ))

  # System BOS hardware cost.
  systemHardwareCapital = hardwareCapitalCost * systemSize

  # System BOS soft costs for labor, permitting, and customers.
  systemSoftCosts = installationLaborCost + permittingCost + customerAcquisitionCost

  # System overhead costs.
  systemOverheadCost = installerOverheadCost * (
    systemModuleCapital
    + systemInverterCapital
    + systemHardwareCapital
    + systemSoftCosts
  )

  # All capital costs.
  return np.stack([
    systemModuleCapital                                         , # module
    systemInverterCapital                                       , # inverters
    systemHardwareCapital + systemSoftCosts + systemOverheadCost, # balance of system
  ])


# Fixed-cost function.
def fixed_cost(scale, parameter):

  # For readability, copy the parameter vectors to named variables.
  discountRate     = parameter[ 0] # 1/yr
  moduleLifetime   = parameter[ 4] # yr
  moduleFixedCost  = parameter[ 7] # $/kW/yr

  # System lifetime fixed costs.
  return np.stack([
    moduleFixedCost * module_power(parameter) * npv(discountRate, moduleLifetime)
  ])


# Production function.
def production(scale, capital, lifetime, fixed, input, parameter):

  # For readability, copy the parameter vectors to named variables.
  systemSize             = parameter[ 2] # m^2
  moduleLifetime         = parameter[ 4] # yr
  hazardousWasteContent  = parameter[20] # g/m^2
  greenhouseGasOffset    = parameter[21] # gCO2e/kWh

  # Lifetime energy production.
  lifetimeEnergy = module_power(parameter) * specific_yield(parameter) * moduleLifetime

  # All outputs.
  return np.stack([
    lifetimeEnergy                      , # lifetime energy
    hazardousWasteContent * systemSize  , # hazardous waste
    greenhouseGasOffset * lifetimeEnergy, # greenhouse gas
  ])


# Metrics function.
def metrics(scale, capital, lifetime, fixed, input_raw, input, output_raw, output, cost, parameter):

  # For readability, copy the parameter vectors to named variables.
  moduleLifetime   = parameter[ 4] # yr
  moduleEfficiency = parameter[ 5] # %/100
  benchmarkLCOC    = parameter[22] # $/Wdc	
  benchmarkLCOE    = parameter[23] # $/kWh	
  strategicMetal   = input_raw[0]  # g/system
  lifetimeEnergy   = output[0]     # kWh/system
  hazardousWaste   = output[1]     # g/system
  greenhouseGas    = output[2]     # gCO2e/system

  # All metrics.
  return np.stack([
    benchmarkLCOC - cost / module_power(parameter) , # levelized cost of capacity
    benchmarkLCOE - cost / lifetimeEnergy          , # levelized cost of energy
    - greenhouseGas / lifetimeEnergy               , # greenhouse gas
    strategicMetal / lifetimeEnergy                , # strategic metal
    hazardousWaste / lifetimeEnergy                , # hazardous waste
    specific_yield(parameter)                      , # specific yield
    moduleEfficiency                               , # module efficiency
    moduleLifetime                                 , # module lifetime
  ])
