"""
Generic model for residential PV.

This PV model tracks components, technologies, critical materials, and hazardous waste.


.. table:: Elements of ``capital`` arrays.

   ===== ===================== ========
   Index Description           Units
   ===== ===================== ========
   0     module capital cost   $/system
   1     inverter capital cost $/system
   2     balance capital cost  $/system
   ===== ===================== ========


.. table:: Elements of ``fixed`` arrays.

   ===== =========== ========
   Index Description Units
   ===== =========== ========
   0     fixed cost  $/system
   ===== =========== ========


.. table:: Elements of ``input`` arrays.

   ===== ================ ========
   Index Description       Units
   ===== ================ ========
   0     strategic metals g/system
   ===== ================ ========


.. table:: Elements of ``output`` arrays.

   ===== ================================== ============
   Index Description                        Units
   ===== ================================== ============
   0     lifetime energy production         kWh/system
   1     lifecycle hazardous waste          g/system
   2     lifetime greenhouse gas production gCO2e/system
   ===== ================================== ============


.. table:: Elements of ``metric`` arrays.

   ===== ===================== =========
   Index Description           Units
   ===== ===================== =========
   0     system cost           $/Wdc
   1     levelized energy cost $/kWh
   2     greenhouse gas        gCO2e/kWh
   3     strategic metal       g/kWh
   4     hazardous waste       g/kWh
   5     specific yield        hr/yr
   6     module efficiency     %/100
   7     module lifetime       yr
   ===== ===================== =========


.. table:: Elements of ``parameter`` arrays.

   ===== ========================= =========
   Index Description               Units
   ===== ========================= =========
   0     discount rate             1/yr
   1     insolation                W/m^2
   2     system size               m^2
   3     module capital cost       $/m^2
   4     module lifetime           yr
   5     module efficiency         %/100
   6     module aperture           %/100
   7     module fixed cost         $/kW/yr
   8     module degradation rate   1/yr
   9     location capacity factor  %/100
   10    module soiling loss       %/100
   11    inverter capital cost     $/W
   12    inverter lifetime         yr
   13    inverter replacement cost %/100
   14    inverter efficiency       %/100
   15    hardware capital cost     $/m^2
   16    installation labor cost   $/system
   17    permitting cost           $/system
   18    customer acquisition cost $/system
   19    installer overhead cost   %/100
   20    hazardous waste content   g/m^2
   21    greenhouse gas offset     gCO2e/kWh
   22    benchmark LCOC            $/Wdc
   23    benchmark LCOE            $/kWh
   ===== ========================= =========
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


def module_power(parameter):
  """
  Nominal module energy production.

  Parameters
  ----------
  parameter : array
    The technological parameterization.
  """
  insolation       = parameter[ 1] # W/m^2
  systemSize       = parameter[ 2] # m^2
  moduleEfficiency = parameter[ 5] # %/100
  return (insolation / 1000) * systemSize * moduleEfficiency


def performance_ratio(parameter):
  """
  Performance ratio for the system.

  Parameters
  ----------
  parameter : array
    The technological parameterization.
  """
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


def specific_yield(parameter):
  """
  Specific yield for the system.

  Parameters
  ----------
  parameter : array
    The technological parameterization.
  """
  locationCapacityFactor = parameter[ 9] # %/100
  return 8760 * locationCapacityFactor * performance_ratio(parameter)


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
  discountRate     = parameter[ 0] # 1/yr
  moduleLifetime   = parameter[ 4] # yr
  moduleFixedCost  = parameter[ 7] # $/kW/yr

  # System lifetime fixed costs.
  return np.stack([
    moduleFixedCost * module_power(parameter) * npv(discountRate, moduleLifetime)
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
    benchmarkLCOC - sum(capital) / module_power(parameter) / 1000, # system cost
    benchmarkLCOE - cost / lifetimeEnergy                        , # levelized cost of energy
    - greenhouseGas / lifetimeEnergy                             , # greenhouse gas
    strategicMetal / lifetimeEnergy                              , # strategic metal
    hazardousWaste / lifetimeEnergy                              , # hazardous waste
    specific_yield(parameter)                                    , # specific yield
    moduleEfficiency                                             , # module efficiency
    moduleLifetime                                               , # module lifetime
  ])
