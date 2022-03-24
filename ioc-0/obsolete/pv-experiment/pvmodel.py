"""
Engineering-based cost model for PV manufacturing.
Based on Polysilicon Chunk Manufacturing Cost Excel Model

Manufacturing Steps: 
1. Harvest Chunk
2. Siemens CVD
3. Etch Filaments
4. Machine Filaments
5. Ingots (Saw, Crop, Anneal, Growth)
6. TCS

Cost summary adds cost from each step in manufacturing process

VERSION STATUS: Validated  all manufacturing steps and financial summary with Excel Model

FUTURE WORK: 
    - use named_tuples when reading in input variables to make it easier to create new models in the future
    - isolate administrative functions/code from calculations; could read in CSVs and return objects
    - convert True/False input file parameters to true boolean values (likely need to define function to do this)

"""


import concurrent.futures as ft
import numpy              as np
import pandas             as pd

from collections     import namedtuple
from copy            import deepcopy
from functools       import reduce
from itertools       import repeat
from multiprocessing import cpu_count


"""
----- Read Input Data ----- 
"""

CurrentInputs = namedtuple("CurrentInputs",
    [
        "harvestChunkInputs"     ,
        "siemensCVDInputs"       ,
        "etchFilamentsInputs"    ,
        "machineFilamentsInputs" ,
        "sawIngotsInputs"        ,
        "cropIngotsInputs"       ,
        "annealIngotsInputs"     ,
        "ingotGrowthInputs"      ,
        "TCSInputs"              ,
    ])

def readDefaultInputs():
    return CurrentInputs(
        harvestChunkInputs     = pd.read_csv('harvestChunk.csv',    index_col=0, header=0).to_dict(),
        siemensCVDInputs       = pd.read_csv('siemensCVD.csv',      index_col=0, header=0).to_dict(),
        etchFilamentsInputs    = pd.read_csv('etchFilament.csv',    index_col=0, header=0).to_dict(),
        machineFilamentsInputs = pd.read_csv('machineFilament.csv', index_col=0, header=0).to_dict(),
        sawIngotsInputs        = pd.read_csv('sawIngots.csv',       index_col=0, header=0).to_dict(),
        cropIngotsInputs       = pd.read_csv('cropIngots.csv',      index_col=0, header=0).to_dict(),
        annealIngotsInputs     = pd.read_csv('annealIngots.csv',    index_col=0, header=0).to_dict(),
        ingotGrowthInputs      = pd.read_csv('ingotGrowth.csv',     index_col=0, header=0).to_dict(),
        TCSInputs              = pd.read_csv('TCS.csv',             index_col=0, header=0).to_dict(),
    )


""" 
----- Read Scenario Input Data ----- 
"""


ScenarioInputs = namedtuple("ScenarioInputs",
    [
        "region"              ,
        "annualProdVol"       ,
        "plantLife"           ,
        "dedicatedEquip"      ,
        "harvestChunkInUse"   ,
        "siemensCVDInUse"     ,
        "etchFilamentsInUse"  ,
        "machineFilInUse"     ,
        "sawIngotInUse"       ,
        "cropIngotInUse"      ,
        "annealIngotInUse"    ,
        "growIngotInUse"      ,
        "TCSInUse"            ,
        "TCSProcess"          ,
        "TCSProcessInputs"    ,
    ])


def readScenarioInputs():
    scenario = pd.read_csv('scenario.csv', index_col=0, header=0).to_dict()
    return ScenarioInputs(
        region              =       scenario['Value']['Region']                         ,
        annualProdVol       = float(scenario['Value']['Annual Production Volume']      ),
        plantLife           = float(scenario['Value']['Length of Production Run']      ),
        dedicatedEquip      =       scenario['Value']['Dedicated Equipment Investment'] ,
        harvestChunkInUse   =       scenario['Value']['Use Harvest Chunk?']             ,
        siemensCVDInUse     =       scenario['Value']['Use Siemens CVD?']               ,
        etchFilamentsInUse  =       scenario['Value']['Use Etch Filaments?']            ,
        machineFilInUse     =       scenario['Value']['Use Machine Filaments?']         ,
        sawIngotInUse       =       scenario['Value']['Use Saw Ingots?']                ,
        cropIngotInUse      =       scenario['Value']['Use Crop Ingots?']               ,
        annealIngotInUse    =       scenario['Value']['Use Anneal Ingots?']             ,
        growIngotInUse      =       scenario['Value']['Use Grow Ingots?']               ,
        TCSInUse            =       scenario['Value']['Use TCS?']                       ,
        TCSProcess          =       scenario['Value']['TCS Process']                    ,
        TCSProcessInputs    = pd.read_csv('TCS-process.csv', index_col=0, header=0)
    )


"""
----- Define Regional Constants -----
"""

RegionalInputs = namedtuple("RegionalInputs",
    [
        "days"            ,
        "hrs"             ,
        "equipDiscount"   ,
        "capexFactor"     ,
        "capitalRecRate"  ,
        "equipRecLife"    ,
        "buildingLife"    ,
        "workingCapPeriod",
        "skilledWage"     ,
        "unskilledWage"   ,
        "salary"          ,
        "indirectLabor"   ,
        "benefitFactor"   ,
        "laborFactor"     ,
        "natGasPrice"     ,
        "elecPrice"       ,
        "elecFactor"      ,
        "buildingCostSQF" ,
        "CR10KCost"       ,
        "CR1KCost"        ,
        "CR100Cost"       ,
    ])


def readRegionalInputs(region):
    inputs = pd.read_csv('indices.csv', index_col=0, header=0).to_dict()
    return RegionalInputs(
        days                = inputs[region]['Working Days per Year']        ,
        hrs                 = inputs[region]['Working Hours per Day']        ,
        equipDiscount       = inputs[region]['Equipment Discount']           ,
        capexFactor         = inputs[region]['CapEx Correction Factor']      ,
        capitalRecRate      = inputs[region]['Capital Recovery Rate']        ,
        equipRecLife        = inputs[region]['Equipment Recovery Life']      ,
        buildingLife        = inputs[region]['Building Recovery Life']       ,
        workingCapPeriod    = inputs[region]['Working Capital Period']       ,
        skilledWage         = inputs[region]['Skilled Direct Wages']         ,
        unskilledWage       = inputs[region]['Unskilled Direct Wages']       ,
        salary              = inputs[region]['Indirect Salary']              ,
        indirectLabor       = inputs[region]['Indirect:Direct Labor Ratio']  ,
        benefitFactor       = inputs[region]['Benefits on Wage and Salary']  ,
        laborFactor         = inputs[region]['Labor Count Multiplier']       ,
        natGasPrice         = inputs[region]['Price of Natural Gas']         ,
        elecPrice           = inputs[region]['Price of Electricity']         ,
        elecFactor          = inputs[region]['Electricity Multiplier']       ,
        buildingCostSQF     = inputs[region]['Price of Building Space']      ,
        CR10KCost           = inputs[region]['Price of CR10K Building Space'],
        CR1KCost            = inputs[region]['Price of CR1K Building Space'] ,
        CR100Cost           = inputs[region]['Price of CR100Building Space'] ,
    )



def readInputs():
    defaultInputs = readDefaultInputs()
    scenarioInputs = readScenarioInputs()
    regionalInputs = readRegionalInputs(scenarioInputs.region)
    return defaultInputs, scenarioInputs, regionalInputs


# In[2]:


""" 
------ Define Functions for Manufacturing Step Costs -----
"""


def buildingCosts(floorSQF, clean10KSQF, clean1KSQF, clean100SQF, buildingCostSQF, CR10KCost, CR1KCost, CR100Cost):    
    return buildingCostSQF * floorSQF + CR10KCost * clean10KSQF + CR1KCost * clean1KSQF + CR100Cost * clean100SQF


def runtime(productionVol, throughput, downtime, hrs, days): 
    return (productionVol * 1000) / (throughput * hrs * days * (1 - downtime))


def parallelStationCalc(runtimeOneStation, dedicatedEquip):
    return  np.ceil(runtimeOneStation) if dedicatedEquip == 'True' else runtimeOneStation.copy()


def toolLifeCalc(numParallelStations, toolingLife, effProductionVol, plantLife): 
    toolLives = [plantLife, (numParallelStations * toolingLife / (effProductionVol * 1000))]
    return np.min(toolLives)


def grossIngotWeight(length, weightFraction, diameter):
    return np.pi * ((diameter / 20)**2 * length * 2.33 / 1000 * (1 + weightFraction))


def sizeFilamentBatch(diameter, filamentWidth, kerfLoss):
    size = np.trunc( (np.pi * (diameter / 20)**2) / ( (filamentWidth / 10) + (kerfLoss / 10000) )**2 )
    size = np.trunc(0.9 * size)
    return size


def dfSelect(df,idx,col):
    return df.loc[df.index == idx, col].iloc[0]


def skipStep(): 
    empty = pd.DataFrame({
            '$/kg Poly Si Chunk': [0,0,0,0,0,0,0,0,0], 
            '$/year' : [0,0,0,0,0,0,0,0,0]}, 
            index=['Material Cost','Direct Labor Cost','Utility Cost','Equipment Cost','Tooling Cost','Building Cost','Maintenance Cost','Overhead Labor Cost','Cost of Capital'])
    rejRate = 0
    return empty, rejRate


def financialSummary(dfs): 
    summary = pd.DataFrame()
    for df in dfs: 
        summary = summary.add(df, fill_value=0)
    summary['%'] = summary['$/year'] / summary['$/year'].sum()
    summary.loc['Total'] = summary.sum()
    return summary
    


def financialCalculations(capitalInvestment, auxEquipInvest, installFactor, runtimeOneStation, toolinglInvestment, toolSetPerStation, buildingCostperStation, numParallelStations, 
                          totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, operatingPowerConsumption, equipMaintCost, scenarioInputs, regionalInputs):
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
    
    region             = scenarioInputs.region
    annualProdVol      = scenarioInputs.annualProdVol
    plantLife          = scenarioInputs.plantLife
    dedicatedEquip     = scenarioInputs.dedicatedEquip
    harvestChunkInUse  = scenarioInputs.harvestChunkInUse
    siemensCVDInUse    = scenarioInputs.siemensCVDInUse
    etchFilamentsInUse = scenarioInputs.etchFilamentsInUse
    machineFilInUse    = scenarioInputs.machineFilInUse
    sawIngotInUse      = scenarioInputs.sawIngotInUse
    cropIngotInUse     = scenarioInputs.cropIngotInUse
    annealIngotInUse   = scenarioInputs.annealIngotInUse
    growIngotInUse     = scenarioInputs.growIngotInUse
    TCSInUse           = scenarioInputs.TCSInUse
    TCSProcess         = scenarioInputs.TCSProcess
    TCSProcessInputs   = scenarioInputs.TCSProcessInputs

    days             = regionalInputs.days
    hrs              = regionalInputs.hrs
    equipDiscount    = regionalInputs.equipDiscount
    capexFactor      = regionalInputs.capexFactor
    capitalRecRate   = regionalInputs.capitalRecRate
    equipRecLife     = regionalInputs.equipRecLife
    buildingLife     = regionalInputs.buildingLife
    workingCapPeriod = regionalInputs.workingCapPeriod
    skilledWage      = regionalInputs.skilledWage
    unskilledWage    = regionalInputs.unskilledWage
    salary           = regionalInputs.salary
    indirectLabor    = regionalInputs.indirectLabor
    benefitFactor    = regionalInputs.benefitFactor
    laborFactor      = regionalInputs.laborFactor
    natGasPrice      = regionalInputs.natGasPrice
    elecPrice        = regionalInputs.elecPrice
    elecFactor       = regionalInputs.elecFactor
    buildingCostSQF  = regionalInputs.buildingCostSQF
    CR10KCost        = regionalInputs.CR10KCost
    CR1KCost         = regionalInputs.CR1KCost
    CR100Cost        = regionalInputs.CR100Cost

    # calculate total costs to input into annuities and cost summary
    totalEquipInvest = capitalInvestment * (1 + auxEquipInvest) * (1 + installFactor) * np.ceil(runtimeOneStation)
    totalToolingInvest = toolinglInvestment * toolSetPerStation * np.ceil(runtimeOneStation)
    totalBuildingInvest = buildingCostperStation * np.ceil(runtimeOneStation)
    
    # calculate annuity payments
    equipAnnuity = np.pmt(capitalRecRate / 12, equipRecLife * 12, -totalEquipInvest) * (numParallelStations / np.ceil(runtimeOneStation)) * 12
    toolingAnnuity = np.pmt(capitalRecRate / 12, plantLife * 12, -totalToolingInvest) * 12
    buildingAnnuity = np.pmt(capitalRecRate / 12, buildingLife * 12, -totalBuildingInvest) * (numParallelStations / np.ceil(runtimeOneStation)) * 12
    
    # create dataframe with normalized costs and total costs
    costSummary = pd.DataFrame({
            '$/kg Poly Si Chunk': [
                    totalMaterialCosts,
                    (unskilledWage * (1 + benefitFactor) * unskilledDirectLaborers / throughput + skilledWage * (1 + benefitFactor) * skilledDirectLaborers / throughput) / ((1 - avgDowntime) * (1 - cumRejectionRate)),
                    operatingPowerConsumption * elecPrice / ((throughput * (1 - cumRejectionRate) * (1 - avgDowntime))), 
                    0,0,0,0,0,0], 
            '$/year' : [
                    0,0,0,
                    totalEquipInvest * numParallelStations / (equipRecLife * np.ceil(runtimeOneStation)), 
                    totalToolingInvest / plantLife, 
                    totalBuildingInvest * numParallelStations / (buildingLife * np.ceil(runtimeOneStation)), 
                    equipMaintCost * ((totalEquipInvest + totalToolingInvest) * numParallelStations / np.ceil(runtimeOneStation) + totalBuildingInvest), 
                    (unskilledDirectLaborers + skilledDirectLaborers) * numParallelStations * salary * indirectLabor * (1 + benefitFactor), 
                    0
                    ]}, 
            index=['Material Cost','Direct Labor Cost','Utility Cost','Equipment Cost','Tooling Cost','Building Cost','Maintenance Cost','Overhead Labor Cost','Cost of Capital'])
    
    variableCostRows = ['Material Cost','Direct Labor Cost','Utility Cost']        
    costSummary.loc[costSummary.index.isin(variableCostRows), '$/year'] = costSummary['$/kg Poly Si Chunk'] * annualProdVol * 1000
    
    workingRows = ['Material Cost','Direct Labor Cost','Utility Cost','Maintenance Cost','Overhead Labor Cost']
    workingAnnuity = np.pmt(capitalRecRate / 12, workingCapPeriod, -(workingCapPeriod * (costSummary.loc[costSummary.index.isin(workingRows), '$/year'].sum()) / 12)) * 12
    
    costSummary.loc[costSummary.index == 'Cost of Capital', '$/year'] = (equipAnnuity + toolingAnnuity + buildingAnnuity + workingAnnuity) - costSummary['$/year'].sum()
    
    fixedCostRows = ['Equipment Cost','Tooling Cost','Building Cost','Maintenance Cost','Overhead Labor Cost','Cost of Capital']
    costSummary.loc[costSummary.index.isin(fixedCostRows), '$/kg Poly Si Chunk'] = costSummary['$/year'] / (annualProdVol * 1000)
    
    return costSummary # dataframe object


def harvestChunk(inUse, currentInputs, scenarioInputs, regionalInputs): 
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
    
    region             = scenarioInputs.region
    annualProdVol      = scenarioInputs.annualProdVol
    plantLife          = scenarioInputs.plantLife
    dedicatedEquip     = scenarioInputs.dedicatedEquip
    harvestChunkInUse  = scenarioInputs.harvestChunkInUse
    siemensCVDInUse    = scenarioInputs.siemensCVDInUse
    etchFilamentsInUse = scenarioInputs.etchFilamentsInUse
    machineFilInUse    = scenarioInputs.machineFilInUse
    sawIngotInUse      = scenarioInputs.sawIngotInUse
    cropIngotInUse     = scenarioInputs.cropIngotInUse
    annealIngotInUse   = scenarioInputs.annealIngotInUse
    growIngotInUse     = scenarioInputs.growIngotInUse
    TCSInUse           = scenarioInputs.TCSInUse
    TCSProcess         = scenarioInputs.TCSProcess
    TCSProcessInputs   = scenarioInputs.TCSProcessInputs

    days             = regionalInputs.days
    hrs              = regionalInputs.hrs
    equipDiscount    = regionalInputs.equipDiscount
    capexFactor      = regionalInputs.capexFactor
    capitalRecRate   = regionalInputs.capitalRecRate
    equipRecLife     = regionalInputs.equipRecLife
    buildingLife     = regionalInputs.buildingLife
    workingCapPeriod = regionalInputs.workingCapPeriod
    skilledWage      = regionalInputs.skilledWage
    unskilledWage    = regionalInputs.unskilledWage
    salary           = regionalInputs.salary
    indirectLabor    = regionalInputs.indirectLabor
    benefitFactor    = regionalInputs.benefitFactor
    laborFactor      = regionalInputs.laborFactor
    natGasPrice      = regionalInputs.natGasPrice
    elecPrice        = regionalInputs.elecPrice
    elecFactor       = regionalInputs.elecFactor
    buildingCostSQF  = regionalInputs.buildingCostSQF
    CR10KCost        = regionalInputs.CR10KCost
    CR1KCost         = regionalInputs.CR1KCost
    CR100Cost        = regionalInputs.CR100Cost

    if inUse == 'False':
        costSummary, cumRejectionRate = skipStep()
    else: 
        
        # define input parameters
        
        argonGas                    = currentInputs.harvestChunkInputs['Value']['Argon Usage']                                        # SLM
        argonPrice                  = currentInputs.harvestChunkInputs['Value']['Argon Price']                                        # $/std liter
        argonScrapRate              = currentInputs.harvestChunkInputs['Value']['Argon Scrap Rate']                                   # %
        
        polySiYieldLossRate         = currentInputs.harvestChunkInputs['Value']['Poly Si Yield Loss']                                 # %
        polySiScrapReclRate         = currentInputs.harvestChunkInputs['Value']['Poly Si Scrap Reclemation Rate']                     # %
        avgDowntime                 = currentInputs.harvestChunkInputs['Value']['Average Downtime']                                   # %
        
        auxEquipInvest              = currentInputs.harvestChunkInputs['Value']['Auxiliary Equipment Investment']                     # % 
        installFactor               = currentInputs.harvestChunkInputs['Value']['Installation Cost Factor']
        equipMaintCost              = currentInputs.harvestChunkInputs['Value']['Equipment Maintenance Cost Factor']                  # %
        baseCapEx                   = currentInputs.harvestChunkInputs['Value']['Capital Investment']                                 # $/station
        
        unskilledDirectLaborers     = currentInputs.harvestChunkInputs['Value']['Unskilled Direct Laborers Factor'] * laborFactor     # ppl/station
        skilledDirectLaborers       = currentInputs.harvestChunkInputs['Value']['Skilled Direct Laborers Factor'] * laborFactor       # ppl/station
        
        toolinglInvestment          = currentInputs.harvestChunkInputs['Value']['Tooling Investment']                                 # per toolset
        toolingLife                 = currentInputs.harvestChunkInputs['Value']['Tooling Life']                                       # kgs/tool
        
        operatingPowerConsumption   = currentInputs.harvestChunkInputs['Value']['Operating Power Consumption']                        # kW
        floorSQM                    = currentInputs.harvestChunkInputs['Value']['Floor SQM']                                          # sq m
        clean10KSQM                 = currentInputs.harvestChunkInputs['Value']['Clean 10k SQM']                                      # sq m
        clean1KSQM                  = currentInputs.harvestChunkInputs['Value']['Clean 1k SQM']                                       # sq m
        clean100SQM                 = currentInputs.harvestChunkInputs['Value']['Clean 100 SQM']                                      # sq m
        

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
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, operatingPowerConsumption, equipMaintCost, scenarioInputs, regionalInputs)
        
    return costSummary, cumRejectionRate


def siemensCVD(inUse, harvestChunkRejRate, currentInputs, scenarioInputs, regionalInputs):
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
    
    region             = scenarioInputs.region
    annualProdVol      = scenarioInputs.annualProdVol
    plantLife          = scenarioInputs.plantLife
    dedicatedEquip     = scenarioInputs.dedicatedEquip
    harvestChunkInUse  = scenarioInputs.harvestChunkInUse
    siemensCVDInUse    = scenarioInputs.siemensCVDInUse
    etchFilamentsInUse = scenarioInputs.etchFilamentsInUse
    machineFilInUse    = scenarioInputs.machineFilInUse
    sawIngotInUse      = scenarioInputs.sawIngotInUse
    cropIngotInUse     = scenarioInputs.cropIngotInUse
    annealIngotInUse   = scenarioInputs.annealIngotInUse
    growIngotInUse     = scenarioInputs.growIngotInUse
    TCSInUse           = scenarioInputs.TCSInUse
    TCSProcess         = scenarioInputs.TCSProcess
    TCSProcessInputs   = scenarioInputs.TCSProcessInputs

    days             = regionalInputs.days
    hrs              = regionalInputs.hrs
    equipDiscount    = regionalInputs.equipDiscount
    capexFactor      = regionalInputs.capexFactor
    capitalRecRate   = regionalInputs.capitalRecRate
    equipRecLife     = regionalInputs.equipRecLife
    buildingLife     = regionalInputs.buildingLife
    workingCapPeriod = regionalInputs.workingCapPeriod
    skilledWage      = regionalInputs.skilledWage
    unskilledWage    = regionalInputs.unskilledWage
    salary           = regionalInputs.salary
    indirectLabor    = regionalInputs.indirectLabor
    benefitFactor    = regionalInputs.benefitFactor
    laborFactor      = regionalInputs.laborFactor
    natGasPrice      = regionalInputs.natGasPrice
    elecPrice        = regionalInputs.elecPrice
    elecFactor       = regionalInputs.elecFactor
    buildingCostSQF  = regionalInputs.buildingCostSQF
    CR10KCost        = regionalInputs.CR10KCost
    CR1KCost         = regionalInputs.CR1KCost
    CR100Cost        = regionalInputs.CR100Cost

    if inUse == 'False':
        costSummary, cumRejectionRate = skipStep()
        reactorThroughput, totalSiPerRod, usableSiPerRod, effProductionVol = 0, 0, 0, 0
    else:
        
        # define siemens CVD mfg step input parameters

        h2Gas                       = currentInputs.siemensCVDInputs['Value']['Hydrogen Consumption Rate']                        # kg/hr-station
        h2Price                     = currentInputs.siemensCVDInputs['Value']['Hydrogen Price']                                   # $/kg
        h2ScrapRate                 = currentInputs.siemensCVDInputs['Value']['Hydrogen Scrap Rate']                              # %
        
        materialScrapRate           = currentInputs.siemensCVDInputs['Value']['Material Scrap Rate']                              # %
        polySiRejectRate            = currentInputs.siemensCVDInputs['Value']['Poly Si Reject Rate']                              # %
        polySiScrapReclRate         = currentInputs.siemensCVDInputs['Value']['Poly Si Scrap Rec Rate']                           # %
        avgDowntime                 = currentInputs.siemensCVDInputs['Value']['Average Downtime']                                 # %
        
        otherConsumableCost         = currentInputs.siemensCVDInputs['Value']['Other Consumable Cost']                            # $/kg PS
        batchSize                   = currentInputs.siemensCVDInputs['Value']['Batch Size']                                       # rods/batch
        finalRodSize                = currentInputs.siemensCVDInputs['Value']['Final Rod Size']                                   # mm diameter
        
        inputCycleTime              = currentInputs.siemensCVDInputs['Value']['Cycle Time']                                       # hrs/batch
        processTime                 = currentInputs.siemensCVDInputs['Value']['Setup, Harvest, Clean Time']                       # hrs/batch
        baseCapEx                   = currentInputs.siemensCVDInputs['Value']['Capital Investment']                               # $/station
        
        auxEquipInvest              = currentInputs.siemensCVDInputs['Value']['Auxiliary Equipment Investment']                   # % 
        installFactor               = currentInputs.siemensCVDInputs['Value']['Installation Cost Factor']
        equipMaintCost              = currentInputs.siemensCVDInputs['Value']['Equipment Maintenance Cost Factor']                # %
        
        unskilledDirectLaborers     = currentInputs.siemensCVDInputs['Value']['Unskilled Direct Laborers Factor'] * laborFactor   # ppl/station
        skilledDirectLaborers       = currentInputs.siemensCVDInputs['Value']['Skilled Direct Laborers Factor'] * laborFactor     # ppl/station
        
        toolinglInvestment          = currentInputs.siemensCVDInputs['Value']['Tooling Investment']                               # per toolset
        toolingLife                 = currentInputs.siemensCVDInputs['Value']['Tooling Life']                                     # kgs/tool
        
        operatingPowerConsumption   = currentInputs.siemensCVDInputs['Value']['Operating Power Consumption']                      # kW
        floorSQM                    = currentInputs.siemensCVDInputs['Value']['Floor SQM']                                        # sq m
        clean10KSQM                 = currentInputs.siemensCVDInputs['Value']['Clean 10k SQM']                                    # sq m
        clean1KSQM                  = currentInputs.siemensCVDInputs['Value']['Clean 1k SQM']                                     # sq m
        clean100SQM                 = currentInputs.siemensCVDInputs['Value']['Clean 100 SQM']                                    # sq m
        
        
        # intermediate calculations
        
        cumRejectionRate = 1 - (1 - (materialScrapRate + polySiRejectRate) * (1 - polySiScrapReclRate))*(1 - harvestChunkRejRate *(1 - polySiScrapReclRate))
        effProductionVol = annualProdVol / (1 - cumRejectionRate)
        
        totalSiPerRod = (np.pi * (finalRodSize / 20)**2 * currentInputs.ingotGrowthInputs['Value']['Ingot Length'] * 2.33/1000) 
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
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, operatingPowerConsumption, equipMaintCost, scenarioInputs, regionalInputs)
        
    return costSummary, reactorThroughput, cumRejectionRate, totalSiPerRod, usableSiPerRod, effProductionVol


def etchFilaments(inUse, siemensCVDRejRate, usableSiPerRod, siemensEffProd, currentInputs, scenarioInputs, regionalInputs):
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
    
    region             = scenarioInputs.region
    annualProdVol      = scenarioInputs.annualProdVol
    plantLife          = scenarioInputs.plantLife
    dedicatedEquip     = scenarioInputs.dedicatedEquip
    harvestChunkInUse  = scenarioInputs.harvestChunkInUse
    siemensCVDInUse    = scenarioInputs.siemensCVDInUse
    etchFilamentsInUse = scenarioInputs.etchFilamentsInUse
    machineFilInUse    = scenarioInputs.machineFilInUse
    sawIngotInUse      = scenarioInputs.sawIngotInUse
    cropIngotInUse     = scenarioInputs.cropIngotInUse
    annealIngotInUse   = scenarioInputs.annealIngotInUse
    growIngotInUse     = scenarioInputs.growIngotInUse
    TCSInUse           = scenarioInputs.TCSInUse
    TCSProcess         = scenarioInputs.TCSProcess
    TCSProcessInputs   = scenarioInputs.TCSProcessInputs

    days             = regionalInputs.days
    hrs              = regionalInputs.hrs
    equipDiscount    = regionalInputs.equipDiscount
    capexFactor      = regionalInputs.capexFactor
    capitalRecRate   = regionalInputs.capitalRecRate
    equipRecLife     = regionalInputs.equipRecLife
    buildingLife     = regionalInputs.buildingLife
    workingCapPeriod = regionalInputs.workingCapPeriod
    skilledWage      = regionalInputs.skilledWage
    unskilledWage    = regionalInputs.unskilledWage
    salary           = regionalInputs.salary
    indirectLabor    = regionalInputs.indirectLabor
    benefitFactor    = regionalInputs.benefitFactor
    laborFactor      = regionalInputs.laborFactor
    natGasPrice      = regionalInputs.natGasPrice
    elecPrice        = regionalInputs.elecPrice
    elecFactor       = regionalInputs.elecFactor
    buildingCostSQF  = regionalInputs.buildingCostSQF
    CR10KCost        = regionalInputs.CR10KCost
    CR1KCost         = regionalInputs.CR1KCost
    CR100Cost        = regionalInputs.CR100Cost

    if inUse == 'False': 
        costSummary, cumRejectionRate = skipStep()
        HPProduction = 0
    else:
        
        # define etch filaments input parameters

        HFGas                       = currentInputs.etchFilamentsInputs['Value']['HF Consumption Rate']                               # SCM/hr
        HFPrice                     = currentInputs.etchFilamentsInputs['Value']['HF Price']                                          # $/SCM
        NitricRate                  = currentInputs.etchFilamentsInputs['Value']['Nitric Consumption Rate']                           # kg/hr
        NitricPrice                 = currentInputs.etchFilamentsInputs['Value']['Nitric Acid Price']                                 # $/kg
        N2Gas                       = currentInputs.etchFilamentsInputs['Value']['Nitrogen Consumption Rate']                         # SCM/hr
        N2Price                     = currentInputs.etchFilamentsInputs['Value']['Nitrogen Price']                                    # $/SCM
        DIWater                     = currentInputs.etchFilamentsInputs['Value']['DI Water Consumption Rate']                         # m3
        DIWaterPrice                = currentInputs.etchFilamentsInputs['Value']['DI Water Price']                                    # $/m3
        
        materialScrapRate           = currentInputs.etchFilamentsInputs['Value']['Material Scrap Rate']                               # %
        partRejectRate              = currentInputs.etchFilamentsInputs['Value']['Part Reject Rate']                                  # %
        avgDowntime                 = currentInputs.etchFilamentsInputs['Value']['Average Downtime']                                  # %
        
        filamentBatchSize           = currentInputs.etchFilamentsInputs['Value']['Filament Batch Size']                               # filament/batch
        filamentSetupTime           = currentInputs.etchFilamentsInputs['Value']['Filament Setup Time']                               # min/batch
        filamentCycleTime           = currentInputs.etchFilamentsInputs['Value']['Filament Cycle Time']                               # min/batch
        
        HPBatchSize                 = currentInputs.etchFilamentsInputs['Value']['HP Batch Size']                                     # kg hair pin /batch
        HPSetupTime                 = currentInputs.etchFilamentsInputs['Value']['HP Setup Time']                                     # min/batch
        HPCycleTime                 = currentInputs.etchFilamentsInputs['Value']['HP Cycle Time']                                     # min/batch
        
        baseCapEx                   = currentInputs.etchFilamentsInputs['Value']['Capital Investment']                                # $/station
        
        auxEquipInvest              = currentInputs.TCSInputs['Value']['Auxiliary Equipment Investment']                              # %, Note: In Excel model, set equal to the input value used for TCS mfg step... 
        installFactor               = currentInputs.etchFilamentsInputs['Value']['Installation Cost Factor']
        equipMaintCost              = currentInputs.etchFilamentsInputs['Value']['Equipment Maintenance Cost Factor']                 # %
        
        unskilledDirectLaborers     = currentInputs.etchFilamentsInputs['Value']['Unskilled Direct Laborers Factor'] * laborFactor    # ppl/station
        skilledDirectLaborers       = currentInputs.etchFilamentsInputs['Value']['Skilled Direct Laborers Factor'] * laborFactor      # ppl/station
        
        toolinglInvestment          = currentInputs.etchFilamentsInputs['Value']['Tooling Investment']                                # per toolset
        toolingLife                 = currentInputs.etchFilamentsInputs['Value']['Tooling Life']                                      # kgs/tool
        
        operatingPowerConsumption   = currentInputs.etchFilamentsInputs['Value']['Operating Power Consumption']                       # kW
        floorSQM                    = currentInputs.etchFilamentsInputs['Value']['Floor SQM']                                         # sq m
        clean10KSQM                 = currentInputs.etchFilamentsInputs['Value']['Clean 10k SQM']                                     # sq m
        clean1KSQM                  = currentInputs.etchFilamentsInputs['Value']['Clean 1k SQM']                                      # sq m
        clean100SQM                 = currentInputs.etchFilamentsInputs['Value']['Clean 100 SQM']                                     # sq m
        
        virginFilament              = currentInputs.etchFilamentsInputs['Value']['Fraction Virgin Filament']                          # %
        
        
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
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, operatingPowerConsumption, equipMaintCost, scenarioInputs, regionalInputs)
        
        
    return costSummary, cumRejectionRate, HPProduction


def machineFilaments(inUse, etchRejectionRate, totalSiPerRod, currentInputs, scenarioInputs, regionalInputs):
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
    
    region             = scenarioInputs.region
    annualProdVol      = scenarioInputs.annualProdVol
    plantLife          = scenarioInputs.plantLife
    dedicatedEquip     = scenarioInputs.dedicatedEquip
    harvestChunkInUse  = scenarioInputs.harvestChunkInUse
    siemensCVDInUse    = scenarioInputs.siemensCVDInUse
    etchFilamentsInUse = scenarioInputs.etchFilamentsInUse
    machineFilInUse    = scenarioInputs.machineFilInUse
    sawIngotInUse      = scenarioInputs.sawIngotInUse
    cropIngotInUse     = scenarioInputs.cropIngotInUse
    annealIngotInUse   = scenarioInputs.annealIngotInUse
    growIngotInUse     = scenarioInputs.growIngotInUse
    TCSInUse           = scenarioInputs.TCSInUse
    TCSProcess         = scenarioInputs.TCSProcess
    TCSProcessInputs   = scenarioInputs.TCSProcessInputs

    days             = regionalInputs.days
    hrs              = regionalInputs.hrs
    equipDiscount    = regionalInputs.equipDiscount
    capexFactor      = regionalInputs.capexFactor
    capitalRecRate   = regionalInputs.capitalRecRate
    equipRecLife     = regionalInputs.equipRecLife
    buildingLife     = regionalInputs.buildingLife
    workingCapPeriod = regionalInputs.workingCapPeriod
    skilledWage      = regionalInputs.skilledWage
    unskilledWage    = regionalInputs.unskilledWage
    salary           = regionalInputs.salary
    indirectLabor    = regionalInputs.indirectLabor
    benefitFactor    = regionalInputs.benefitFactor
    laborFactor      = regionalInputs.laborFactor
    natGasPrice      = regionalInputs.natGasPrice
    elecPrice        = regionalInputs.elecPrice
    elecFactor       = regionalInputs.elecFactor
    buildingCostSQF  = regionalInputs.buildingCostSQF
    CR10KCost        = regionalInputs.CR10KCost
    CR1KCost         = regionalInputs.CR1KCost
    CR100Cost        = regionalInputs.CR100Cost

    if inUse == 'False': 
        costSummary, cumRejectionRate = skipStep()
    else:
        
        # define etch filaments input parameters

        consumableRate              = currentInputs.machineFilamentsInputs['Value']['Consumable Rate']                                    # unit/hr
        consumablePrice             = currentInputs.machineFilamentsInputs['Value']['Consumable Price']                                   # $/unit
        
        materialScrapRate           = currentInputs.machineFilamentsInputs['Value']['Material Scrap Rate']                                # %
        yieldLoss                   = currentInputs.machineFilamentsInputs['Value']['Yield Loss']                                         # %
        scrapRecRate                = currentInputs.machineFilamentsInputs['Value']['Scrap Reclamation Rate']
        avgDowntime                 = currentInputs.machineFilamentsInputs['Value']['Average Downtime']                                   # %
        
        filamentBatchSize           = currentInputs.machineFilamentsInputs['Value']['Filament Batch Size']                                # filament/batch
        filamentSetupTime           = currentInputs.machineFilamentsInputs['Value']['Filament Setup Time']                                # min/batch
        filamentCycleTime           = currentInputs.machineFilamentsInputs['Value']['Filament Cycle Time']                                # min/batch
        
        baseCapEx                   = currentInputs.machineFilamentsInputs['Value']['Capital Investment']                                 # $/station
        
        auxEquipInvest              = currentInputs.machineFilamentsInputs['Value']['Auxiliary Equipment Investment']                     # %
        installFactor               = currentInputs.machineFilamentsInputs['Value']['Installation Cost Factor']
        equipMaintCost              = currentInputs.machineFilamentsInputs['Value']['Equipment Maintenance Cost Factor']                  # %
        
        unskilledDirectLaborers     = currentInputs.machineFilamentsInputs['Value']['Unskilled Direct Laborers Factor'] * laborFactor     # ppl/station
        skilledDirectLaborers       = currentInputs.machineFilamentsInputs['Value']['Skilled Direct Laborers Factor'] * laborFactor       # ppl/station
        
        toolinglInvestment          = currentInputs.machineFilamentsInputs['Value']['Tooling Investment']                                 # per toolset
        toolingLife                 = currentInputs.machineFilamentsInputs['Value']['Tooling Life']                                       # kgs/tool
        
        operatingPowerConsumption   = currentInputs.machineFilamentsInputs['Value']['Operating Power Consumption']                        # kW
        floorSQM                    = currentInputs.machineFilamentsInputs['Value']['Floor SQM']                                          # sq m
        clean10KSQM                 = currentInputs.machineFilamentsInputs['Value']['Clean 10k SQM']                                      # sq m
        clean1KSQM                  = currentInputs.machineFilamentsInputs['Value']['Clean 1k SQM']                                       # sq m
        clean100SQM                 = currentInputs.machineFilamentsInputs['Value']['Clean 100 SQM']                                      # sq m
        
        ingotGrossWeight = grossIngotWeight(currentInputs.ingotGrowthInputs['Value']['Ingot Length'], currentInputs.ingotGrowthInputs['Value']['Ingot Weight (tops and tails)'], currentInputs.ingotGrowthInputs['Value']['As Grown Ingot Diameter'])
        growthBatchSize = sizeFilamentBatch(currentInputs.ingotGrowthInputs['Value']['Final Ingot Diameter'], currentInputs.sawIngotsInputs['Value']['Filament Width'], currentInputs.sawIngotsInputs['Value']['Kerf Loss'])

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
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, operatingPowerConsumption, equipMaintCost, scenarioInputs, regionalInputs)
        
        
    return costSummary, cumRejectionRate


def sawIngots(inUse, machineRejectRate, usableSiPerRod, totalSiPerRod, currentInputs, scenarioInputs, regionalInputs):
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
    
    region             = scenarioInputs.region
    annualProdVol      = scenarioInputs.annualProdVol
    plantLife          = scenarioInputs.plantLife
    dedicatedEquip     = scenarioInputs.dedicatedEquip
    harvestChunkInUse  = scenarioInputs.harvestChunkInUse
    siemensCVDInUse    = scenarioInputs.siemensCVDInUse
    etchFilamentsInUse = scenarioInputs.etchFilamentsInUse
    machineFilInUse    = scenarioInputs.machineFilInUse
    sawIngotInUse      = scenarioInputs.sawIngotInUse
    cropIngotInUse     = scenarioInputs.cropIngotInUse
    annealIngotInUse   = scenarioInputs.annealIngotInUse
    growIngotInUse     = scenarioInputs.growIngotInUse
    TCSInUse           = scenarioInputs.TCSInUse
    TCSProcess         = scenarioInputs.TCSProcess
    TCSProcessInputs   = scenarioInputs.TCSProcessInputs

    days             = regionalInputs.days
    hrs              = regionalInputs.hrs
    equipDiscount    = regionalInputs.equipDiscount
    capexFactor      = regionalInputs.capexFactor
    capitalRecRate   = regionalInputs.capitalRecRate
    equipRecLife     = regionalInputs.equipRecLife
    buildingLife     = regionalInputs.buildingLife
    workingCapPeriod = regionalInputs.workingCapPeriod
    skilledWage      = regionalInputs.skilledWage
    unskilledWage    = regionalInputs.unskilledWage
    salary           = regionalInputs.salary
    indirectLabor    = regionalInputs.indirectLabor
    benefitFactor    = regionalInputs.benefitFactor
    laborFactor      = regionalInputs.laborFactor
    natGasPrice      = regionalInputs.natGasPrice
    elecPrice        = regionalInputs.elecPrice
    elecFactor       = regionalInputs.elecFactor
    buildingCostSQF  = regionalInputs.buildingCostSQF
    CR10KCost        = regionalInputs.CR10KCost
    CR1KCost         = regionalInputs.CR1KCost
    CR100Cost        = regionalInputs.CR100Cost

    if inUse == 'False': 
        costSummary, cumRejectionRate = skipStep()
    else:
        
        # define etch filaments input parameters

        wireLife                    = currentInputs.sawIngotsInputs['Value']['Wire Life']                                         # batches
        wireCost                    = currentInputs.sawIngotsInputs['Value']['Wire Cost']                                         # $/wire
        
        SiCSlurryConsumption        = currentInputs.sawIngotsInputs['Value']['SiC Slurry Consumption']                            # kg/hr
        SiCSlurryPrice              = currentInputs.sawIngotsInputs['Value']['SiC Slurry Price']                                  # $/kg
        SiCSlurryScrap              = currentInputs.sawIngotsInputs['Value']['SiC Slurry Scrap Rate']                             # %
        
        kerfLoss                    = currentInputs.sawIngotsInputs['Value']['Kerf Loss']                                         # microns
        sellKerf                    = currentInputs.sawIngotsInputs['Value']['Sell Kerf Loss Si?']                                # 1=Yes, 0=No
        kerfPrice                   = currentInputs.sawIngotsInputs['Value']['Kerf Loss Si Price']                                # $/kg
        partRejectRate              = currentInputs.sawIngotsInputs['Value']['Part Reject Rate']                                  # %
        
        avgDowntime                 = currentInputs.sawIngotsInputs['Value']['Average Downtime']                                  # %
        
        batchSize                   = currentInputs.sawIngotsInputs['Value']['Batch Size']                                        # ingot/batch
        setupTime                   = currentInputs.sawIngotsInputs['Value']['Setup Time']                                        # min/batch
        cutSpeed                    = currentInputs.sawIngotsInputs['Value']['Cutting Speed']                                     # mm/min
        
        baseCapEx                   = currentInputs.sawIngotsInputs['Value']['Capital Investment']                                # $/station
        
        auxEquipInvest              = currentInputs.sawIngotsInputs['Value']['Auxiliary Equipment Investment']                    # %
        installFactor               = currentInputs.sawIngotsInputs['Value']['Installation Cost Factor']
        equipMaintCost              = currentInputs.sawIngotsInputs['Value']['Equipment Maintenance Cost Factor']                 # %
        
        unskilledDirectLaborers     = currentInputs.sawIngotsInputs['Value']['Unskilled Direct Laborers Factor'] * laborFactor    # ppl/station
        skilledDirectLaborers       = currentInputs.sawIngotsInputs['Value']['Skilled Direct Laborers Factor'] * laborFactor      # ppl/station
        
        toolinglInvestment          = currentInputs.sawIngotsInputs['Value']['Tooling Investment']                                # per toolset
        toolingLife                 = currentInputs.sawIngotsInputs['Value']['Tooling Life']                                      # kgs/tool
        
        operatingPowerConsumption   = currentInputs.sawIngotsInputs['Value']['Operating Power Consumption']                       # kW
        floorSQM                    = currentInputs.sawIngotsInputs['Value']['Floor SQM']                                         # sq m
        clean10KSQM                 = currentInputs.sawIngotsInputs['Value']['Clean 10k SQM']                                     # sq m
        clean1KSQM                  = currentInputs.sawIngotsInputs['Value']['Clean 1k SQM']                                      # sq m
        clean100SQM                 = currentInputs.sawIngotsInputs['Value']['Clean 100 SQM']                                     # sq m
        
        ingotLength                 = currentInputs.ingotGrowthInputs['Value']['Ingot Length']
        
        ingotGrossWeight = grossIngotWeight(currentInputs.ingotGrowthInputs['Value']['Ingot Length'], currentInputs.ingotGrowthInputs['Value']['Ingot Weight (tops and tails)'], currentInputs.ingotGrowthInputs['Value']['As Grown Ingot Diameter'])
        growthBatchSize = sizeFilamentBatch(currentInputs.ingotGrowthInputs['Value']['Final Ingot Diameter'], currentInputs.sawIngotsInputs['Value']['Filament Width'], currentInputs.sawIngotsInputs['Value']['Kerf Loss'])
        
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
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, operatingPowerConsumption, equipMaintCost, scenarioInputs, regionalInputs)
        
        
    return costSummary, cumRejectionRate


def cropIngots(inUse, sawRejectRate, totalSiPerRod, currentInputs, scenarioInputs, regionalInputs):
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
    
    region             = scenarioInputs.region
    annualProdVol      = scenarioInputs.annualProdVol
    plantLife          = scenarioInputs.plantLife
    dedicatedEquip     = scenarioInputs.dedicatedEquip
    harvestChunkInUse  = scenarioInputs.harvestChunkInUse
    siemensCVDInUse    = scenarioInputs.siemensCVDInUse
    etchFilamentsInUse = scenarioInputs.etchFilamentsInUse
    machineFilInUse    = scenarioInputs.machineFilInUse
    sawIngotInUse      = scenarioInputs.sawIngotInUse
    cropIngotInUse     = scenarioInputs.cropIngotInUse
    annealIngotInUse   = scenarioInputs.annealIngotInUse
    growIngotInUse     = scenarioInputs.growIngotInUse
    TCSInUse           = scenarioInputs.TCSInUse
    TCSProcess         = scenarioInputs.TCSProcess
    TCSProcessInputs   = scenarioInputs.TCSProcessInputs

    days             = regionalInputs.days
    hrs              = regionalInputs.hrs
    equipDiscount    = regionalInputs.equipDiscount
    capexFactor      = regionalInputs.capexFactor
    capitalRecRate   = regionalInputs.capitalRecRate
    equipRecLife     = regionalInputs.equipRecLife
    buildingLife     = regionalInputs.buildingLife
    workingCapPeriod = regionalInputs.workingCapPeriod
    skilledWage      = regionalInputs.skilledWage
    unskilledWage    = regionalInputs.unskilledWage
    salary           = regionalInputs.salary
    indirectLabor    = regionalInputs.indirectLabor
    benefitFactor    = regionalInputs.benefitFactor
    laborFactor      = regionalInputs.laborFactor
    natGasPrice      = regionalInputs.natGasPrice
    elecPrice        = regionalInputs.elecPrice
    elecFactor       = regionalInputs.elecFactor
    buildingCostSQF  = regionalInputs.buildingCostSQF
    CR10KCost        = regionalInputs.CR10KCost
    CR1KCost         = regionalInputs.CR1KCost
    CR100Cost        = regionalInputs.CR100Cost

    if inUse == 'False': 
        costSummary, cumRejectionRate = skipStep()
    else:
        
        # define etch filaments input parameters

        weightRemoved               = currentInputs.cropIngotsInputs['Value']['Weight of Sections Removed']                       # kg
        
        SiCSlurryConsumption        = currentInputs.cropIngotsInputs['Value']['SiC Slurry Consumption']                           # kg/hr
        SiCSlurryPrice              = currentInputs.cropIngotsInputs['Value']['SiC Slurry Price']                                 # $/kg
                
        bladeLife                   = currentInputs.cropIngotsInputs['Value']['Blade Life']                                       # batches
        bladeCost                   = currentInputs.cropIngotsInputs['Value']['Blade Cost']                                       # $/blade
        
        brickRejectRate             = currentInputs.cropIngotsInputs['Value']['Brick Reject Rate']                                # %
        scrapRecRate                = currentInputs.cropIngotsInputs['Value']['Scrap Reclamation Rate']                           # %
        
        avgDowntime                 = currentInputs.cropIngotsInputs['Value']['Average Downtime']                                 # %
        
        batchSize                   = currentInputs.cropIngotsInputs['Value']['Batch Size']                                       # ingot/batch
        setupTime                   = currentInputs.cropIngotsInputs['Value']['Setup Time']                                       # min/batch
        sawRate                     = currentInputs.cropIngotsInputs['Value']['Saw Rate']                                         # mm/min
        
        baseCapEx                   = currentInputs.cropIngotsInputs['Value']['Capital Investment']                               # $/station
        
        auxEquipInvest              = currentInputs.cropIngotsInputs['Value']['Auxiliary Equipment Investment']                   # %
        installFactor               = currentInputs.cropIngotsInputs['Value']['Installation Cost Factor']
        equipMaintCost              = currentInputs.cropIngotsInputs['Value']['Equipment Maintenance Cost Factor']                # %
        
        unskilledDirectLaborers     = currentInputs.cropIngotsInputs['Value']['Unskilled Direct Laborers Factor'] * laborFactor   # ppl/station
        skilledDirectLaborers       = currentInputs.cropIngotsInputs['Value']['Skilled Direct Laborers Factor'] * laborFactor     # ppl/station
        
        toolinglInvestment          = currentInputs.cropIngotsInputs['Value']['Tooling Investment']                               # per toolset
        toolingLife                 = currentInputs.cropIngotsInputs['Value']['Tooling Life']                                     # kgs/tool
        
        operatingPowerConsumption   = currentInputs.cropIngotsInputs['Value']['Operating Power Consumption']                      # kW
        floorSQM                    = currentInputs.cropIngotsInputs['Value']['Floor SQM']                                        # sq m
        clean10KSQM                 = currentInputs.cropIngotsInputs['Value']['Clean 10k SQM']                                    # sq m
        clean1KSQM                  = currentInputs.cropIngotsInputs['Value']['Clean 1k SQM']                                     # sq m
        clean100SQM                 = currentInputs.cropIngotsInputs['Value']['Clean 100 SQM']                                    # sq m
        
        ingotDiameter               = currentInputs.ingotGrowthInputs['Value']['As Grown Ingot Diameter']
        
        ingotGrossWeight = grossIngotWeight(currentInputs.ingotGrowthInputs['Value']['Ingot Length'], currentInputs.ingotGrowthInputs['Value']['Ingot Weight (tops and tails)'], currentInputs.ingotGrowthInputs['Value']['As Grown Ingot Diameter'])
        growthBatchSize = sizeFilamentBatch(currentInputs.ingotGrowthInputs['Value']['Final Ingot Diameter'], currentInputs.sawIngotsInputs['Value']['Filament Width'], currentInputs.sawIngotsInputs['Value']['Kerf Loss'])

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
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, operatingPowerConsumption, equipMaintCost, scenarioInputs, regionalInputs)
        
        
    return costSummary, cumRejectionRate


def annealIngots(inUse, cropRejectRate, totalSiPerRod, currentInputs, scenarioInputs, regionalInputs):
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
    
    region             = scenarioInputs.region
    annualProdVol      = scenarioInputs.annualProdVol
    plantLife          = scenarioInputs.plantLife
    dedicatedEquip     = scenarioInputs.dedicatedEquip
    harvestChunkInUse  = scenarioInputs.harvestChunkInUse
    siemensCVDInUse    = scenarioInputs.siemensCVDInUse
    etchFilamentsInUse = scenarioInputs.etchFilamentsInUse
    machineFilInUse    = scenarioInputs.machineFilInUse
    sawIngotInUse      = scenarioInputs.sawIngotInUse
    cropIngotInUse     = scenarioInputs.cropIngotInUse
    annealIngotInUse   = scenarioInputs.annealIngotInUse
    growIngotInUse     = scenarioInputs.growIngotInUse
    TCSInUse           = scenarioInputs.TCSInUse
    TCSProcess         = scenarioInputs.TCSProcess
    TCSProcessInputs   = scenarioInputs.TCSProcessInputs

    days             = regionalInputs.days
    hrs              = regionalInputs.hrs
    equipDiscount    = regionalInputs.equipDiscount
    capexFactor      = regionalInputs.capexFactor
    capitalRecRate   = regionalInputs.capitalRecRate
    equipRecLife     = regionalInputs.equipRecLife
    buildingLife     = regionalInputs.buildingLife
    workingCapPeriod = regionalInputs.workingCapPeriod
    skilledWage      = regionalInputs.skilledWage
    unskilledWage    = regionalInputs.unskilledWage
    salary           = regionalInputs.salary
    indirectLabor    = regionalInputs.indirectLabor
    benefitFactor    = regionalInputs.benefitFactor
    laborFactor      = regionalInputs.laborFactor
    natGasPrice      = regionalInputs.natGasPrice
    elecPrice        = regionalInputs.elecPrice
    elecFactor       = regionalInputs.elecFactor
    buildingCostSQF  = regionalInputs.buildingCostSQF
    CR10KCost        = regionalInputs.CR10KCost
    CR1KCost         = regionalInputs.CR1KCost
    CR100Cost        = regionalInputs.CR100Cost

    if inUse == 'False': 
        costSummary, cumRejectionRate = skipStep()
    else:
        
        # define input parameters

        argonGas                    = currentInputs.annealIngotsInputs['Value']['Argon Gas']                                          # SLM
        argonPrice                  = currentInputs.annealIngotsInputs['Value']['Argon Price']                                        # $/std liter
        argonScrapRate              = currentInputs.annealIngotsInputs['Value']['Argon Scrap Rate']                                   # %
        
        polySiYieldLossRate         = currentInputs.annealIngotsInputs['Value']['Poly Si Chunk Yield Loss Rate']                      # %
        polySiScrapReclRate         = currentInputs.annealIngotsInputs['Value']['Poly Si Scrap Reclamation Rate']                     # %
        
        avgDowntime                 = currentInputs.annealIngotsInputs['Value']['Average Downtime']                                   # %
        
        furnaceCap                  = currentInputs.annealIngotsInputs['Value']['Furnace Capacity']                                   # kg/hr
        
        baseCapEx                   = currentInputs.annealIngotsInputs['Value']['Capital Investment']                                 # $/station
        
        auxEquipInvest              = currentInputs.annealIngotsInputs['Value']['Auxiliary Equipment Investment']                     # %
        installFactor               = currentInputs.annealIngotsInputs['Value']['Installation Cost Factor']
        equipMaintCost              = currentInputs.annealIngotsInputs['Value']['Equipment Maintenance Cost Factor']                  # %
        
        unskilledDirectLaborers     = currentInputs.annealIngotsInputs['Value']['Unskilled Direct Laborers Factor'] * laborFactor     # ppl/station
        skilledDirectLaborers       = currentInputs.annealIngotsInputs['Value']['Skilled Direct Laborers Factor'] * laborFactor       # ppl/station
        
        toolinglInvestment          = currentInputs.annealIngotsInputs['Value']['Tooling Investment']                                 # per toolset
        toolingLife                 = currentInputs.annealIngotsInputs['Value']['Tooling Life']                                       # kgs/tool
        
        operatingPowerConsumption   = currentInputs.annealIngotsInputs['Value']['Operating Power Consumption']                        # kW
        floorSQM                    = currentInputs.annealIngotsInputs['Value']['Floor SQM']                                          # sq m
        clean10KSQM                 = currentInputs.annealIngotsInputs['Value']['Clean 10k SQM']                                      # sq m
        clean1KSQM                  = currentInputs.annealIngotsInputs['Value']['Clean 1k SQM']                                       # sq m
        clean100SQM                 = currentInputs.annealIngotsInputs['Value']['Clean 100 SQM']                                      # sq m
                
        ingotGrossWeight = grossIngotWeight(currentInputs.ingotGrowthInputs['Value']['Ingot Length'], currentInputs.ingotGrowthInputs['Value']['Ingot Weight (tops and tails)'], currentInputs.ingotGrowthInputs['Value']['As Grown Ingot Diameter'])
        growthBatchSize = sizeFilamentBatch(currentInputs.ingotGrowthInputs['Value']['Final Ingot Diameter'], currentInputs.sawIngotsInputs['Value']['Filament Width'], currentInputs.sawIngotsInputs['Value']['Kerf Loss'])

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
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, operatingPowerConsumption, equipMaintCost, scenarioInputs, regionalInputs)
        
        
    return costSummary, cumRejectionRate


def ingnotGrowth(inUse, annealRejectRate, usableSiPerRod, currentInputs, scenarioInputs, regionalInputs):
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
    
    region             = scenarioInputs.region
    annualProdVol      = scenarioInputs.annualProdVol
    plantLife          = scenarioInputs.plantLife
    dedicatedEquip     = scenarioInputs.dedicatedEquip
    harvestChunkInUse  = scenarioInputs.harvestChunkInUse
    siemensCVDInUse    = scenarioInputs.siemensCVDInUse
    etchFilamentsInUse = scenarioInputs.etchFilamentsInUse
    machineFilInUse    = scenarioInputs.machineFilInUse
    sawIngotInUse      = scenarioInputs.sawIngotInUse
    cropIngotInUse     = scenarioInputs.cropIngotInUse
    annealIngotInUse   = scenarioInputs.annealIngotInUse
    growIngotInUse     = scenarioInputs.growIngotInUse
    TCSInUse           = scenarioInputs.TCSInUse
    TCSProcess         = scenarioInputs.TCSProcess
    TCSProcessInputs   = scenarioInputs.TCSProcessInputs

    days             = regionalInputs.days
    hrs              = regionalInputs.hrs
    equipDiscount    = regionalInputs.equipDiscount
    capexFactor      = regionalInputs.capexFactor
    capitalRecRate   = regionalInputs.capitalRecRate
    equipRecLife     = regionalInputs.equipRecLife
    buildingLife     = regionalInputs.buildingLife
    workingCapPeriod = regionalInputs.workingCapPeriod
    skilledWage      = regionalInputs.skilledWage
    unskilledWage    = regionalInputs.unskilledWage
    salary           = regionalInputs.salary
    indirectLabor    = regionalInputs.indirectLabor
    benefitFactor    = regionalInputs.benefitFactor
    laborFactor      = regionalInputs.laborFactor
    natGasPrice      = regionalInputs.natGasPrice
    elecPrice        = regionalInputs.elecPrice
    elecFactor       = regionalInputs.elecFactor
    buildingCostSQF  = regionalInputs.buildingCostSQF
    CR10KCost        = regionalInputs.CR10KCost
    CR1KCost         = regionalInputs.CR1KCost
    CR100Cost        = regionalInputs.CR100Cost

    if inUse == 'False': 
        costSummary, cumRejectionRate = skipStep()
    else:
        
        # define input parameters
        
        polySiPrice                 = currentInputs.ingotGrowthInputs['Value']['Poly-Si Material Price']                          # $/kg
        polySiScrapRate             = currentInputs.ingotGrowthInputs['Value']['Poly Si Material Scrap Rate']                     # %
        
        SiSeedPrice                 = currentInputs.ingotGrowthInputs['Value']['Si Seed Price']                                   # $/pc
        SiSeedLife                  = currentInputs.ingotGrowthInputs['Value']['Si Seed Life']                                    # cycles
        crucibleCost                = currentInputs.ingotGrowthInputs['Value']['Crucible Cost']                                   # $/charge
        crucibleLife                = currentInputs.ingotGrowthInputs['Value']['Crucible Life']                                   # batches/crucible
        waterConsumption            = currentInputs.ingotGrowthInputs['Value']['Cooling Water Cons Rate']                         # m3/batch
        waterPrice                  = currentInputs.ingotGrowthInputs['Value']['Water Price']                                     # $/m3
        argonGas                    = currentInputs.ingotGrowthInputs['Value']['Argon Consumption Rate']                          # SLM
        argonPrice                  = currentInputs.ingotGrowthInputs['Value']['Argon Price']                                     # $/std liter
        partRejectRate              = currentInputs.ingotGrowthInputs['Value']['Part Reject Rate']                                # %
        
        avgDowntime                 = currentInputs.ingotGrowthInputs['Value']['Average Downtime']                                # %
        
        ingotLength                 = currentInputs.ingotGrowthInputs['Value']['Ingot Length']                                    # cm
        setupTime                   = currentInputs.ingotGrowthInputs['Value']['Setup (Load) Time']                               # hrs/batch
        pumpTime                    = currentInputs.ingotGrowthInputs['Value']['Pump Down and Leak Check']                        # hrs/batch
        meltTime                    = currentInputs.ingotGrowthInputs['Value']['Melt/Stabilize']                                  # hrs/batch
        pullSpeed                   = currentInputs.ingotGrowthInputs['Value']['Average Pull Speed']                              # mm/hr
        coolTime                    = currentInputs.ingotGrowthInputs['Value']['Cool and Unload']                                 # hrs/batch
        cleanTime                   = currentInputs.ingotGrowthInputs['Value']['Clean']                                           # hrs/batch
        
        baseCapEx                   = currentInputs.ingotGrowthInputs['Value']['Capital Investment']                              # $/station
        
        auxEquipInvest              = currentInputs.ingotGrowthInputs['Value']['Auxiliary Equipment Investment']                  # %
        installFactor               = currentInputs.ingotGrowthInputs['Value']['Installation Cost Factor']
        equipMaintCost              = currentInputs.ingotGrowthInputs['Value']['Equipment Maintenance Cost Factor']               # %
        
        unskilledDirectLaborers     = currentInputs.ingotGrowthInputs['Value']['Unskilled Direct Laborers Factor'] * laborFactor  # ppl/station
        skilledDirectLaborers       = currentInputs.ingotGrowthInputs['Value']['Skilled Direct Laborers Factor'] * laborFactor    # ppl/station
        
        toolinglInvestment          = currentInputs.ingotGrowthInputs['Value']['Tooling Investment']                              # per toolset
        toolingLife                 = currentInputs.ingotGrowthInputs['Value']['Tooling Life']                                    # kgs/tool
        
        operatingPowerConsumption   = currentInputs.ingotGrowthInputs['Value']['Operating Power Consumption']                     # kW
        fullPowerConsumption        = currentInputs.ingotGrowthInputs['Value']['Full Power Consumption']                          # kW
        floorSQM                    = currentInputs.ingotGrowthInputs['Value']['Floor SQM']                                       # sq m
        clean10KSQM                 = currentInputs.ingotGrowthInputs['Value']['Clean 10k SQM']                                   # sq m
        clean1KSQM                  = currentInputs.ingotGrowthInputs['Value']['Clean 1k SQM']                                    # sq m
        clean100SQM                 = currentInputs.ingotGrowthInputs['Value']['Clean 100 SQM']                                   # sq m
                
        ingotGrossWeight = grossIngotWeight(currentInputs.ingotGrowthInputs['Value']['Ingot Length'], currentInputs.ingotGrowthInputs['Value']['Ingot Weight (tops and tails)'], currentInputs.ingotGrowthInputs['Value']['As Grown Ingot Diameter'])
        growthBatchSize = sizeFilamentBatch(currentInputs.ingotGrowthInputs['Value']['Final Ingot Diameter'], currentInputs.sawIngotsInputs['Value']['Filament Width'], currentInputs.sawIngotsInputs['Value']['Kerf Loss'])

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
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, adjPowerConsumption, equipMaintCost, scenarioInputs, regionalInputs)
        
        
    return costSummary, cumRejectionRate


def TCS(inUse, operation, siemensCVDRejRate, HPProduction, siemensEffProd, currentInputs, scenarioInputs, regionalInputs):
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
    
    region             = scenarioInputs.region
    annualProdVol      = scenarioInputs.annualProdVol
    plantLife          = scenarioInputs.plantLife
    dedicatedEquip     = scenarioInputs.dedicatedEquip
    harvestChunkInUse  = scenarioInputs.harvestChunkInUse
    siemensCVDInUse    = scenarioInputs.siemensCVDInUse
    etchFilamentsInUse = scenarioInputs.etchFilamentsInUse
    machineFilInUse    = scenarioInputs.machineFilInUse
    sawIngotInUse      = scenarioInputs.sawIngotInUse
    cropIngotInUse     = scenarioInputs.cropIngotInUse
    annealIngotInUse   = scenarioInputs.annealIngotInUse
    growIngotInUse     = scenarioInputs.growIngotInUse
    TCSInUse           = scenarioInputs.TCSInUse
    TCSProcess         = scenarioInputs.TCSProcess
    TCSProcessInputs   = scenarioInputs.TCSProcessInputs

    days             = regionalInputs.days
    hrs              = regionalInputs.hrs
    equipDiscount    = regionalInputs.equipDiscount
    capexFactor      = regionalInputs.capexFactor
    capitalRecRate   = regionalInputs.capitalRecRate
    equipRecLife     = regionalInputs.equipRecLife
    buildingLife     = regionalInputs.buildingLife
    workingCapPeriod = regionalInputs.workingCapPeriod
    skilledWage      = regionalInputs.skilledWage
    unskilledWage    = regionalInputs.unskilledWage
    salary           = regionalInputs.salary
    indirectLabor    = regionalInputs.indirectLabor
    benefitFactor    = regionalInputs.benefitFactor
    laborFactor      = regionalInputs.laborFactor
    natGasPrice      = regionalInputs.natGasPrice
    elecPrice        = regionalInputs.elecPrice
    elecFactor       = regionalInputs.elecFactor
    buildingCostSQF  = regionalInputs.buildingCostSQF
    CR10KCost        = regionalInputs.CR10KCost
    CR1KCost         = regionalInputs.CR1KCost
    CR100Cost        = regionalInputs.CR100Cost

    if inUse == 'False': 
        costSummary, cumRejectionRate = skipStep()
    else:
        
        # define input parameters
        
        MGSiUsage                   = currentInputs.TCSInputs['Value']['MG Si Usage Factor']                              # kg/kg MG Si
        MGSiPrice                   = currentInputs.TCSInputs['Value']['MG Si Price']                                     # $/kg
        MGSiScrapRate               = currentInputs.TCSInputs['Value']['MG Si Scrap Rate']                                # %
        
        HClUsage                    = currentInputs.TCSInputs['Value']['HCl Usage Factor']                                # kg/kg MG Si
        HClPrice                    = currentInputs.TCSInputs['Value']['HCl Price']                                       # $/pc
        HClScrapRate                = currentInputs.TCSInputs['Value']['HCl Scrap Rate']                                  # %
        
        H2Usage                     = currentInputs.TCSInputs['Value']['Hydrogen Usage Factor']                           # kg/kg MG Si
        H2Price                     = currentInputs.TCSInputs['Value']['Hydrogen Price']                                  # $/kg
        
        otherScrapRate              = currentInputs.TCSInputs['Value']['Other Material Scrap Rate']                       # %
        
        avgDowntime                 = currentInputs.TCSInputs['Value']['Average Downtime']                                # %
                
        auxEquipInvest              = currentInputs.TCSInputs['Value']['Auxiliary Equipment Investment']                  # %
        installFactor               = currentInputs.TCSInputs['Value']['Installation Cost Factor']                        # %
        equipMaintCost              = currentInputs.TCSInputs['Value']['Equipment Maintenance Cost Factor']               # %
        
        unskilledDirectLaborers     = currentInputs.TCSInputs['Value']['Unskilled Direct Laborers Factor'] * laborFactor  # ppl/station
        skilledDirectLaborers       = currentInputs.TCSInputs['Value']['Skilled Direct Laborers Factor'] * laborFactor    # ppl/station
        
        toolinglInvestment          = currentInputs.TCSInputs['Value']['Tooling Investment']                              # per toolset
        toolingLife                 = currentInputs.TCSInputs['Value']['Tooling Life']                                    # kgs/tool
        
        clean10KSQM                 = currentInputs.TCSInputs['Value']['Clean 10k SQM']                                   # sq m
        clean1KSQM                  = currentInputs.TCSInputs['Value']['Clean 1k SQM']                                    # sq m
        clean100SQM                 = currentInputs.TCSInputs['Value']['Clean 100 SQM']                                   # sq m
                
        
        # intermediate calculations
        
        cumRejectionRate = siemensCVDRejRate
        effProductionVol = annualProdVol / (1 - cumRejectionRate)
        
        grossProd = siemensEffProd * 1000
        MGSiCost = ((effProductionVol - HPProduction) / effProductionVol) * grossProd * MGSiPrice * MGSiUsage / (1 - MGSiScrapRate)
        HClCost = grossProd * HClUsage * HClPrice / (1 - HClScrapRate)
        H2Cost = H2Usage * H2Price * grossProd / (1 - otherScrapRate)
        wasteCost = dfSelect(TCSProcessInputs, operation, 'Waste $/kg TCS') * effProductionVol
        totalMaterialCosts = np.sum([MGSiCost, HClCost, H2Cost, wasteCost]) / (1 - cumRejectionRate) / (annualProdVol * 1000)
        
        throughput = (annualProdVol * 1000) / (days * hrs)
        
        adjEffProdVol = effProductionVol * (1 - cumRejectionRate)
        runtimeOneStation = runtime(adjEffProdVol, throughput, avgDowntime, hrs, days)
        numParallelStations = parallelStationCalc(runtimeOneStation, dedicatedEquip)
        
        capitalInvestment = dfSelect(TCSProcessInputs, operation, 'Equipment Cost ($/station)') * capexFactor * (1 - equipDiscount)
        
        prodToolLife = toolLifeCalc(numParallelStations, toolingLife, effProductionVol, plantLife)
        toolSetPerStation = np.ceil(plantLife / prodToolLife)
        
        operatingPowerConsumption   = dfSelect(TCSProcessInputs, operation, 'Power (kW)') * elecFactor
        heatNatGas                  = dfSelect(TCSProcessInputs, operation, 'Heat Natural Gas (m3/kg Poly Si)') * throughput
        adjUtilities = (operatingPowerConsumption * elecPrice + heatNatGas * natGasPrice) / elecPrice       # adding in Nat Gas and adjusting for use in financial calculation function
        
        unskilledDirectLaborers = unskilledDirectLaborers * annualProdVol / 3000
        skilledDirectLaborers = skilledDirectLaborers * annualProdVol / 3000
        
        floorSQM                    = dfSelect(TCSProcessInputs, operation, 'Floorspace (m2/station)')
        buildingCostperStation = buildingCosts(floorSQM, clean10KSQM, clean1KSQM, clean100SQM, buildingCostSQF, CR10KCost, CR1KCost, CR100Cost)
        
        
        # financial calculations
        
        costSummary = financialCalculations(capitalInvestment, auxEquipInvest, installFactor, runtimeOneStation, toolinglInvestment, toolSetPerStation, buildingCostperStation, numParallelStations, 
                                            totalMaterialCosts, unskilledDirectLaborers, skilledDirectLaborers, throughput, avgDowntime, cumRejectionRate, adjUtilities, equipMaintCost, scenarioInputs, regionalInputs)
        
        
    return costSummary




# In[5]:



def inputObjects(currentInputs):
    return {
        "Harvest Chunk"     : currentInputs.harvestChunkInputs    ,
        "Siemens CVD"       : currentInputs.siemensCVDInputs      ,
        "Etch Filaments"    : currentInputs.etchFilamentsInputs   ,
        "Machine Filaments" : currentInputs.machineFilamentsInputs,
        "Saw Ingots"        : currentInputs.sawIngotsInputs       ,
        "Crop Ingots"       : currentInputs.cropIngotsInputs      ,
        "Anneal Ingots"     : currentInputs.annealIngotsInputs    ,
        "Ingot Growth"      : currentInputs.ingotGrowthInputs     ,
        "TCS"               : currentInputs.TCSInputs             ,
    }


# In[8]:


def inputToFrame(inputs, label):
    result = reduce(
        lambda x, y: x.join(y),
        [
            pd.DataFrame(dict(((section, k), [v]) for k, v in frame["Value"].items()))
            for section, frame in inputObjects(inputs).items()
        ]
    )
    result.index = pd.Index([label], name="Label")
    return result


# In[9]:


def frameToInputs(row, defaultInputs):
    target = inputObjects(deepcopy(defaultInputs))
    for section, column in row.index:
        if section == "Factor" or section == "Factors":
            continue
        target[section]["Value"][column] = row[(section, column)]
    return CurrentInputs(
        harvestChunkInputs     = target["Harvest Chunk"     ],
        siemensCVDInputs       = target["Siemens CVD"       ],
        etchFilamentsInputs    = target["Etch Filaments"    ],
        machineFilamentsInputs = target["Machine Filaments" ],
        sawIngotsInputs        = target["Saw Ingots"        ],
        cropIngotsInputs       = target["Crop Ingots"       ],
        annealIngotsInputs     = target["Anneal Ingots"     ],
        ingotGrowthInputs      = target["Ingot Growth"      ],
        TCSInputs              = target["TCS"               ],
    )


# In[10]:


def runSome(inputFrame, scenarioInputs, regionalInputs, defaultInputs):

    region             = scenarioInputs.region
    annualProdVol      = scenarioInputs.annualProdVol
    plantLife          = scenarioInputs.plantLife
    dedicatedEquip     = scenarioInputs.dedicatedEquip
    harvestChunkInUse  = scenarioInputs.harvestChunkInUse
    siemensCVDInUse    = scenarioInputs.siemensCVDInUse
    etchFilamentsInUse = scenarioInputs.etchFilamentsInUse
    machineFilInUse    = scenarioInputs.machineFilInUse
    sawIngotInUse      = scenarioInputs.sawIngotInUse
    cropIngotInUse     = scenarioInputs.cropIngotInUse
    annealIngotInUse   = scenarioInputs.annealIngotInUse
    growIngotInUse     = scenarioInputs.growIngotInUse
    TCSInUse           = scenarioInputs.TCSInUse
    TCSProcess         = scenarioInputs.TCSProcess
    TCSProcessInputs   = scenarioInputs.TCSProcessInputs

    someResults = pd.DataFrame()

    for label in inputFrame.index:

        row = inputFrame.loc[label]
        currentInputs = frameToInputs(row, defaultInputs)

        harvestFinancials, harvestRejectRate                                                                  = harvestChunk(harvestChunkInUse, currentInputs, scenarioInputs, regionalInputs)
        siemensCVDFinancials, CVDthroughput, siemensCVDRejRate, totalSiPerRod, usableSiPerRod, siemensEffProd = siemensCVD(siemensCVDInUse, harvestRejectRate, currentInputs, scenarioInputs, regionalInputs)
        etchFilamentsFinancial, etchRejectionRate, HPProduction                                               = etchFilaments(etchFilamentsInUse, siemensCVDRejRate, usableSiPerRod, siemensEffProd, currentInputs, scenarioInputs, regionalInputs)
        machineFinancials, machineRejectRate                                                                  = machineFilaments(machineFilInUse, etchRejectionRate, totalSiPerRod, currentInputs, scenarioInputs, regionalInputs)
        sawFinancials, sawRejectRate                                                                          = sawIngots(sawIngotInUse, machineRejectRate, usableSiPerRod, totalSiPerRod, currentInputs, scenarioInputs, regionalInputs)
        cropFinancials, cropRejectRate                                                                        = cropIngots(cropIngotInUse, sawRejectRate, totalSiPerRod, currentInputs, scenarioInputs, regionalInputs)
        annealFinacials, annealRejectRate                                                                     = annealIngots(annealIngotInUse, cropRejectRate, totalSiPerRod, currentInputs, scenarioInputs, regionalInputs)
        growthFinancials, growthRejRate                                                                       = ingnotGrowth(growIngotInUse, annealRejectRate, usableSiPerRod, currentInputs, scenarioInputs, regionalInputs)
        TCSFinancials                                                                                         = TCS(TCSInUse, TCSProcess, siemensCVDRejRate, HPProduction, siemensEffProd, currentInputs, scenarioInputs, regionalInputs)

        steps = [harvestFinancials, siemensCVDFinancials, etchFilamentsFinancial, machineFinancials, sawFinancials, cropFinancials, annealFinacials, growthFinancials, TCSFinancials]
        result = financialSummary(steps)
        
        result = result[["$/kg Poly Si Chunk"]].transpose()
        result.index = [row.name]
        result.index.name = "Label"
        someResults = someResults.append(result)

    return someResults


def runModel(inputFrame, scenarioInputs, regionalInputs, defaultInputs):

    results = pd.DataFrame()

    nbatch = cpu_count()
    with ft.ProcessPoolExecutor(max_workers=nbatch) as executor:
        for result in executor.map(
                runSome,
                map(lambda ix: inputFrame.loc[ix], np.array_split(inputFrame.index, nbatch)),
                repeat(scenarioInputs),
                repeat(regionalInputs),
                repeat(defaultInputs)):
            results = results.append(result)

    results.columns = pd.MultiIndex.from_tuples([("Results", column) for column in results.columns])
    return results
