import numpy           as np
#mport numpy_financial as npf


""" 
------ Define Functions for Manufacturing Step Costs -----
"""


def buildingCosts(floorSQF, clean10KSQF, clean1KSQF, clean100SQF, buildingCostSQF, CR10KCost, CR1KCost, CR100Cost):    
    return buildingCostSQF * floorSQF + CR10KCost * clean10KSQF + CR1KCost * clean1KSQF + CR100Cost * clean100SQF


def runtime(productionVol, throughput, downtime, hrs, days): 
    return (productionVol * 1000) / (throughput * hrs * days * (1 - downtime))


def parallelStationCalc(runtimeOneStation, dedicatedEquip):
    return  np.ceil(runtimeOneStation) if dedicatedEquip else runtimeOneStation.copy()


def toolLifeCalc(numParallelStations, toolingLife, effProductionVol, plantLife): 
    toolLives = [plantLife, (numParallelStations * toolingLife / (effProductionVol * 1000))]
    return np.min(toolLives)


def grossIngotWeight(length, weightFraction, diameter):
    return np.pi * ((diameter / 20)**2 * length * 2.33 / 1000 * (1 + weightFraction))


def sizeFilamentBatch(diameter, filamentWidth, kerfLoss):
    size = np.trunc( (np.pi * (diameter / 20)**2) / ( (filamentWidth / 10) + (kerfLoss / 10000) )**2 )
    size = np.trunc(0.9 * size)
    return size

financialsHeader = [
    'Material Cost',
    'Direct Labor Cost',
    'Utility Cost',
    'Equipment Cost',
    'Tooling Cost',
    'Building Cost',
    'Maintenance Cost',
    'Overhead Labor Cost',
    'Cost of Capital'
]

MATERIAL_COST       = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0])
DIRECT_LABOR_COST   = np.array([0, 1, 0, 0, 0, 0, 0, 0, 0])
UTILITY_COST        = np.array([0, 0, 1, 0, 0, 0, 0, 0, 0])
EQUIPMENT_COST      = np.array([0, 0, 0, 1, 0, 0, 0, 0, 0])
TOOLING_COST        = np.array([0, 0, 0, 0, 1, 0, 0, 0, 0])
BUILDING_COST       = np.array([0, 0, 0, 0, 0, 1, 0, 0, 0])
MAINTENANCE_COST    = np.array([0, 0, 0, 0, 0, 0, 1, 0, 0])
OVERHEAD_LABOR_COST = np.array([0, 0, 0, 0, 0, 0, 0, 1, 0])
COST_OF_CAPITAL     = np.array([0, 0, 0, 0, 0, 0, 0, 0, 1])

VARIABLE_COSTS = MATERIAL_COST + DIRECT_LABOR_COST + UTILITY_COST
WORKING_COSTS = VARIABLE_COSTS + MAINTENANCE_COST + OVERHEAD_LABOR_COST
FIXED_COSTS = EQUIPMENT_COST + TOOLING_COST + BUILDING_COST + MAINTENANCE_COST + OVERHEAD_LABOR_COST + COST_OF_CAPITAL

def makeFinancials(
    materialCost      = 0,
    directLaborCost   = 0,
    UtilityCost       = 0,
    equipmentCost     = 0,
    toolingCost       = 0,
    buildingCost      = 0,
    maintenanceCost   = 0,
    overheadLaborCost = 0,
    costOfCapital     = 0,
):
    return np.array(
        [
            materialCost     ,
            directLaborCost  ,
            UtilityCost      ,
            equipmentCost    ,
            toolingCost      ,
            buildingCost     ,
            maintenanceCost  ,
            overheadLaborCost,
            costOfCapital    ,
        ]
    )

def financialSummary(dfs):
    summary = dfs.sum(axis = 0)[0]
    return np.append(summary, summary.sum())


def financialCalculations(capitalInvestment, auxEquipInvest, installFactor, runtimeOneStation, toolinglInvestment, toolSetPerStation, buildingCostperStation, numParallelStations, 
                          totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, operatingPowerConsumption, equipMaintCost, z):
    """
    Calculates the financial summary ($/kg-Poly Si and $/yr) of the manufacturing step. Outputs DataFrame of Values
    
    Returns numpy dataframe object with financial cost summary
    
    Parameters
    ----------
    capitalInvestment : float
        CapEx for the manufacturing process
    auxEquipInvest : float
        Auxilary Equipment for manufacturing process
    installFactor : float
        Installation cost mulitiplier
    runTimeOneStation : float
        Time one manufacturing station takes to run
    toolingInvestment : float
        Capital investment for tools in manufacturing step
    toolSetPerStation : float
        Number of tool sets required for each station
    buildingCostPerStation : float
        Cost of floor space for the station
    numParallelStations : float
        Number of stations required for parallel operation
    totalMaterialCosts : float
        Total cost of all input materials into the process
    unskilledDirectLaborers : float
        Number of unskilled laborers needed
    skilledDirectLaborers : float
        Number of skilled laborers needed
    throughput : float
        Rate of product creation for that manufacturing step
    avgDowntime : float
        Fraction of time the manufacturing equipment is spent not operating
    cumRejectionRate : float
        Cumulative fraction of material rejected (wasted) in the process
    operatingPowerConsumption : float
        Power requirement for the manufacutirng process
    equipMaintCost : float
        Equipment cost expressed as fraction of total investment
        
    """

    annualProdVol      = z[232]      # Scenario: Annual Production Volume
    plantLife          = z[234]      # Scenario: Length of Production Run
    dedicatedEquip     = z[233] == 1 # Scenario: Dedicated Equipment Investment
    harvestChunkInUse  = z[235] == 1 # Scenario: Use Harvest Chunk?
    siemensCVDInUse    = z[236] == 1 # Scenario: Use Siemens CVD?
    etchFilamentsInUse = z[237] == 1 # Scenario: Use Etch Filaments?
    machineFilInUse    = z[238] == 1 # Scenario: Use Machine Filaments?
    sawIngotInUse      = z[239] == 1 # Scenario: Use Saw Ingots?
    cropIngotInUse     = z[240] == 1 # Scenario: Use Crop Ingots?
    annealIngotInUse   = z[241] == 1 # Scenario: Use Anneal Ingots?
    growIngotInUse     = z[242] == 1 # Scenario: Use Grow Ingots?
    TCSInUse           = z[243] == 1 # Scenario: Use TCS?

    days             = z[126] # Indices: Working Days per Year
    hrs              = z[127] # Indices: Working Hours per Day
    equipDiscount    = z[139] # Indices: Equipment Discount
    capexFactor      = z[145] # Indices: CapEx Correction Factor
    capitalRecRate   = z[128] # Indices: Capital Recovery Rate
    equipRecLife     = z[129] # Indices: Equipment Recovery Life
    buildingLife     = z[130] # Indices: Building Recovery Life
    workingCapPeriod = z[131] # Indices: Working Capital Period
    unskilledWage    = z[121] # Indices: Unskilled Direct Wages
    skilledWage      = z[122] # Indices: Skilled Direct Wages
    salary           = z[123] # Indices: Indirect Salary
    indirectLabor    = z[124] # Indices: Indirect:Direct Labor Ratio
    benefitFactor    = z[125] # Indices: Benefits on Wage and Salary
    laborFactor      = z[144] # Indices: Labor Count Multiplier
    natGasPrice      = z[133] # Indices: Price of Natural Gas
    elecPrice        = z[132] # Indices: Price of Electricity
    elecFactor       = z[146] # Indices: Electricity Multiplier
    buildingCostSQF  = z[134] # Indices: Price of Building Space
    CR10KCost        = z[135] # Indices: Price of CR10K Building Space
    CR1KCost         = z[136] # Indices: Price of CR1K Building Space
    CR100Cost        = z[137] # Indices: Price of CR100Building Space

    # calculate total costs to input into annuities and cost summary
    totalEquipInvest = capitalInvestment * (1 + auxEquipInvest) * (1 + installFactor) * np.ceil(runtimeOneStation)
    totalToolingInvest = toolinglInvestment * toolSetPerStation * np.ceil(runtimeOneStation)
    totalBuildingInvest = buildingCostperStation * np.ceil(runtimeOneStation)
    
    # calculate annuity payments
    equipAnnuity = np.pmt(capitalRecRate / 12, equipRecLife * 12, -totalEquipInvest) * (numParallelStations / np.ceil(runtimeOneStation)) * 12
    toolingAnnuity = np.pmt(capitalRecRate / 12, plantLife * 12, -totalToolingInvest) * 12
    buildingAnnuity = np.pmt(capitalRecRate / 12, buildingLife * 12, -totalBuildingInvest) * (numParallelStations / np.ceil(runtimeOneStation)) * 12

    # create dataframe with normalized costs and total costs
    costSummaryWeight = makeFinancials(
                    totalMaterialCosts,
                    (unskilledWage * (1 + benefitFactor) * unskilledDirectLaborers / throughput + skilledWage * (1 + benefitFactor) * skilledDirectLaborers / throughput) / ((1 - avgDowntime) * (1 - cumRejectionRate)),
                    operatingPowerConsumption * elecPrice / ((throughput * (1 - cumRejectionRate) * (1 - avgDowntime))), 
                    0,0,0,0,0,0)
    costSummaryTime = makeFinancials(
                    0,0,0,
                    totalEquipInvest * numParallelStations / (equipRecLife * np.ceil(runtimeOneStation)), 
                    totalToolingInvest / plantLife, 
                    totalBuildingInvest * numParallelStations / (buildingLife * np.ceil(runtimeOneStation)), 
                    equipMaintCost * ((totalEquipInvest + totalToolingInvest) * numParallelStations / np.ceil(runtimeOneStation) + totalBuildingInvest), 
                    (unskilledDirectLaborers + skilledDirectLaborers) * numParallelStations * salary * indirectLabor * (1 + benefitFactor), 
                    0
                    )
    
    costSummaryTime += VARIABLE_COSTS * costSummaryWeight * annualProdVol * 1000

    workingAnnuity = np.pmt(capitalRecRate / 12, workingCapPeriod, -(workingCapPeriod * (np.dot(WORKING_COSTS, costSummaryTime) / 12)) * 12)
    
    costSummaryTime += COST_OF_CAPITAL * (equipAnnuity + toolingAnnuity + buildingAnnuity + workingAnnuity - costSummaryTime.sum())

    costSummaryWeight += FIXED_COSTS * costSummaryTime / (annualProdVol * 1000)
    
    return np.stack([costSummaryWeight, costSummaryTime]) # dataframe object


def harvestChunk(inUse, z): 
    """
    Calculates cost of Harvest Chunk manfucturing step
    
    Parameters
    ----------
    inUse : bool
        Parameter indicating if this manufacturing step should be included in the process
        True = Included, False = Not inlcuded
        
    Returns
    ----------
    costSummary : dataframe object
        Summary of financial cost calculations
    cumRejectionRate : float
        Cumulative rejection rate (waste) for process steps
    """
    
    annualProdVol      = z[232]      # Scenario: Annual Production Volume
    plantLife          = z[234]      # Scenario: Length of Production Run
    dedicatedEquip     = z[233] == 1 # Scenario: Dedicated Equipment Investment
    harvestChunkInUse  = z[235] == 1 # Scenario: Use Harvest Chunk?
    siemensCVDInUse    = z[236] == 1 # Scenario: Use Siemens CVD?
    etchFilamentsInUse = z[237] == 1 # Scenario: Use Etch Filaments?
    machineFilInUse    = z[238] == 1 # Scenario: Use Machine Filaments?
    sawIngotInUse      = z[239] == 1 # Scenario: Use Saw Ingots?
    cropIngotInUse     = z[240] == 1 # Scenario: Use Crop Ingots?
    annealIngotInUse   = z[241] == 1 # Scenario: Use Anneal Ingots?
    growIngotInUse     = z[242] == 1 # Scenario: Use Grow Ingots?
    TCSInUse           = z[243] == 1 # Scenario: Use TCS?

    days             = z[126] # Indices: Working Days per Year
    hrs              = z[127] # Indices: Working Hours per Day
    equipDiscount    = z[139] # Indices: Equipment Discount
    capexFactor      = z[145] # Indices: CapEx Correction Factor
    capitalRecRate   = z[128] # Indices: Capital Recovery Rate
    equipRecLife     = z[129] # Indices: Equipment Recovery Life
    buildingLife     = z[130] # Indices: Building Recovery Life
    workingCapPeriod = z[131] # Indices: Working Capital Period
    unskilledWage    = z[121] # Indices: Unskilled Direct Wages
    skilledWage      = z[122] # Indices: Skilled Direct Wages
    salary           = z[123] # Indices: Indirect Salary
    indirectLabor    = z[124] # Indices: Indirect:Direct Labor Ratio
    benefitFactor    = z[125] # Indices: Benefits on Wage and Salary
    laborFactor      = z[144] # Indices: Labor Count Multiplier
    natGasPrice      = z[133] # Indices: Price of Natural Gas
    elecPrice        = z[132] # Indices: Price of Electricity
    elecFactor       = z[146] # Indices: Electricity Multiplier
    buildingCostSQF  = z[134] # Indices: Price of Building Space
    CR10KCost        = z[135] # Indices: Price of CR10K Building Space
    CR1KCost         = z[136] # Indices: Price of CR1K Building Space
    CR100Cost        = z[137] # Indices: Price of CR100Building Space

    if not inUse:
        costSummary, cumRejectionRate = skipStep()
    else: 
        
        # define input parameters
        argonGas                  = z[102]               # Harvest Chunk: Argon Usage
        argonPrice                = z[103]               # Harvest Chunk: Argon Price
        argonScrapRate            = z[104]               # Harvest Chunk: Argon Scrap Rate
        polySiYieldLossRate       = z[105]               # Harvest Chunk: Poly Si Yield Loss
        polySiScrapReclRate       = z[106]               # Harvest Chunk: Poly Si Scrap Reclemation Rate
        avgDowntime               = z[107]               # Harvest Chunk: Average Downtime
        auxEquipInvest            = z[108]               # Harvest Chunk: Auxiliary Equipment Investment
        installFactor             = z[109]               # Harvest Chunk: Installation Cost Factor
        equipMaintCost            = z[110]               # Harvest Chunk: Equipment Maintenance Cost Factor
        baseCapEx                 = z[120]               # Harvest Chunk: Capital Investment
        unskilledDirectLaborers   = z[111] * laborFactor # Harvest Chunk: Unskilled Direct Laborers Factor
        skilledDirectLaborers     = z[112] * laborFactor # Harvest Chunk: Skilled Direct Laborers Factor
        toolinglInvestment        = z[113]               # Harvest Chunk: Tooling Investment
        toolingLife               = z[114]               # Harvest Chunk: Tooling Life
        operatingPowerConsumption = z[115]               # Harvest Chunk: Operating Power Consumption
        floorSQM                  = z[116]               # Harvest Chunk: Floor SQM
        clean10KSQM               = z[117]               # Harvest Chunk: Clean 10k SQM
        clean1KSQM                = z[118]               # Harvest Chunk: Clean 1k SQM
        clean100SQM               = z[119]               # Harvest Chunk: Clean 100 SQM

        # intermediate calculations
        
        cumRejectionRate = 1 - (1 - polySiYieldLossRate * (1 - polySiScrapReclRate))
        effProductionVol = annualProdVol / (1 - cumRejectionRate)
        
        cycleTime = days * hrs * 60 / (effProductionVol * 1000)
        throughput = 60 / cycleTime
        
        materialCosts = argonGas * argonPrice * 60 / throughput
        totalMaterialCosts = materialCosts / ( (1 - cumRejectionRate) * (1 - argonScrapRate))       # material costs depend on regjection rate which is different for each mfg step
        
        runtimeOneStation = runtime(effProductionVol, throughput, avgDowntime, hrs, days)
        numParallelStations = parallelStationCalc(runtimeOneStation, dedicatedEquip)
        
        capitalInvestment = (1 - equipDiscount) * baseCapEx * annualProdVol * capexFactor / 1.7     # cost per station
        
        prodToolLife = toolLifeCalc(numParallelStations, toolingLife, effProductionVol, plantLife)
        toolSetPerStation = np.ceil(plantLife / prodToolLife)
        
        buildingCostperStation = buildingCosts(floorSQM, clean10KSQM, clean1KSQM, clean100SQM, buildingCostSQF, CR10KCost, CR1KCost, CR100Cost)
        
        
        # cost calculations
        
        costSummary = financialCalculations(capitalInvestment, auxEquipInvest, installFactor, runtimeOneStation, toolinglInvestment, toolSetPerStation, buildingCostperStation, numParallelStations, 
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, operatingPowerConsumption, equipMaintCost, z)
        
    return costSummary, cumRejectionRate


def siemensCVD(inUse, harvestChunkRejRate, z):
    """
    Calculates cost of Harvest Chunk manfucturing step
    
    Parameters
    ----------
    inUse : bool
        Parameter indicating if this manufacturing step should be included in the process
        True = Included, False = Not inlcuded
    harvestChunkRejRate : float
        Fraction of material wasted in Harvest Chunk manufacturing step
        
    Returns
    ----------
    costSummary : dataframe object
        Summary of financial cost calculations
    cumRejectionRate : float
        Cumulative rejection rate (waste) for process steps
    reactorThroughput : float
        Througput of the reactor in the manufacturing step
    totalSiPerRod : float
        Total mass of Si per rod including tail/head
    usableSiPerRod : float
        Usable mass of Si per rod
    effProductionVol : float
        Effective production volume from the manufacturing step
    """
    
    annualProdVol      = z[232]      # Scenario: Annual Production Volume
    plantLife          = z[234]      # Scenario: Length of Production Run
    dedicatedEquip     = z[233] == 1 # Scenario: Dedicated Equipment Investment
    harvestChunkInUse  = z[235] == 1 # Scenario: Use Harvest Chunk?
    siemensCVDInUse    = z[236] == 1 # Scenario: Use Siemens CVD?
    etchFilamentsInUse = z[237] == 1 # Scenario: Use Etch Filaments?
    machineFilInUse    = z[238] == 1 # Scenario: Use Machine Filaments?
    sawIngotInUse      = z[239] == 1 # Scenario: Use Saw Ingots?
    cropIngotInUse     = z[240] == 1 # Scenario: Use Crop Ingots?
    annealIngotInUse   = z[241] == 1 # Scenario: Use Anneal Ingots?
    growIngotInUse     = z[242] == 1 # Scenario: Use Grow Ingots?
    TCSInUse           = z[243] == 1 # Scenario: Use TCS?

    days             = z[126] # Indices: Working Days per Year
    hrs              = z[127] # Indices: Working Hours per Day
    equipDiscount    = z[139] # Indices: Equipment Discount
    capexFactor      = z[145] # Indices: CapEx Correction Factor
    capitalRecRate   = z[128] # Indices: Capital Recovery Rate
    equipRecLife     = z[129] # Indices: Equipment Recovery Life
    buildingLife     = z[130] # Indices: Building Recovery Life
    workingCapPeriod = z[131] # Indices: Working Capital Period
    unskilledWage    = z[121] # Indices: Unskilled Direct Wages
    skilledWage      = z[122] # Indices: Skilled Direct Wages
    salary           = z[123] # Indices: Indirect Salary
    indirectLabor    = z[124] # Indices: Indirect:Direct Labor Ratio
    benefitFactor    = z[125] # Indices: Benefits on Wage and Salary
    laborFactor      = z[144] # Indices: Labor Count Multiplier
    natGasPrice      = z[133] # Indices: Price of Natural Gas
    elecPrice        = z[132] # Indices: Price of Electricity
    elecFactor       = z[146] # Indices: Electricity Multiplier
    buildingCostSQF  = z[134] # Indices: Price of Building Space
    CR10KCost        = z[135] # Indices: Price of CR10K Building Space
    CR1KCost         = z[136] # Indices: Price of CR1K Building Space
    CR100Cost        = z[137] # Indices: Price of CR100Building Space

    if not inUse:
        costSummary, cumRejectionRate = skipStep()
        reactorThroughput, totalSiPerRod, usableSiPerRod, effProductionVol = 0, 0, 0, 0
    else:
        
        # define siemens CVD mfg step input parameters

        h2Gas                     = z[244]               # Siemens CSV: Hydrogen Consumption Rate
        h2Price                   = z[245]               # Siemens CSV: Hydrogen Price
        h2ScrapRate               = z[246]               # Siemens CSV: Hydrogen Scrap Rate
        materialScrapRate         = z[247]               # Siemens CSV: Material Scrap Rate
        polySiRejectRate          = z[248]               # Siemens CSV: Poly Si Reject Rate
        polySiScrapReclRate       = z[249]               # Siemens CSV: Poly Si Scrap Rec Rate
        avgDowntime               = z[250]               # Siemens CSV: Average Downtime
        otherConsumableCost       = z[251]               # Siemens CSV: Other Consumable Cost
        batchSize                 = z[254]               # Siemens CSV: Batch Size
        finalRodSize              = z[255]               # Siemens CSV: Final Rod Size
        inputCycleTime            = z[257]               # Siemens CSV: Cycle Time
        processTime               = z[258]               # Siemens CSV: Setup, Harvest, Clean Time
        baseCapEx                 = z[259]               # Siemens CSV: Capital Investment
        auxEquipInvest            = z[260]               # Siemens CSV: Auxiliary Equipment Investment
        installFactor             = z[261]               # Siemens CSV: Installation Cost Factor
        equipMaintCost            = z[262]               # Siemens CSV: Equipment Maintenance Cost Factor
        unskilledDirectLaborers   = z[252] * laborFactor # Siemens CSV: Unskilled Direct Laborers Factor
        skilledDirectLaborers     = z[253] * laborFactor # Siemens CSV: Skilled Direct Laborers Factor
        toolinglInvestment        = z[263]               # Siemens CSV: Tooling Investment
        toolingLife               = z[264]               # Siemens CSV: Tooling Life
        operatingPowerConsumption = z[265]               # Siemens CSV: Operating Power Consumption
        floorSQM                  = z[266]               # Siemens CSV: Floor SQM
        clean10KSQM               = z[267]               # Siemens CSV: Clean 10k SQM
        clean1KSQM                = z[268]               # Siemens CSV: Clean 1k SQM
        clean100SQM               = z[269]               # Siemens CSV: Clean 100 SQM
        
        
        # intermediate calculations
        
        cumRejectionRate = 1 - (1 - (materialScrapRate + polySiRejectRate) * (1 - polySiScrapReclRate))*(1 - harvestChunkRejRate *(1 - polySiScrapReclRate))
        effProductionVol = annualProdVol / (1 - cumRejectionRate)
        
        ingotLength = z[161] # Ingot Growth: Ingot Length
        totalSiPerRod = (np.pi * (finalRodSize / 20)**2 * ingotLength * 2.33/1000) 
        usableSiPerRod = totalSiPerRod * (1 - materialScrapRate)
        
        cycleTime = (inputCycleTime + processTime) * 60 / (batchSize * usableSiPerRod)
        throughput = 60 / cycleTime
        
        runtimeOneStation = runtime(effProductionVol, throughput, avgDowntime, hrs, days)
        numParallelStations = parallelStationCalc(runtimeOneStation, dedicatedEquip)
        
        reactorThroughput = (effProductionVol * 1000) / (hrs * days * numParallelStations)
        
        prodToolLife = toolLifeCalc(numParallelStations, toolingLife, effProductionVol, plantLife)
        toolSetPerStation = np.ceil(plantLife / prodToolLife)
        
        capitalInvestment = (1 - equipDiscount) * baseCapEx * capexFactor
        
        buildingCostperStation = buildingCosts(floorSQM, clean10KSQM, clean1KSQM, clean100SQM, buildingCostSQF, CR10KCost, CR1KCost, CR100Cost)
        
        materialCosts = h2Gas * h2Price / throughput
        totalMaterialCosts = materialCosts / ((1 - cumRejectionRate) * (1 - h2ScrapRate)) / (1 - (materialScrapRate + polySiRejectRate)) + (otherConsumableCost / (1 - cumRejectionRate))
        
        
        # financial calculations
        
        costSummary = financialCalculations(capitalInvestment, auxEquipInvest, installFactor, runtimeOneStation, toolinglInvestment, toolSetPerStation, buildingCostperStation, numParallelStations, 
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, operatingPowerConsumption, equipMaintCost, z)
        
    return costSummary, reactorThroughput, cumRejectionRate, totalSiPerRod, usableSiPerRod, effProductionVol


def etchFilaments(inUse, siemensCVDRejRate, usableSiPerRod, siemensEffProd, z):
    """
    Calculates cost of Etch Filaments manfucturing step
    
    Parameters
    ----------
    inUse : bool
        Parameter indicating if this manufacturing step should be included in the process
        True = Included, False = Not inlcuded
    siemensCVDRejRate : float
        Cumulative fraction of material wasted in previous manufacturing steps
        
    Returns
    ----------
    costSummary : dataframe object
        Summary of financial cost calculations
    cumRejectionRate : float
        Cumulative rejection rate (waste) for process steps
    HPProduction : float
        Hair pin production volume
    """
    
    annualProdVol      = z[232]      # Scenario: Annual Production Volume
    plantLife          = z[234]      # Scenario: Length of Production Run
    dedicatedEquip     = z[233] == 1 # Scenario: Dedicated Equipment Investment
    harvestChunkInUse  = z[235] == 1 # Scenario: Use Harvest Chunk?
    siemensCVDInUse    = z[236] == 1 # Scenario: Use Siemens CVD?
    etchFilamentsInUse = z[237] == 1 # Scenario: Use Etch Filaments?
    machineFilInUse    = z[238] == 1 # Scenario: Use Machine Filaments?
    sawIngotInUse      = z[239] == 1 # Scenario: Use Saw Ingots?
    cropIngotInUse     = z[240] == 1 # Scenario: Use Crop Ingots?
    annealIngotInUse   = z[241] == 1 # Scenario: Use Anneal Ingots?
    growIngotInUse     = z[242] == 1 # Scenario: Use Grow Ingots?
    TCSInUse           = z[243] == 1 # Scenario: Use TCS?

    days             = z[126] # Indices: Working Days per Year
    hrs              = z[127] # Indices: Working Hours per Day
    equipDiscount    = z[139] # Indices: Equipment Discount
    capexFactor      = z[145] # Indices: CapEx Correction Factor
    capitalRecRate   = z[128] # Indices: Capital Recovery Rate
    equipRecLife     = z[129] # Indices: Equipment Recovery Life
    buildingLife     = z[130] # Indices: Building Recovery Life
    workingCapPeriod = z[131] # Indices: Working Capital Period
    unskilledWage    = z[121] # Indices: Unskilled Direct Wages
    skilledWage      = z[122] # Indices: Skilled Direct Wages
    salary           = z[123] # Indices: Indirect Salary
    indirectLabor    = z[124] # Indices: Indirect:Direct Labor Ratio
    benefitFactor    = z[125] # Indices: Benefits on Wage and Salary
    laborFactor      = z[144] # Indices: Labor Count Multiplier
    natGasPrice      = z[133] # Indices: Price of Natural Gas
    elecPrice        = z[132] # Indices: Price of Electricity
    elecFactor       = z[146] # Indices: Electricity Multiplier
    buildingCostSQF  = z[134] # Indices: Price of Building Space
    CR10KCost        = z[135] # Indices: Price of CR10K Building Space
    CR1KCost         = z[136] # Indices: Price of CR1K Building Space
    CR100Cost        = z[137] # Indices: Price of CR100Building Space
    virginFilament   = z[101] # Etch Filament: Fraction Virgin Filament
    
    if not inUse: 
        costSummary, cumRejectionRate = skipStep()
        HPProduction = 0
    else:
        
        # define etch filaments input parameters

        HFGas                     = z[ 72]               # Etch Filament: HF Consumption Rate
        HFPrice                   = z[ 73]               # Etch Filament: HF Price
        NitricRate                = z[ 74]               # Etch Filament: Nitric Consumption Rate
        NitricPrice               = z[ 75]               # Etch Filament: Nitric Acid Price
        N2Gas                     = z[ 76]               # Etch Filament: Nitrogen Consumption Rate
        N2Price                   = z[ 77]               # Etch Filament: Nitrogen Price
        DIWater                   = z[ 78]               # Etch Filament: DI Water Consumption Rate
        DIWaterPrice              = z[ 79]               # Etch Filament: DI Water Price
        materialScrapRate         = z[ 80]               # Etch Filament: Material Scrap Rate
        partRejectRate            = z[ 81]               # Etch Filament: Part Reject Rate
        avgDowntime               = z[ 82]               # Etch Filament: Average Downtime
        filamentBatchSize         = z[ 85]               # Etch Filament: Filament Batch Size
        filamentSetupTime         = z[ 86]               # Etch Filament: Filament Setup Time
        filamentCycleTime         = z[ 87]               # Etch Filament: Filament Cycle Time
        HPBatchSize               = z[ 88]               # Etch Filament: HP Batch Size
        HPSetupTime               = z[ 89]               # Etch Filament: HP Setup Time
        HPCycleTime               = z[ 90]               # Etch Filament: HP Cycle Time
        baseCapEx                 = z[ 91]               # Etch Filament: Capital Investment
        auxEquipInvest            = z[ 18]               # TCS: Auxiliary Equipment Investment
        installFactor             = z[ 92]               # Etch Filament: Installation Cost Factor
        equipMaintCost            = z[ 93]               # Etch Filament: Equipment Maintenance Cost Factor
        unskilledDirectLaborers   = z[ 83] * laborFactor # Etch Filament: Unskilled Direct Laborers Factor
        skilledDirectLaborers     = z[ 84] * laborFactor # Etch Filament: Skilled Direct Laborers Factor
        toolinglInvestment        = z[ 94]               # Etch Filament: Tooling Investment
        toolingLife               = z[ 95]               # Etch Filament: Tooling Life
        operatingPowerConsumption = z[ 96]               # Etch Filament: Operating Power Consumption
        floorSQM                  = z[ 97]               # Etch Filament: Floor SQM
        clean10KSQM               = z[ 98]               # Etch Filament: Clean 10k SQM
        clean1KSQM                = z[ 99]               # Etch Filament: Clean 1k SQM
        clean100SQM               = z[100]               # Etch Filament: Clean 100 SQM
        
        
        # intermediate calculations
        HPProduction = 0    # scrubbed?
        
        cumRejectionRate = 1 - ( (1 - partRejectRate) * (1 - siemensCVDRejRate) )
        effProductionVol = annualProdVol / (1 - cumRejectionRate)
        
        materialCostPerHour = np.dot([HFGas, NitricRate, N2Gas, DIWater], [HFPrice, NitricPrice, N2Price, DIWaterPrice])
        materialCosts = materialCostPerHour * days * hrs / (annualProdVol * 1000)
        totalMaterialCosts = materialCosts / ((1 - cumRejectionRate) * (1 - materialScrapRate))
        
        filamentProcessTime = (filamentCycleTime + filamentSetupTime) / filamentBatchSize / usableSiPerRod
        chunkProcessTime = (HPCycleTime + HPSetupTime) / HPBatchSize
        cycleTime = (filamentProcessTime * virginFilament) + (chunkProcessTime * (1 - virginFilament))
        throughput = 60 / cycleTime
        
        runtimeOneStation = runtime(effProductionVol, throughput, avgDowntime, hrs, days)
        numParallelStations = parallelStationCalc(runtimeOneStation, dedicatedEquip)
        
        capitalInvestment = (1 - equipDiscount) * baseCapEx * capexFactor * siemensEffProd
        
        prodToolLife = toolLifeCalc(numParallelStations, toolingLife, effProductionVol, plantLife)
        toolSetPerStation = np.ceil(plantLife / prodToolLife)
                
        buildingCostperStation = buildingCosts(floorSQM, clean10KSQM, clean1KSQM, clean100SQM, buildingCostSQF, CR10KCost, CR1KCost, CR100Cost)


        # financial calculations
        
        costSummary = financialCalculations(capitalInvestment, auxEquipInvest, installFactor, runtimeOneStation, toolinglInvestment, toolSetPerStation, buildingCostperStation, numParallelStations, 
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, operatingPowerConsumption, equipMaintCost, z)
        
        
    return costSummary, cumRejectionRate, HPProduction


def machineFilaments(inUse, etchRejectionRate, totalSiPerRod, z):
    """
    Calculates cost of Machining Filaments manfucturing step
    
    Parameters
    ----------
    inUse : bool
        Parameter indicating if this manufacturing step should be included in the process
        True = Included, False = Not inlcuded
    etchRejectionRate : float
        Cumulative fraction of material wasted in previous manufacturing steps
    totalSiPerRod : float
        Total Si mass for each rod (including head/tail)
        
    Returns
    ----------
    costSummary : dataframe object
        Summary of financial cost calculations
    cumRejectionRate : float
        Cumulative rejection rate (waste) for process steps
    """
    
    annualProdVol      = z[232]      # Scenario: Annual Production Volume
    plantLife          = z[234]      # Scenario: Length of Production Run
    dedicatedEquip     = z[233] == 1 # Scenario: Dedicated Equipment Investment
    harvestChunkInUse  = z[235] == 1 # Scenario: Use Harvest Chunk?
    siemensCVDInUse    = z[236] == 1 # Scenario: Use Siemens CVD?
    etchFilamentsInUse = z[237] == 1 # Scenario: Use Etch Filaments?
    machineFilInUse    = z[238] == 1 # Scenario: Use Machine Filaments?
    sawIngotInUse      = z[239] == 1 # Scenario: Use Saw Ingots?
    cropIngotInUse     = z[240] == 1 # Scenario: Use Crop Ingots?
    annealIngotInUse   = z[241] == 1 # Scenario: Use Anneal Ingots?
    growIngotInUse     = z[242] == 1 # Scenario: Use Grow Ingots?
    TCSInUse           = z[243] == 1 # Scenario: Use TCS?

    days             = z[126] # Indices: Working Days per Year
    hrs              = z[127] # Indices: Working Hours per Day
    equipDiscount    = z[139] # Indices: Equipment Discount
    capexFactor      = z[145] # Indices: CapEx Correction Factor
    capitalRecRate   = z[128] # Indices: Capital Recovery Rate
    equipRecLife     = z[129] # Indices: Equipment Recovery Life
    buildingLife     = z[130] # Indices: Building Recovery Life
    workingCapPeriod = z[131] # Indices: Working Capital Period
    unskilledWage    = z[121] # Indices: Unskilled Direct Wages
    skilledWage      = z[122] # Indices: Skilled Direct Wages
    salary           = z[123] # Indices: Indirect Salary
    indirectLabor    = z[124] # Indices: Indirect:Direct Labor Ratio
    benefitFactor    = z[125] # Indices: Benefits on Wage and Salary
    laborFactor      = z[144] # Indices: Labor Count Multiplier
    natGasPrice      = z[133] # Indices: Price of Natural Gas
    elecPrice        = z[132] # Indices: Price of Electricity
    elecFactor       = z[146] # Indices: Electricity Multiplier
    buildingCostSQF  = z[134] # Indices: Price of Building Space
    CR10KCost        = z[135] # Indices: Price of CR10K Building Space
    CR1KCost         = z[136] # Indices: Price of CR1K Building Space
    CR100Cost        = z[137] # Indices: Price of CR100Building Space

    if not inUse: 
        costSummary, cumRejectionRate = skipStep()
    else:
        
        # define etch filaments input parameters

        consumableRate            = z[183]               # Machine Filament: Consumable Rate
        consumablePrice           = z[184]               # Machine Filament: Consumable Price
        materialScrapRate         = z[185]               # Machine Filament: Material Scrap Rate
        yieldLoss                 = z[186]               # Machine Filament: Yield Loss
        scrapRecRate              = z[187]               # Machine Filament: Scrap Reclamation Rate
        avgDowntime               = z[188]               # Machine Filament: Average Downtime
        filamentBatchSize         = z[191]               # Machine Filament: Filament Batch Size
        filamentSetupTime         = z[192]               # Machine Filament: Filament Setup Time
        filamentCycleTime         = z[193]               # Machine Filament: Filament Cycle Time
        baseCapEx                 = z[194]               # Machine Filament: Capital Investment
        auxEquipInvest            = z[195]               # Machine Filament: Auxiliary Equipment Investment
        installFactor             = z[196]               # Machine Filament: Installation Cost Factor
        equipMaintCost            = z[197]               # Machine Filament: Equipment Maintenance Cost Factor
        unskilledDirectLaborers   = z[189] * laborFactor # Machine Filament: Unskilled Direct Laborers Factor
        skilledDirectLaborers     = z[190] * laborFactor # Machine Filament: Skilled Direct Laborers Factor
        toolinglInvestment        = z[198]               # Machine Filament: Tooling Investment
        toolingLife               = z[199]               # Machine Filament: Tooling Life
        operatingPowerConsumption = z[200]               # Machine Filament: Operating Power Consumption
        floorSQM                  = z[201]               # Machine Filament: Floor SQM
        clean10KSQM               = z[202]               # Machine Filament: Clean 10k SQM
        clean1KSQM                = z[203]               # Machine Filament: Clean 1k SQM
        clean100SQM               = z[204]               # Machine Filament: Clean 100 SQM
        
        ingotLength   = z[161] # Ingot Growth: Ingot Length
        ingotWeight   = z[162] # Ingot Growth: Ingot Weight (tops and tails)
        ingotDiameter = z[163] # Ingot Growth: As Grown Ingot Diameter
        finalDiameter = z[164] # Ingot Growth: Final Ingot Diameter
        filamentWidth = z[218] # Saw Ingots: Filament Width
        kerfLoss      = z[210] # Saw Ingots: Kerf Loss
        ingotGrossWeight = grossIngotWeight(ingotLength, ingotWeight, ingotDiameter)
        growthBatchSize = sizeFilamentBatch(finalDiameter, filamentWidth, kerfLoss)

        # intermediate calculations
        
        cumRejectionRate = 1 - (1 - ((1 - scrapRecRate) * yieldLoss)) * (1 - etchRejectionRate)
        effProductionVol = annualProdVol / (1 - cumRejectionRate)
        
        cycleTime = (filamentCycleTime + filamentSetupTime) / filamentBatchSize / totalSiPerRod
        throughput = 60 / cycleTime
        
        materialCosts = consumableRate * consumablePrice * 60 / throughput
        totalMaterialCosts = materialCosts / ((1 - cumRejectionRate) * (1 - materialScrapRate))
        
        runtimeOneStation = runtime(effProductionVol, throughput, avgDowntime, hrs, days)
        numParallelStations = parallelStationCalc(runtimeOneStation, dedicatedEquip)
        
        capitalInvestment = baseCapEx * capexFactor
        
        ingotWeight =  ingotGrossWeight / (1.15 * growthBatchSize)
        adjEffProdVol = effProductionVol * (ingotWeight / totalSiPerRod)
        
        prodToolLife = toolLifeCalc(numParallelStations, toolingLife, adjEffProdVol, plantLife)
        toolSetPerStation = np.ceil(plantLife / prodToolLife)
                
        buildingCostperStation = buildingCosts(floorSQM, clean10KSQM, clean1KSQM, clean100SQM, buildingCostSQF, CR10KCost, CR1KCost, CR100Cost)


        # financial calculations
        
        costSummary = financialCalculations(capitalInvestment, auxEquipInvest, installFactor, runtimeOneStation, toolinglInvestment, toolSetPerStation, buildingCostperStation, numParallelStations, 
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, operatingPowerConsumption, equipMaintCost, z)
        
        
    return costSummary, cumRejectionRate


def sawIngots(inUse, machineRejectRate, usableSiPerRod, totalSiPerRod, z):
    """
    Calculates cost of Sawing Ingot manfucturing step
    
    Parameters
    ----------
    inUse : bool
        Parameter indicating if this manufacturing step should be included in the process
        True = Included, False = Not inlcuded
    etchRejectionRate : float
        Cumulative fraction of material wasted in previous manufacturing steps
    usableSiPerRod : float
        Usable mass of Si for each rod
    totalSiPerRod : float
        Total Si mass for each rod (including head/tail)
        
    Returns
    ----------
    costSummary : dataframe object
        Summary of financial cost calculations
    cumRejectionRate : float
        Cumulative rejection rate (waste) for process steps
    """
    
    annualProdVol      = z[232]      # Scenario: Annual Production Volume
    plantLife          = z[234]      # Scenario: Length of Production Run
    dedicatedEquip     = z[233] == 1 # Scenario: Dedicated Equipment Investment
    harvestChunkInUse  = z[235] == 1 # Scenario: Use Harvest Chunk?
    siemensCVDInUse    = z[236] == 1 # Scenario: Use Siemens CVD?
    etchFilamentsInUse = z[237] == 1 # Scenario: Use Etch Filaments?
    machineFilInUse    = z[238] == 1 # Scenario: Use Machine Filaments?
    sawIngotInUse      = z[239] == 1 # Scenario: Use Saw Ingots?
    cropIngotInUse     = z[240] == 1 # Scenario: Use Crop Ingots?
    annealIngotInUse   = z[241] == 1 # Scenario: Use Anneal Ingots?
    growIngotInUse     = z[242] == 1 # Scenario: Use Grow Ingots?
    TCSInUse           = z[243] == 1 # Scenario: Use TCS?

    days             = z[126] # Indices: Working Days per Year
    hrs              = z[127] # Indices: Working Hours per Day
    equipDiscount    = z[139] # Indices: Equipment Discount
    capexFactor      = z[145] # Indices: CapEx Correction Factor
    capitalRecRate   = z[128] # Indices: Capital Recovery Rate
    equipRecLife     = z[129] # Indices: Equipment Recovery Life
    buildingLife     = z[130] # Indices: Building Recovery Life
    workingCapPeriod = z[131] # Indices: Working Capital Period
    unskilledWage    = z[121] # Indices: Unskilled Direct Wages
    skilledWage      = z[122] # Indices: Skilled Direct Wages
    salary           = z[123] # Indices: Indirect Salary
    indirectLabor    = z[124] # Indices: Indirect:Direct Labor Ratio
    benefitFactor    = z[125] # Indices: Benefits on Wage and Salary
    laborFactor      = z[144] # Indices: Labor Count Multiplier
    natGasPrice      = z[133] # Indices: Price of Natural Gas
    elecPrice        = z[132] # Indices: Price of Electricity
    elecFactor       = z[146] # Indices: Electricity Multiplier
    buildingCostSQF  = z[134] # Indices: Price of Building Space
    CR10KCost        = z[135] # Indices: Price of CR10K Building Space
    CR1KCost         = z[136] # Indices: Price of CR1K Building Space
    CR100Cost        = z[137] # Indices: Price of CR100Building Space

    if not inUse: 
        costSummary, cumRejectionRate = skipStep()
    else:
        
        # define etch filaments input parameters

        wireLife                  = z[205]               # Saw Ingots: Wire Life
        wireCost                  = z[206]               # Saw Ingots: Wire Cost
        SiCSlurryConsumption      = z[207]               # Saw Ingots: SiC Slurry Consumption
        SiCSlurryPrice            = z[208]               # Saw Ingots: SiC Slurry Price
        SiCSlurryScrap            = z[209]               # Saw Ingots: SiC Slurry Scrap Rate
        kerfLoss                  = z[210]               # Saw Ingots: Kerf Loss
        sellKerf                  = z[211]               # Saw Ingots: Sell Kerf Loss Si?
        kerfPrice                 = z[212]               # Saw Ingots: Kerf Loss Si Price
        partRejectRate            = z[213]               # Saw Ingots: Part Reject Rate
        avgDowntime               = z[214]               # Saw Ingots: Average Downtime
        batchSize                 = z[217]               # Saw Ingots: Batch Size
        setupTime                 = z[219]               # Saw Ingots: Setup Time
        cutSpeed                  = z[220]               # Saw Ingots: Cutting Speed
        baseCapEx                 = z[221]               # Saw Ingots: Capital Investment
        auxEquipInvest            = z[222]               # Saw Ingots: Auxiliary Equipment Investment
        installFactor             = z[223]               # Saw Ingots: Installation Cost Factor
        equipMaintCost            = z[224]               # Saw Ingots: Equipment Maintenance Cost Factor
        unskilledDirectLaborers   = z[215] * laborFactor # Saw Ingots: Unskilled Direct Laborers Factor
        skilledDirectLaborers     = z[216] * laborFactor # Saw Ingots: Skilled Direct Laborers Factor
        toolinglInvestment        = z[225]               # Saw Ingots: Tooling Investment
        toolingLife               = z[226]               # Saw Ingots: Tooling Life
        operatingPowerConsumption = z[227]               # Saw Ingots: Operating Power Consumption
        floorSQM                  = z[228]               # Saw Ingots: Floor SQM
        clean10KSQM               = z[229]               # Saw Ingots: Clean 10k SQM
        clean1KSQM                = z[230]               # Saw Ingots: Clean 1k SQM
        clean100SQM               = z[231]               # Saw Ingots: Clean 100 SQM

        ingotLength   = z[161] # Ingot Growth: Ingot Length
        ingotWeight   = z[162] # Ingot Growth: Ingot Weight (tops and tails)
        ingotDiameter = z[163] # Ingot Growth: As Grown Ingot Diameter
        finalDiameter = z[164] # Ingot Growth: Final Ingot Diameter
        filamentWidth = z[218] # Saw Ingots: Filament Width
        kerfLoss      = z[210] # Saw Ingots: Kerf Loss
        ingotGrossWeight = grossIngotWeight(ingotLength, ingotWeight, ingotDiameter)
        growthBatchSize = sizeFilamentBatch(finalDiameter, filamentWidth, kerfLoss)
        
        # intermediate calculations
        
        cumRejectionRate = 1 - ( (1 - partRejectRate) * (1 - machineRejectRate) )
        effProductionVol = annualProdVol / (1 - cumRejectionRate)
        
        cycleTime = ingotLength * 10 / cutSpeed
        processRate = 60 / (cycleTime + setupTime)
        processTime = (cycleTime + setupTime) / (batchSize * growthBatchSize)
        throughput = 60 / (processTime / usableSiPerRod)
        
        sawWireCosts = (wireCost / wireLife) * processRate / throughput
        kerfCosts = -1 * sellKerf * (kerfLoss / 10000)**2 * ingotLength * kerfPrice / (0.9 * totalSiPerRod)
        slurryCost = SiCSlurryConsumption *  SiCSlurryPrice / ( (1 - SiCSlurryScrap) * throughput )
        totalMaterialCosts = np.sum([sawWireCosts, kerfCosts, slurryCost]) / (1 - cumRejectionRate)
        
        runtimeOneStation = runtime(effProductionVol, throughput, avgDowntime, hrs, days)
        numParallelStations = parallelStationCalc(runtimeOneStation, dedicatedEquip)
        
        capitalInvestment = baseCapEx * capexFactor
        
        prodToolLife = toolLifeCalc(numParallelStations, toolingLife, effProductionVol, plantLife)
        toolSetPerStation = np.ceil(plantLife / prodToolLife)
                
        buildingCostperStation = buildingCosts(floorSQM, clean10KSQM, clean1KSQM, clean100SQM, buildingCostSQF, CR10KCost, CR1KCost, CR100Cost)


        # financial calculations
        
        costSummary = financialCalculations(capitalInvestment, auxEquipInvest, installFactor, runtimeOneStation, toolinglInvestment, toolSetPerStation, buildingCostperStation, numParallelStations, 
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, operatingPowerConsumption, equipMaintCost, z)
        
        
    return costSummary, cumRejectionRate


def cropIngots(inUse, sawRejectRate, totalSiPerRod, z):
    """
    Calculates cost of Crop Ingot manfucturing step
    
    Parameters
    ----------
    inUse : bool
        Parameter indicating if this manufacturing step should be included in the process
        True = Included, False = Not inlcuded
    sawRejectionRate : float
        Cumulative fraction of material wasted in previous manufacturing steps
    totalSiPerRod : float
        Total Si mass for each rod (including head/tail)
        
    Returns
    ----------
    costSummary : dataframe object
        Summary of financial cost calculations
    cumRejectionRate : float
        Cumulative rejection rate (waste) for process steps
    """
    
    annualProdVol      = z[232]      # Scenario: Annual Production Volume
    plantLife          = z[234]      # Scenario: Length of Production Run
    dedicatedEquip     = z[233] == 1 # Scenario: Dedicated Equipment Investment
    harvestChunkInUse  = z[235] == 1 # Scenario: Use Harvest Chunk?
    siemensCVDInUse    = z[236] == 1 # Scenario: Use Siemens CVD?
    etchFilamentsInUse = z[237] == 1 # Scenario: Use Etch Filaments?
    machineFilInUse    = z[238] == 1 # Scenario: Use Machine Filaments?
    sawIngotInUse      = z[239] == 1 # Scenario: Use Saw Ingots?
    cropIngotInUse     = z[240] == 1 # Scenario: Use Crop Ingots?
    annealIngotInUse   = z[241] == 1 # Scenario: Use Anneal Ingots?
    growIngotInUse     = z[242] == 1 # Scenario: Use Grow Ingots?
    TCSInUse           = z[243] == 1 # Scenario: Use TCS?

    days             = z[126] # Indices: Working Days per Year
    hrs              = z[127] # Indices: Working Hours per Day
    equipDiscount    = z[139] # Indices: Equipment Discount
    capexFactor      = z[145] # Indices: CapEx Correction Factor
    capitalRecRate   = z[128] # Indices: Capital Recovery Rate
    equipRecLife     = z[129] # Indices: Equipment Recovery Life
    buildingLife     = z[130] # Indices: Building Recovery Life
    workingCapPeriod = z[131] # Indices: Working Capital Period
    unskilledWage    = z[121] # Indices: Unskilled Direct Wages
    skilledWage      = z[122] # Indices: Skilled Direct Wages
    salary           = z[123] # Indices: Indirect Salary
    indirectLabor    = z[124] # Indices: Indirect:Direct Labor Ratio
    benefitFactor    = z[125] # Indices: Benefits on Wage and Salary
    laborFactor      = z[144] # Indices: Labor Count Multiplier
    natGasPrice      = z[133] # Indices: Price of Natural Gas
    elecPrice        = z[132] # Indices: Price of Electricity
    elecFactor       = z[146] # Indices: Electricity Multiplier
    buildingCostSQF  = z[134] # Indices: Price of Building Space
    CR10KCost        = z[135] # Indices: Price of CR10K Building Space
    CR1KCost         = z[136] # Indices: Price of CR1K Building Space
    CR100Cost        = z[137] # Indices: Price of CR100Building Space

    if not inUse: 
        costSummary, cumRejectionRate = skipStep()
    else:
        
        # define etch filaments input parameters

        weightRemoved             = z[ 48]               # Crop Ingots: Weight of Sections Removed
        SiCSlurryConsumption      = z[ 51]               # Crop Ingots: SiC Slurry Consumption
        SiCSlurryPrice            = z[ 52]               # Crop Ingots: SiC Slurry Price
        bladeLife                 = z[ 49]               # Crop Ingots: Blade Life
        bladeCost                 = z[ 50]               # Crop Ingots: Blade Cost
        brickRejectRate           = z[ 53]               # Crop Ingots: Brick Reject Rate
        scrapRecRate              = z[ 54]               # Crop Ingots: Scrap Reclamation Rate
        avgDowntime               = z[ 55]               # Crop Ingots: Average Downtime
        batchSize                 = z[ 58]               # Crop Ingots: Batch Size
        setupTime                 = z[ 59]               # Crop Ingots: Setup Time
        sawRate                   = z[ 60]               # Crop Ingots: Saw Rate
        baseCapEx                 = z[ 61]               # Crop Ingots: Capital Investment
        auxEquipInvest            = z[ 62]               # Crop Ingots: Auxiliary Equipment Investment
        installFactor             = z[ 63]               # Crop Ingots: Installation Cost Factor
        equipMaintCost            = z[ 64]               # Crop Ingots: Equipment Maintenance Cost Factor
        unskilledDirectLaborers   = z[ 56] * laborFactor # Crop Ingots: Unskilled Direct Laborers Factor
        skilledDirectLaborers     = z[ 57] * laborFactor # Crop Ingots: Skilled Direct Laborers Factor
        toolinglInvestment        = z[ 65]               # Crop Ingots: Tooling Investment
        toolingLife               = z[ 66]               # Crop Ingots: Tooling Life
        operatingPowerConsumption = z[ 67]               # Crop Ingots: Operating Power Consumption
        floorSQM                  = z[ 68]               # Crop Ingots: Floor SQM
        clean10KSQM               = z[ 69]               # Crop Ingots: Clean 10k SQM
        clean1KSQM                = z[ 70]               # Crop Ingots: Clean 1k SQM
        clean100SQM               = z[ 71]               # Crop Ingots: Clean 100 SQM
        
        ingotLength   = z[161] # Ingot Growth: Ingot Length
        ingotWeight   = z[162] # Ingot Growth: Ingot Weight (tops and tails)
        ingotDiameter = z[163] # Ingot Growth: As Grown Ingot Diameter
        finalDiameter = z[164] # Ingot Growth: Final Ingot Diameter
        filamentWidth = z[218] # Saw Ingots: Filament Width
        kerfLoss      = z[210] # Saw Ingots: Kerf Loss
        ingotGrossWeight = grossIngotWeight(ingotLength, ingotWeight, ingotDiameter)
        growthBatchSize = sizeFilamentBatch(finalDiameter, filamentWidth, kerfLoss)

        # intermediate calculations
        
        yieldLoss = (weightRemoved / ingotGrossWeight) + brickRejectRate * (1 - scrapRecRate)
        
        cumRejectionRate = 1 - ( (1 - yieldLoss) * (1 - sawRejectRate) )
        effProductionVol = annualProdVol / (1 - cumRejectionRate)
        
        cycleTime = (ingotDiameter / sawRate + setupTime) / batchSize
        throughput = cycleTime * growthBatchSize * totalSiPerRod / 60
        
        wireCosts = bladeCost / (bladeLife * batchSize * ingotGrossWeight)
        slurryCosts = SiCSlurryConsumption * SiCSlurryPrice * (60 / cycleTime) / ingotGrossWeight
        totalMaterialCosts = (wireCosts + slurryCosts) / (1 - cumRejectionRate)
        
        runtimeOneStation = runtime(effProductionVol, throughput, avgDowntime, hrs, days)
        numParallelStations = parallelStationCalc(runtimeOneStation, dedicatedEquip)
        
        capitalInvestment = baseCapEx * capexFactor
        
        prodToolLife = toolLifeCalc(numParallelStations, toolingLife, effProductionVol, plantLife)
        toolSetPerStation = np.ceil(plantLife / prodToolLife)
                
        buildingCostperStation = buildingCosts(floorSQM, clean10KSQM, clean1KSQM, clean100SQM, buildingCostSQF, CR10KCost, CR1KCost, CR100Cost)


        # financial calculations
        
        costSummary = financialCalculations(capitalInvestment, auxEquipInvest, installFactor, runtimeOneStation, toolinglInvestment, toolSetPerStation, buildingCostperStation, numParallelStations, 
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, operatingPowerConsumption, equipMaintCost, z)
        
        
    return costSummary, cumRejectionRate


def annealIngots(inUse, cropRejectRate, totalSiPerRod, z):
    """
    Calculates cost of Anneal Ingot manfucturing step
    
    Parameters
    ----------
    inUse : bool
        Parameter indicating if this manufacturing step should be included in the process
        True = Included, False = Not inlcuded
    cropRejectRate : float
        Cumulative fraction of material wasted in previous manufacturing steps
    totalSiPerRod : float
        Total Si mass for each rod (including head/tail)
        
    Returns
    ----------
    costSummary : dataframe object
        Summary of financial cost calculations
    cumRejectionRate : float
        Cumulative rejection rate (waste) for process steps
    """
    
    annualProdVol      = z[232]      # Scenario: Annual Production Volume
    plantLife          = z[234]      # Scenario: Length of Production Run
    dedicatedEquip     = z[233] == 1 # Scenario: Dedicated Equipment Investment
    harvestChunkInUse  = z[235] == 1 # Scenario: Use Harvest Chunk?
    siemensCVDInUse    = z[236] == 1 # Scenario: Use Siemens CVD?
    etchFilamentsInUse = z[237] == 1 # Scenario: Use Etch Filaments?
    machineFilInUse    = z[238] == 1 # Scenario: Use Machine Filaments?
    sawIngotInUse      = z[239] == 1 # Scenario: Use Saw Ingots?
    cropIngotInUse     = z[240] == 1 # Scenario: Use Crop Ingots?
    annealIngotInUse   = z[241] == 1 # Scenario: Use Anneal Ingots?
    growIngotInUse     = z[242] == 1 # Scenario: Use Grow Ingots?
    TCSInUse           = z[243] == 1 # Scenario: Use TCS?

    days             = z[126] # Indices: Working Days per Year
    hrs              = z[127] # Indices: Working Hours per Day
    equipDiscount    = z[139] # Indices: Equipment Discount
    capexFactor      = z[145] # Indices: CapEx Correction Factor
    capitalRecRate   = z[128] # Indices: Capital Recovery Rate
    equipRecLife     = z[129] # Indices: Equipment Recovery Life
    buildingLife     = z[130] # Indices: Building Recovery Life
    workingCapPeriod = z[131] # Indices: Working Capital Period
    unskilledWage    = z[121] # Indices: Unskilled Direct Wages
    skilledWage      = z[122] # Indices: Skilled Direct Wages
    salary           = z[123] # Indices: Indirect Salary
    indirectLabor    = z[124] # Indices: Indirect:Direct Labor Ratio
    benefitFactor    = z[125] # Indices: Benefits on Wage and Salary
    laborFactor      = z[144] # Indices: Labor Count Multiplier
    natGasPrice      = z[133] # Indices: Price of Natural Gas
    elecPrice        = z[132] # Indices: Price of Electricity
    elecFactor       = z[146] # Indices: Electricity Multiplier
    buildingCostSQF  = z[134] # Indices: Price of Building Space
    CR10KCost        = z[135] # Indices: Price of CR10K Building Space
    CR1KCost         = z[136] # Indices: Price of CR1K Building Space
    CR100Cost        = z[137] # Indices: Price of CR100Building Space

    if not inUse: 
        costSummary, cumRejectionRate = skipStep()
    else:
        
        # define input parameters

        argonGas                  = z[ 28]               # Anneal Ingots: Argon Gas
        argonPrice                = z[ 29]               # Anneal Ingots: Argon Price
        argonScrapRate            = z[ 30]               # Anneal Ingots: Argon Scrap Rate
        polySiYieldLossRate       = z[ 31]               # Anneal Ingots: Poly Si Chunk Yield Loss Rate
        polySiScrapReclRate       = z[ 32]               # Anneal Ingots: Poly Si Scrap Reclamation Rate
        avgDowntime               = z[ 33]               # Anneal Ingots: Average Downtime
        furnaceCap                = z[ 34]               # Anneal Ingots: Furnace Capacity
        baseCapEx                 = z[ 37]               # Anneal Ingots: Capital Investment
        auxEquipInvest            = z[ 38]               # Anneal Ingots: Auxiliary Equipment Investment
        installFactor             = z[ 39]               # Anneal Ingots: Installation Cost Factor
        equipMaintCost            = z[ 40]               # Anneal Ingots: Equipment Maintenance Cost Factor
        unskilledDirectLaborers   = z[ 35] * laborFactor # Anneal Ingots: Unskilled Direct Laborers Factor
        skilledDirectLaborers     = z[ 36] * laborFactor # Anneal Ingots: Skilled Direct Laborers Factor
        toolinglInvestment        = z[ 41]               # Anneal Ingots: Tooling Investment
        toolingLife               = z[ 42]               # Anneal Ingots: Tooling Life
        operatingPowerConsumption = z[ 43]               # Anneal Ingots: Operating Power Consumption
        floorSQM                  = z[ 44]               # Anneal Ingots: Floor SQM
        clean10KSQM               = z[ 45]               # Anneal Ingots: Clean 10k SQM
        clean1KSQM                = z[ 46]               # Anneal Ingots: Clean 1k SQM
        clean100SQM               = z[ 47]               # Anneal Ingots: Clean 100 SQM
                
        ingotLength   = z[161] # Ingot Growth: Ingot Length
        ingotWeight   = z[162] # Ingot Growth: Ingot Weight (tops and tails)
        ingotDiameter = z[163] # Ingot Growth: As Grown Ingot Diameter
        finalDiameter = z[164] # Ingot Growth: Final Ingot Diameter
        filamentWidth = z[218] # Saw Ingots: Filament Width
        kerfLoss      = z[210] # Saw Ingots: Kerf Loss
        ingotGrossWeight = grossIngotWeight(ingotLength, ingotWeight, ingotDiameter)
        growthBatchSize = sizeFilamentBatch(finalDiameter, filamentWidth, kerfLoss)

        # intermediate calculations
        
        cumRejectionRate = 1 - (1 - (1 - polySiScrapReclRate) * polySiYieldLossRate) * (1 - cropRejectRate)
        effProductionVol = annualProdVol / (1 - cumRejectionRate)
        
        filamentWeight = ingotGrossWeight / (1.15 * growthBatchSize)
        throughput = furnaceCap / (filamentWeight / totalSiPerRod)
                
        totalMaterialCosts = (argonGas * argonPrice * 60 / throughput) / ((1 - cumRejectionRate) * (1 - argonScrapRate))
        
        adjEffProdVol = effProductionVol * (filamentWeight / totalSiPerRod)
        runtimeOneStation = runtime(adjEffProdVol, throughput, avgDowntime, hrs, days)
        numParallelStations = parallelStationCalc(runtimeOneStation, dedicatedEquip)
        
        capitalInvestment = baseCapEx * capexFactor
        
        prodToolLife = toolLifeCalc(numParallelStations, toolingLife, effProductionVol, plantLife)
        toolSetPerStation = np.ceil(plantLife / prodToolLife)
                
        buildingCostperStation = buildingCosts(floorSQM, clean10KSQM, clean1KSQM, clean100SQM, buildingCostSQF, CR10KCost, CR1KCost, CR100Cost)


        # financial calculations
        
        costSummary = financialCalculations(capitalInvestment, auxEquipInvest, installFactor, runtimeOneStation, toolinglInvestment, toolSetPerStation, buildingCostperStation, numParallelStations, 
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, operatingPowerConsumption, equipMaintCost, z)
        
        
    return costSummary, cumRejectionRate


def ingnotGrowth(inUse, annealRejectRate, usableSiPerRod, z):
    """
    Calculates cost of Ingot Growth manfucturing step
    
    Parameters
    ----------
    inUse : bool
        Parameter indicating if this manufacturing step should be included in the process
        True = Included, False = Not inlcuded
    annealRejectionRate : float
        Cumulative fraction of material wasted in previous manufacturing steps
    usableSiPerRod : float
        Usable mass of Si for each rod
        
    Returns
    ----------
    costSummary : dataframe object
        Summary of financial cost calculations
    cumRejectionRate : float
        Cumulative rejection rate (waste) for process steps
    """
    
    annualProdVol      = z[232]      # Scenario: Annual Production Volume
    plantLife          = z[234]      # Scenario: Length of Production Run
    dedicatedEquip     = z[233] == 1 # Scenario: Dedicated Equipment Investment
    harvestChunkInUse  = z[235] == 1 # Scenario: Use Harvest Chunk?
    siemensCVDInUse    = z[236] == 1 # Scenario: Use Siemens CVD?
    etchFilamentsInUse = z[237] == 1 # Scenario: Use Etch Filaments?
    machineFilInUse    = z[238] == 1 # Scenario: Use Machine Filaments?
    sawIngotInUse      = z[239] == 1 # Scenario: Use Saw Ingots?
    cropIngotInUse     = z[240] == 1 # Scenario: Use Crop Ingots?
    annealIngotInUse   = z[241] == 1 # Scenario: Use Anneal Ingots?
    growIngotInUse     = z[242] == 1 # Scenario: Use Grow Ingots?
    TCSInUse           = z[243] == 1 # Scenario: Use TCS?

    days             = z[126] # Indices: Working Days per Year
    hrs              = z[127] # Indices: Working Hours per Day
    equipDiscount    = z[139] # Indices: Equipment Discount
    capexFactor      = z[145] # Indices: CapEx Correction Factor
    capitalRecRate   = z[128] # Indices: Capital Recovery Rate
    equipRecLife     = z[129] # Indices: Equipment Recovery Life
    buildingLife     = z[130] # Indices: Building Recovery Life
    workingCapPeriod = z[131] # Indices: Working Capital Period
    unskilledWage    = z[121] # Indices: Unskilled Direct Wages
    skilledWage      = z[122] # Indices: Skilled Direct Wages
    salary           = z[123] # Indices: Indirect Salary
    indirectLabor    = z[124] # Indices: Indirect:Direct Labor Ratio
    benefitFactor    = z[125] # Indices: Benefits on Wage and Salary
    laborFactor      = z[144] # Indices: Labor Count Multiplier
    natGasPrice      = z[133] # Indices: Price of Natural Gas
    elecPrice        = z[132] # Indices: Price of Electricity
    elecFactor       = z[146] # Indices: Electricity Multiplier
    buildingCostSQF  = z[134] # Indices: Price of Building Space
    CR10KCost        = z[135] # Indices: Price of CR10K Building Space
    CR1KCost         = z[136] # Indices: Price of CR1K Building Space
    CR100Cost        = z[137] # Indices: Price of CR100Building Space

    if not inUse: 
        costSummary, cumRejectionRate = skipStep()
    else:
        
        # define input parameters
        
        polySiPrice               = z[147]               # Ingot Growth: Poly-Si Material Price
        polySiScrapRate           = z[148]               # Ingot Growth: Poly Si Material Scrap Rate
        SiSeedPrice               = z[149]               # Ingot Growth: Si Seed Price
        SiSeedLife                = z[150]               # Ingot Growth: Si Seed Life
        crucibleCost              = z[151]               # Ingot Growth: Crucible Cost
        crucibleLife              = z[152]               # Ingot Growth: Crucible Life
        waterConsumption          = z[153]               # Ingot Growth: Cooling Water Cons Rate
        waterPrice                = z[154]               # Ingot Growth: Water Price
        argonGas                  = z[155]               # Ingot Growth: Argon Consumption Rate
        argonPrice                = z[156]               # Ingot Growth: Argon Price
        partRejectRate            = z[157]               # Ingot Growth: Part Reject Rate
        avgDowntime               = z[158]               # Ingot Growth: Average Downtime
        ingotLength               = z[161]               # Ingot Growth: Ingot Length
        setupTime                 = z[165]               # Ingot Growth: Setup (Load) Time
        pumpTime                  = z[166]               # Ingot Growth: Pump Down and Leak Check
        meltTime                  = z[167]               # Ingot Growth: Melt/Stabilize
        meltTime                  = z[167]               # Ingot Growth: Melt/Stabilize
        pullSpeed                 = z[168]               # Ingot Growth: Average Pull Speed
        coolTime                  = z[169]               # Ingot Growth: Cool and Unload
        cleanTime                 = z[170]               # Ingot Growth: Clean
        baseCapEx                 = z[171]               # Ingot Growth: Capital Investment
        auxEquipInvest            = z[172]               # Ingot Growth: Auxiliary Equipment Investment
        installFactor             = z[173]               # Ingot Growth: Installation Cost Factor
        equipMaintCost            = z[174]               # Ingot Growth: Equipment Maintenance Cost Factor
        unskilledDirectLaborers   = z[159] * laborFactor # Ingot Growth: Unskilled Direct Laborers Factor
        skilledDirectLaborers     = z[160] * laborFactor # Ingot Growth: Skilled Direct Laborers Factor
        toolinglInvestment        = z[175]               # Ingot Growth: Tooling Investment
        toolingLife               = z[176]               # Ingot Growth: Tooling Life
        operatingPowerConsumption = z[177]               # Ingot Growth: Operating Power Consumption
        fullPowerConsumption      = z[178]               # Ingot Growth: Full Power Consumption
        floorSQM                  = z[179]               # Ingot Growth: Floor SQM
        clean10KSQM               = z[180]               # Ingot Growth: Clean 10k SQM
        clean1KSQM                = z[181]               # Ingot Growth: Clean 1k SQM
        clean100SQM               = z[182]               # Ingot Growth: Clean 100 SQM
                
        ingotLength   = z[161] # Ingot Growth: Ingot Length
        ingotWeight   = z[162] # Ingot Growth: Ingot Weight (tops and tails)
        ingotDiameter = z[163] # Ingot Growth: As Grown Ingot Diameter
        finalDiameter = z[164] # Ingot Growth: Final Ingot Diameter
        filamentWidth = z[218] # Saw Ingots: Filament Width
        kerfLoss      = z[210] # Saw Ingots: Kerf Loss
        ingotGrossWeight = grossIngotWeight(ingotLength, ingotWeight, ingotDiameter)
        growthBatchSize = sizeFilamentBatch(finalDiameter, filamentWidth, kerfLoss)

        # intermediate calculations
        
        cumRejectionRate = 1 - (1 - partRejectRate) * (1 - annealRejectRate)
        effProductionVol = annualProdVol / (1 - cumRejectionRate)
        
        filamentWeight = ingotGrossWeight / (1.15 * growthBatchSize)
        
        pullTime = ingotLength * 10 / pullSpeed
        totalCycleTime = np.sum([pullTime, setupTime, pumpTime, meltTime, coolTime, cleanTime])
        productionSpeed = totalCycleTime / growthBatchSize
        
        throughput = usableSiPerRod / productionSpeed
        
        polySiCost = polySiPrice * ingotGrossWeight / (growthBatchSize * (1 - polySiScrapRate))
        SiSeedCost = SiSeedPrice / SiSeedLife / growthBatchSize
        crucibleCost = crucibleCost / crucibleLife / growthBatchSize
        waterCost = waterConsumption * waterPrice / growthBatchSize
        argonCost = argonGas * argonPrice / (productionSpeed * 60)
        totalMaterialCosts = np.sum([polySiCost, SiSeedCost, crucibleCost, waterCost, argonCost]) / (1 - cumRejectionRate) / usableSiPerRod
        
        runtimeOneStation = runtime(effProductionVol, throughput, avgDowntime, hrs, days)
        numParallelStations = parallelStationCalc(runtimeOneStation, dedicatedEquip)
        
        capitalInvestment = baseCapEx * capexFactor * (1 - equipDiscount)
        
        adjEffProdVol = effProductionVol * filamentWeight / usableSiPerRod
        prodToolLife = toolLifeCalc(numParallelStations, toolingLife, adjEffProdVol, plantLife)
        toolSetPerStation = np.ceil(plantLife / prodToolLife)
                
        buildingCostperStation = buildingCosts(floorSQM, clean10KSQM, clean1KSQM, clean100SQM, buildingCostSQF, CR10KCost, CR1KCost, CR100Cost)
        
        totalPower = setupTime * operatingPowerConsumption + fullPowerConsumption * (productionSpeed - (setupTime / growthBatchSize))
        adjPowerConsumption = totalPower * throughput / usableSiPerRod

        # financial calculations
        
        costSummary = financialCalculations(capitalInvestment, auxEquipInvest, installFactor, runtimeOneStation, toolinglInvestment, toolSetPerStation, buildingCostperStation, numParallelStations, 
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, adjPowerConsumption, equipMaintCost, z)
        
        
    return costSummary, cumRejectionRate


def TCS(inUse, siemensCVDRejRate, HPProduction, siemensEffProd, z):
    """
    Calculates cost of TCS manfucturing step
    
    Parameters
    ----------
    inUse : bool
        Parameter indicating if this manufacturing step should be included in the process
        True = Included, False = Not inlcuded
    siemensRejectionRate : float
        Cumulative fraction of material wasted in previous manufacturing steps
    HPProduction : float
        Hair pin production amount
    siemensEffProd : float
        Effective production volumne from Siemens CVD step
        
    Returns
    ----------
    costSummary : dataframe object
        Summary of financial cost calculations
    """
    
    annualProdVol      = z[232]      # Scenario: Annual Production Volume
    plantLife          = z[234]      # Scenario: Length of Production Run
    dedicatedEquip     = z[233] == 1 # Scenario: Dedicated Equipment Investment
    harvestChunkInUse  = z[235] == 1 # Scenario: Use Harvest Chunk?
    siemensCVDInUse    = z[236] == 1 # Scenario: Use Siemens CVD?
    etchFilamentsInUse = z[237] == 1 # Scenario: Use Etch Filaments?
    machineFilInUse    = z[238] == 1 # Scenario: Use Machine Filaments?
    sawIngotInUse      = z[239] == 1 # Scenario: Use Saw Ingots?
    cropIngotInUse     = z[240] == 1 # Scenario: Use Crop Ingots?
    annealIngotInUse   = z[241] == 1 # Scenario: Use Anneal Ingots?
    growIngotInUse     = z[242] == 1 # Scenario: Use Grow Ingots?
    TCSInUse           = z[243] == 1 # Scenario: Use TCS?

    days             = z[126] # Indices: Working Days per Year
    hrs              = z[127] # Indices: Working Hours per Day
    equipDiscount    = z[139] # Indices: Equipment Discount
    capexFactor      = z[145] # Indices: CapEx Correction Factor
    capitalRecRate   = z[128] # Indices: Capital Recovery Rate
    equipRecLife     = z[129] # Indices: Equipment Recovery Life
    buildingLife     = z[130] # Indices: Building Recovery Life
    workingCapPeriod = z[131] # Indices: Working Capital Period
    unskilledWage    = z[121] # Indices: Unskilled Direct Wages
    skilledWage      = z[122] # Indices: Skilled Direct Wages
    salary           = z[123] # Indices: Indirect Salary
    indirectLabor    = z[124] # Indices: Indirect:Direct Labor Ratio
    benefitFactor    = z[125] # Indices: Benefits on Wage and Salary
    laborFactor      = z[144] # Indices: Labor Count Multiplier
    natGasPrice      = z[133] # Indices: Price of Natural Gas
    elecPrice        = z[132] # Indices: Price of Electricity
    elecFactor       = z[146] # Indices: Electricity Multiplier
    buildingCostSQF  = z[134] # Indices: Price of Building Space
    CR10KCost        = z[135] # Indices: Price of CR10K Building Space
    CR1KCost         = z[136] # Indices: Price of CR1K Building Space
    CR100Cost        = z[137] # Indices: Price of CR100Building Space
    
    if not inUse: 
        costSummary, cumRejectionRate = skipStep()
    else:
        
        # define input parameters
        
        MGSiUsage               = z[  6]               # TCS: MG Si Usage Factor
        MGSiPrice               = z[  7]               # TCS: MG Si Price
        MGSiScrapRate           = z[  8]               # TCS: MG Si Scrap Rate
        HClUsage                = z[  9]               # TCS: HCl Usage Factor
        HClPrice                = z[ 10]               # TCS: HCl Price
        HClScrapRate            = z[ 11]               # TCS: HCl Scrap Rate
        H2Usage                 = z[ 12]               # TCS: Hydrogen Usage Factor
        H2Price                 = z[ 13]               # TCS: Hydrogen Price
        otherScrapRate          = z[ 14]               # TCS: Other Material Scrap Rate
        avgDowntime             = z[ 15]               # TCS: Average Downtime
        auxEquipInvest          = z[ 18]               # TCS: Auxiliary Equipment Investment
        installFactor           = z[ 19]               # TCS: Installation Cost Factor
        equipMaintCost          = z[ 20]               # TCS: Equipment Maintenance Cost Factor
        unskilledDirectLaborers = z[ 16] * laborFactor # TCS: Unskilled Direct Laborers Factor
        skilledDirectLaborers   = z[ 17] * laborFactor # TCS: Skilled Direct Laborers Factor
        toolinglInvestment      = z[ 21]               # TCS: Tooling Investment
        toolingLife             = z[ 22]               # TCS: Tooling Life
        clean10KSQM             = z[ 25]               # TCS: Clean 10k SQM
        clean1KSQM              = z[ 26]               # TCS: Clean 1k SQM
        clean100SQM             = z[ 27]               # TCS: Clean 100 SQM
        
        # intermediate calculations
        
        cumRejectionRate = siemensCVDRejRate
        effProductionVol = annualProdVol / (1 - cumRejectionRate)
        
        grossProd = siemensEffProd * 1000
        MGSiCost = ((effProductionVol - HPProduction) / effProductionVol) * grossProd * MGSiPrice * MGSiUsage / (1 - MGSiScrapRate)
        HClCost = grossProd * HClUsage * HClPrice / (1 - HClScrapRate)
        H2Cost = H2Usage * H2Price * grossProd / (1 - otherScrapRate)
        wasteCost = z[  1] * effProductionVol # TCS Process: Waste $/kg TCS
        totalMaterialCosts = np.sum([MGSiCost, HClCost, H2Cost, wasteCost]) / (1 - cumRejectionRate) / (annualProdVol * 1000)
        
        throughput = (annualProdVol * 1000) / (days * hrs)
        
        adjEffProdVol = effProductionVol * (1 - cumRejectionRate)
        runtimeOneStation = runtime(adjEffProdVol, throughput, avgDowntime, hrs, days)
        numParallelStations = parallelStationCalc(runtimeOneStation, dedicatedEquip)
        
        capitalInvestment = z[  4] * capexFactor * (1 - equipDiscount) # TCS Process: Equipment Cost ($/station)
        
        prodToolLife = toolLifeCalc(numParallelStations, toolingLife, effProductionVol, plantLife)
        toolSetPerStation = np.ceil(plantLife / prodToolLife)
        
        operatingPowerConsumption = z[  3] * elecFactor # TCS Process: Power (kW)
        heatNatGas                = z[  2] * throughput # TCS Process: Heat Natural Gas (m3/kg Poly Si)
        adjUtilities = (operatingPowerConsumption * elecPrice + heatNatGas * natGasPrice) / elecPrice       # adding in Nat Gas and adjusting for use in financial calculation function
        
        unskilledDirectLaborers = unskilledDirectLaborers * annualProdVol / 3000
        skilledDirectLaborers = skilledDirectLaborers * annualProdVol / 3000
        
        floorSQM = z[  5] # TCS Process: Floorspace (m2/station)
        buildingCostperStation = buildingCosts(floorSQM, clean10KSQM, clean1KSQM, clean100SQM, buildingCostSQF, CR10KCost, CR1KCost, CR100Cost)
        
        
        # financial calculations
        
        costSummary = financialCalculations(capitalInvestment, auxEquipInvest, installFactor, runtimeOneStation, toolinglInvestment, toolSetPerStation, buildingCostperStation, numParallelStations, 
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, adjUtilities, equipMaintCost, z)
        
        
    return costSummary


import pandas as pd


zp = pd.read_csv("../../ioc-2/data/parameters.tsv", header = 0, index_col = "Offset", sep="\t")


harvestFinancials, harvestRejectRate = harvestChunk(True, zp.Value)

siemensCVDFinancials, CVDthroughput, siemensCVDRejRate, totalSiPerRod, usableSiPerRod, siemensEffProd = siemensCVD(True, harvestRejectRate, zp.Value)

etchFilamentsFinancial, etchRejectionRate, HPProduction = etchFilaments(True, siemensCVDRejRate, usableSiPerRod, siemensEffProd, zp.Value)

machineFinancials, machineRejectRate = machineFilaments(True, etchRejectionRate, totalSiPerRod, zp.Value)

sawFinancials, sawRejectRate = sawIngots(True, machineRejectRate, usableSiPerRod, totalSiPerRod, zp.Value)

cropFinancials, cropRejectRate = cropIngots(True, sawRejectRate, totalSiPerRod, zp.Value)

annealFinacials, annealRejectRate = annealIngots(True, cropRejectRate, totalSiPerRod, zp.Value)

growthFinancials, growthRejRate = ingnotGrowth(True, annealRejectRate, usableSiPerRod, zp.Value)

TCSFinancials = TCS(True, siemensCVDRejRate, HPProduction, siemensEffProd, zp.Value)



steps = np.stack([harvestFinancials, siemensCVDFinancials, etchFilamentsFinancial, machineFinancials, sawFinancials, cropFinancials, annealFinacials, growthFinancials, TCSFinancials])
pd.DataFrame(
    financialSummary(steps),
    index = np.append(financialsHeader, "Total")
)



print(
  pd.DataFrame(
    financialSummary(steps),
    columns = ["$/kg"],
    index = np.append(financialsHeader, "Total")
  )
)
