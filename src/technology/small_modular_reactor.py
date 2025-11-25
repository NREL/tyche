"""
Small modular reactor technology model file

This file acts as a bridge to the ACCERT model, included in this file as additional functions.

# Derived from The Algorithm for the Capital Cost Estimation of Reactor Technologies (ACCERT)
# See original repo at: https://github.com/accert-dev/ACCERT/
# Original code is Copyright © 2023 UChicago Argonne, LLC

# Code adaptation: Rebecca Hanes, 2025, NREL
"""
import copy
import numpy as np

import pandas as pd

# Original ACCERT location: Cost_Reduction/src.py
# A function to update the high level costs in the database when changing the low level costs
def update_high_level_costs(db, reactor_power):

    
    db_updated = db.copy()
    # update account 21 : material, labor, factory
    db_updated['fact_equip_cost'][21] = db['fact_equip_cost'][212] + db['fact_equip_cost'][213] + db['fact_equip_cost']['211 plus 214 to 219']

    db_updated['site_matrl_cost'][21] = db['site_matrl_cost'][212] + db['site_matrl_cost'][213] + db['site_matrl_cost']['211 plus 214 to 219']

    db_updated['site_labor_cost'][21] = db['site_labor_cost'][212] + db['site_labor_cost'][213] + db['site_labor_cost']['211 plus 214 to 219']

    db_updated['site_labor_hrs'][21] = db['site_labor_hrs'][212] + db['site_labor_hrs'][213] + db['site_labor_hrs']['211 plus 214 to 219']
    
    # update account 23 : material, labor, factory
    db_updated['fact_equip_cost'][23] = db['fact_equip_cost'][232.1] + db['fact_equip_cost'][233]

    db_updated['site_matrl_cost'][23] = db['site_matrl_cost'][232.1] + db['site_matrl_cost'][233]

    db_updated['site_labor_cost'][23] = db['site_labor_cost'][232.1] + db['site_labor_cost'][233]

    db_updated['site_labor_hrs'][23] = db['site_labor_hrs'][232.1] + db['site_labor_hrs'][233]

    # update total costs for accounts 21 : 26
    # total = labor + factory + material
    for x in [21, 212, 213, '211 plus 214 to 219', 22, 23, 232.1, 233, 24, 26]:
        db_updated['total_cost'][x] = db_updated['fact_equip_cost'][x] + db_updated['site_labor_cost'][x] + db_updated['site_matrl_cost'][x]
    
    #update subtotals by account category
    db_updated['total_cost']['10s - Subtotal (USD)'] = db_updated['total_cost'][11] + db_updated['total_cost'][12] + db_updated['total_cost'][13] + db_updated['total_cost'][14] + db_updated['total_cost'][15] + db_updated['total_cost'][16] + db_updated['total_cost'][18]
    db_updated['total_cost']['20s - Subtotal (USD)'] = db_updated['total_cost'][21] + db_updated['total_cost'][22] + db_updated['total_cost'][23] + db_updated['total_cost'][24] + db_updated['total_cost'][25] + db_updated['total_cost'][26] + db_updated['total_cost'][28]
    db_updated['total_cost']['30s - Subtotal (USD)'] = db_updated['total_cost'][31] + db_updated['total_cost'][32] + db_updated['total_cost'][33] + db_updated['total_cost'][34] + db_updated['total_cost'][35]
    db_updated['total_cost']['50s - Subtotal (USD)'] = db_updated['total_cost'][51] + db_updated['total_cost'][52] + db_updated['total_cost'][54]
    db_updated['total_cost']['60s - Subtotal (USD)'] = db_updated['total_cost'][62]

    # update per-kWe-costs by account category
    db_updated['total_cost']['10s - $/kWe'] = db_updated['total_cost']['10s - Subtotal (USD)'] / reactor_power
    db_updated['total_cost']['20s - $/kWe'] = db_updated['total_cost']['20s - Subtotal (USD)'] / reactor_power
    db_updated['total_cost']['30s - $/kWe'] = db_updated['total_cost']['30s - Subtotal (USD)'] / reactor_power
    db_updated['total_cost']['50s - $/kWe'] = db_updated['total_cost']['50s - Subtotal (USD)'] / reactor_power
    db_updated['total_cost']['60s - $/kWe'] = db_updated['total_cost']['60s - Subtotal (USD)'] / reactor_power

    #(db.loc[db['Title'] == '10s - Subtotal', 'Total Cost (USD)']) =\
    #    db.loc[db['Account'].isin([11, 12, 13, 14, 15, 16, 18]), 'Total Cost (USD)'].sum()

    # update total costs for accounts 20
    #(db.loc[db['Title'] == '20s - Subtotal', 'Total Cost (USD)']) =\
    #    db.loc[db['Account'].isin([21, 22, 23, 24, 25, 26, 28]), 'Total Cost (USD)'].sum()

    # update total costs for accounts 30
    #(db.loc[db['Title'] == '30s - Subtotal', 'Total Cost (USD)']) =\
    #    db.loc[db['Account'].isin([31, 32, 33, 34, 35]), 'Total Cost (USD)'].sum()


    # update total costs for accounts 50
    #(db.loc[db['Title'] == '50s - Subtotal', 'Total Cost (USD)']) =\
    #    db.loc[db['Account'].isin([51, 52, 54]), 'Total Cost (USD)'].sum()

    # update total costs for accounts 60
    #(db.loc[db['Title'] == '60s - Subtotal', 'Total Cost (USD)']) =\
    #    db.loc[db['Account'].isin([ 62]), 'Total Cost (USD)'].sum()

    # update costs per kw
    #(db.loc[db['Title'] == '10s - $/kWe', 'Total Cost (USD)']) = (db.loc[db['Title'] == '10s - Subtotal', 'Total Cost (USD)']).values/reactor_power 
    #(db.loc[db['Title'] == '20s - $/kWe', 'Total Cost (USD)']) = (db.loc[db['Title'] == '20s - Subtotal', 'Total Cost (USD)']).values/reactor_power 
    #(db.loc[db['Title'] == '30s - $/kWe', 'Total Cost (USD)']) = (db.loc[db['Title'] == '30s - Subtotal', 'Total Cost (USD)']).values/reactor_power 
    #(db.loc[db['Title'] == '40s - $/kWe', 'Total Cost (USD)']) = (db.loc[db['Title'] == '40s - Subtotal', 'Total Cost (USD)']).values/reactor_power 
    #(db.loc[db['Title'] == '50s - $/kWe', 'Total Cost (USD)']) = (db.loc[db['Title'] == '50s - Subtotal', 'Total Cost (USD)']).values/reactor_power 
    #(db.loc[db['Title'] == '60s - $/kWe', 'Total Cost (USD)']) = (db.loc[db['Title'] == '60s - Subtotal', 'Total Cost (USD)']).values/reactor_power 

    # update final results
    db_updated['total_cost']['Total Direct Capital Cost (Accounts 10 to 20) (USD)'] = db_updated['total_cost']['10s - Subtotal (USD)'] + db_updated['total_cost']['20s - Subtotal (USD)']
    #(db.loc[db['Title'] == 'Total Direct Capital Cost (Accounts 10 to 20)', 'Total Cost (USD)']) =\
    #    (db.loc[db['Title'] == '10s - Subtotal', 'Total Cost (USD)']).values + (db.loc[db['Title'] == '20s - Subtotal', 'Total Cost (USD)']).values

    db_updated['total_cost']['Base Construction Cost (Accounts 10 to 30) (USD)'] = db_updated['total_cost']['Total Direct Capital Cost (Accounts 10 to 20) (USD)'] + db_updated['total_cost']['30s - Subtotal (USD)']
    #(db.loc[db['Title'] == 'Base Construction Cost (Accounts 10 to 30)', 'Total Cost (USD)']) =\
    #   (db.loc[db['Title'] == 'Total Direct Capital Cost (Accounts 10 to 20)', 'Total Cost (USD)']).values +\
    #    (db.loc[db['Title'] == '30s - Subtotal', 'Total Cost (USD)']).values

    db_updated['total_cost']['Total Overnight Cost (Accounts 10 to 50) (USD)'] = db_updated['total_cost']['Base Construction Cost (Accounts 10 to 30) (USD)'] + db_updated['total_cost']['50s - Subtotal (USD)']
    #(db.loc[db['Title'] == 'Total Overnight Cost (Accounts 10 to 50)', 'Total Cost (USD)']) =\
    #    (db.loc[db['Title'] == 'Base Construction Cost (Accounts 10 to 30)', 'Total Cost (USD)']).values +\
    #(db.loc[db['Title'] == '50s - Subtotal', 'Total Cost (USD)']).values

    db_updated['total_cost']['Total Capital Investment Cost (All Accounts) (USD)'] = db_updated['total_cost']['Total Overnight Cost (Accounts 10 to 50) (USD)'] + db_updated['total_cost']['60s - Subtotal (USD)']
    #(db.loc[db['Title'] == 'Total Capital Investment Cost (All Accounts)', 'Total Cost (USD)']) =\
    #   (db.loc[db['Title'] == 'Total Overnight Cost (Accounts 10 to 50)', 'Total Cost (USD)']).values +\
    #    (db.loc[db['Title'] == '60s - Subtotal', 'Total Cost (USD)']).values

    # update final results per kw
    db_updated['total_cost']['(Accounts 10 to 20) US$/kWe'] = db_updated['total_cost']['Total Direct Capital Cost (Accounts 10 to 20) (USD)'] / reactor_power
    #(db.loc[db['Title'] == '(Accounts 10 to 20) US$/kWe', 'Total Cost (USD)']) =\
    #    (db.loc[db['Title'] == 'Total Direct Capital Cost (Accounts 10 to 20)', 'Total Cost (USD)']).values/reactor_power 

    db_updated['total_cost']['(Accounts 10 to 30) US$/kWe'] = db_updated['total_cost']['Base Construction Cost (Accounts 10 to 30) (USD)'] / reactor_power
    #(db.loc[db['Title'] == '(Accounts 10 to 30) US$/kWe', 'Total Cost (USD)']) =\
    #    (db.loc[db['Title'] == 'Base Construction Cost (Accounts 10 to 30)', 'Total Cost (USD)']).values/reactor_power 

    db_updated['total_cost']['(Accounts 10 to 50) US$/kWe'] = db_updated['total_cost']['Total Overnight Cost (Accounts 10 to 50) (USD)'] / reactor_power
    #(db.loc[db['Title'] == '(Accounts 10 to 50) US$/kWe', 'Total Cost (USD)']) =\
    #    (db.loc[db['Title'] == 'Total Overnight Cost (Accounts 10 to 50)', 'Total Cost (USD)']).values/reactor_power 

    db_updated['total_cost']['(Accounts 10 to 60) US$/kWe'] = db_updated['total_cost']['Total Capital Investment Cost (All Accounts) (USD)'] / reactor_power
    #(db.loc[db['Title'] == '(Accounts 10 to 60) US$/kWe', 'Total Cost (USD)']) =\
    #    (db.loc[db['Title'] == 'Total Capital Investment Cost (All Accounts)', 'Total Cost (USD)']).values/reactor_power

    return db_updated




# Original ACCERT location: Cost_Reduction/src.py
# A function to calculate the cost reduction factor due to the ITC subsidies
def ITC_reduction_factor(itc_level):
    itc_values = [0, 0.06, 0.3, 0.4, 0.5]
    ITC_reduction_factor = [1, 0.95,	0.73,	0.63,	0.53 ]
    return np.interp(itc_level, itc_values, ITC_reduction_factor)


def reactor_data_read(rtype = 'Concept B',
                      datafilepath = 'conceptb-inputs.xlsx'):
    """
    Read in baseline cost data for a 300 MWe small modular reactor using
    sodium fast reactor technology.

    Parameters
    ----------
    rtype : string, Default = 'Concept B'
    Reactor type. Calculations are only implemented for Concept B types.

    datafilepath : string, Default = 'small-modular-reactor/conceptb-inputs.xlsx'
    Relative location of inputs for Concept B reactor type.

    Returns
    -------
    tuple(pd.DataFrame, float, pd.DataFrame)
    Tuple of read-in reactor data, the hard coded reactor power, and the spending curve data.
    """
    if rtype != 'Concept B':
        raise NotImplementedError

    rdata = pd.read_excel(datafilepath,
                          sheet_name = 'Costs')
    
    total_cost = {}
    for (acct, tot_cost) in zip(rdata['Account'], rdata['Total Cost (USD)']):
        # The equality requirements filter out nans
        if acct == acct and tot_cost == tot_cost:
            total_cost[acct] = tot_cost

    fact_equip_cost = {}
    for (acct, fact_cost) in zip(rdata['Account'], rdata['Factory Equipment Cost']):
        if acct == acct and fact_cost == fact_cost:
            fact_equip_cost[acct] = fact_cost

    site_labor_hrs = {}
    for (acct, site_lab) in zip(rdata['Account'], rdata['Site Labor Hours']):
        if acct == acct and site_lab == site_lab:
            site_labor_hrs[acct] = site_lab

    site_labor_cost = {}
    for (acct, site_cost) in zip(rdata['Account'], rdata['Site Labor Cost']):
        if acct == acct and site_cost == site_cost:
            site_labor_cost[acct] = site_cost

    site_matrl_cost = {}
    for (acct, site_mat) in zip(rdata['Account'], rdata['Site Material Cost']):
        if acct == acct and site_mat == site_mat:
            site_matrl_cost[acct] = site_mat
    
    rdata_dicts = {'total_cost': total_cost,
                   'fact_equip_cost' : fact_equip_cost,
                   'site_labor_hrs' : site_labor_hrs,
                   'site_labor_cost' : site_labor_cost,
                   'site_matrl_cost' : site_matrl_cost}

    # kWe
    rpower = 310.8 * 1000
    sp = pd.read_excel(datafilepath,
                        sheet_name='Ref Spending Curve',
                        usecols='A : D')

    return (rdata_dicts,
            rpower,
            sp)


def add_factory_cost(rdata, 
                      rpower,
                      f_22, # parameter
                      f_2321, # parameter
                      num_orders): # parameter
    """
    Adding the factory cost to accounts 22 and 232.1

    Parameters
    ----------
    rdata: pd.DataFrame

    rpower: float

    f_22: float

    f_2321: float

    Returns
    -------
    pd.DataFrame
    Structure identical to rdata with updated values
    """
    db = rdata.copy()
    
    # Recalculate factory equipment costs and update dictionary
    db['fact_equip_cost'].update(
        {22: f_22 / num_orders,
         232.1: f_2321 / num_orders}
         )

    #rdata_updated = update_high_level_costs(db, rpower)

    return db


def add_land_cost(rdata, rpower, land_cost_per_acre):
    """
    Add the land cost & Taxes

    Parameters
    ----------
    rdata

    rpower

    land_cost_per_acre

    Returns
    -------
    pd.DataFrame
    Structure identical to rdata with updated values
    """
    db = rdata.copy()

    db['total_cost'].update({
        11: land_cost_per_acre / 22000 * rdata['total_cost'][11],
        12: land_cost_per_acre / 22000 * rdata['total_cost'][12],
        51: land_cost_per_acre / 22000 * rdata['total_cost'][51]
    })
    #rdata_updated = update_high_level_costs(db, rpower)

    return db


def add_BOP_RP_grades(rdata,
                      rpower,
                      RB_grade_0,
                      BOP_grade_0):
    """
    Adjust costs based on Whether the Reactor Building and BOP are nuclear grade equipment

    Parameters
    ----------
    rdata

    rpower

    RB_grade_0

    BOP_grade_0

    Returns
    -------
    pd.DataFrame
    Structure identical to rdata with updated values
    """
    RB_mult = RB_grade_0
    RB_mult[RB_mult == 0] = 0.6
    BOP_mult = BOP_grade_0
    BOP_mult[BOP_mult == 0] = 0.6

    db = rdata.copy()

    db['site_matrl_cost'].update({
        212: RB_mult * rdata['site_matrl_cost'][212]
    })
    db['site_labor_cost'].update({
        212: RB_mult * rdata['site_labor_cost'][212]
    })
    db['site_labor_hrs'].update({
        212: RB_mult * rdata['site_labor_hrs'][212]
    })
    db['fact_equip_cost'].update({
        212: RB_mult * rdata['fact_equip_cost'][212]
    })

    db['site_matrl_cost'].update({
        213: BOP_mult * rdata['site_matrl_cost'][213],
        232.1: BOP_mult * rdata['site_matrl_cost'][232.1],
    })
    db['site_labor_cost'].update({
        213: BOP_mult * rdata['site_labor_cost'][213],
        232.1: BOP_mult * rdata['site_labor_cost'][232.1],
    })
    db['site_labor_hrs'].update({
        213: BOP_mult * rdata['site_labor_hrs'][213],
        232.1: BOP_mult * rdata['site_labor_hrs'][232.1],
    })
    db['fact_equip_cost'].update({
        213: BOP_mult * rdata['fact_equip_cost'][213],
        232.1: BOP_mult * rdata['fact_equip_cost'][232.1],
    })

    #rdata_updated = update_high_level_costs(db, rpower)

    return db



def add_bulk_ordering(rdata,
                      rpower,
                      num_orders,
                      f_22,
                      f_2321):
    """
    Accounts for Bulk order of reactors

    Parameters
    ----------
    rdata

    rpower

    num_orders

    f_22

    f_2321

    Returns
    -------
    pd.DataFrame
    Structure identical to rdata with updated values
    """
    db = rdata.copy()

    # Hard coded learning rates
    lr22 = 0.180234165929142
    lr2321 = 0.260746237204082
    
    """
    reduction_factor_22 = 0
    reduction_factor_2321 = 0

    for ith_unit in range(1, num_orders + 1):
        reduction_factor_22 = reduction_factor_22 + (1 - lr22) ** np.log2(ith_unit) / num_orders
        reduction_factor_2321 = reduction_factor_2321 + (1 - lr2321) ** np.log2(ith_unit) / num_orders
    """
    
    
    # Need an array of the same shape as num_orders
    reduction_factor_22 = np.zeros(shape = num_orders.shape)
    reduction_factor_2321 = np.zeros(shape = num_orders.shape)
    
    for i in range(num_orders.shape[0]):
        for j in range(num_orders.shape[1]):
            reduction_factor_22[i,j] = sum([(1 - lr22) ** np.log2(ith_unit) / num_orders[i,j] for ith_unit in range(1, int(num_orders[i,j])+1)])
            reduction_factor_2321[i,j] = sum([(1 - lr2321) ** np.log2(ith_unit) / num_orders[i,j] for ith_unit in range(1, int(num_orders[i,j])+1)])

    db['fact_equip_cost'][22] = reduction_factor_22 * (rdata['fact_equip_cost'][22] - f_22 / num_orders) + f_22 / num_orders

    db['fact_equip_cost'][232.1] = reduction_factor_2321 * (rdata['fact_equip_cost'][232.1] - f_2321 / num_orders) + f_2321 / num_orders

    #rdata_updated = update_high_level_costs(db, rpower)

    return db


def add_reworking_productivity(rdata,
                               rpower,
                               reactor_type,
                               n_th,
                               design_completion_0,
                               ae_exp_0,
                               N_AE,
                               ce_exp_0,
                               N_cons):
    """
    Accounts for reworking and labor productivity cost impacts

    Parameters
    ----------
    rdata

    rpower

    reactor_type

    n_th

    design_completion_0

    ae_exp_0

    N_AE

    ce_exp_0

    N_cons

    Returns
    -------
    pd.DataFrame
    Structure identical to rdata with updated values
    """
    if reactor_type != 'Concept B':
        raise NotImplementedError
    """""
    if n_th == 1:
        ae_exp = ae_exp_0
        ce_exp = ce_exp_0
    elif n_th > 1:
        ae_exp = min(ae_exp_0 + 2 / N_AE * (n_th - 1), 2)
        ce_exp = min(ce_exp_0 + 2 / N_cons * (n_th - 1), 2)
    """

    design_completion = design_completion_0
    design_completion[n_th > 1] = 1.0

    ae_exp = np.zeros(shape = ae_exp_0.shape)
    ce_exp = np.zeros(shape = ce_exp_0.shape)

    for i in range(ae_exp_0.shape[0]):
        for j in range(ae_exp_0.shape[1]):
            if n_th[i,j] > 1:
                ae_exp[i,j] = min(ae_exp_0[i,j] + 2 / N_AE[i,j] * (n_th[i,j] - 1), 2)
                ce_exp[i,j] = min(ce_exp_0[i,j] + 2 / N_cons[i,j] * (n_th[i,j] - 1), 2)
            else:
                ae_exp[i,j] = ae_exp_0[i,j]
                ce_exp[i,j] = ce_exp_0[i,j]
    
    
    productivity = 0.145 * ce_exp + 0.71

    reworking_factor = (-0.9 * design_completion + 1.9) * (-0.15 * ae_exp + 1.3) * (-0.15 * ce_exp + 1.3)

    db = rdata.copy()

    for x in [212, 213, '211 plus 214 to 219', 22, 232.1, 233, 24, 26]:
        db['site_matrl_cost'].update({
            x: reworking_factor * rdata['site_matrl_cost'][x]
        })
        db['site_labor_cost'].update({
            x: reworking_factor / productivity * rdata['site_labor_cost'][x]
        })
        db['site_labor_hrs'].update({
            x: reworking_factor / productivity * rdata['site_labor_hrs'][x]
        })
        db['fact_equip_cost'].update({
            x: reworking_factor * rdata['fact_equip_cost'][x]
        })

    #rdata_updated = update_high_level_costs(db, rpower)

    return db


def update_direct_cost(reactor_type,
                        n_th,
                        f_22,
                        f_2321,
                        land_cost_per_acre_0,
                        RB_grade_0,
                        BOP_grade_0,
                        num_orders,
                        design_completion_0,
                        ae_exp_0,
                        N_AE,
                        ce_exp_0,
                        N_cons):
    """

    Parameters
    ----------
    reactor_type

    n_th

    f_22

    f_2321

    land_cost_per_acre_0

    RB_grade_0

    BOP_grade_0

    num_orders

    design_completion_0

    ae_exp_0

    N_AE

    ce_exp_0

    N_cons

    Returns
    -------
    pd.DataFrame
    Structure identical to rdata with updated values
    """
    if reactor_type != 'Concept B':
        raise NotImplementedError

    rdata = reactor_data_read(reactor_type)[0]
    rpower = reactor_data_read(reactor_type)[1]

    rdata_factory = add_factory_cost(rdata, 
                                      rpower,
                                      f_22,
                                      f_2321,
                                      num_orders)

    rdata_factory_land_taxes = add_land_cost(rdata_factory,
                                              rpower,
                                              land_cost_per_acre_0)

    rdata_factory_land_taxes_BOP_RP_grades = add_BOP_RP_grades(rdata_factory_land_taxes,
                                                                rpower,
                                                                RB_grade_0,
                                                                BOP_grade_0)

    rdata_factory_land_taxes_BOP_RP_grades_bulkOrder = \
        add_bulk_ordering(rdata_factory_land_taxes_BOP_RP_grades,
                          rpower,
                          num_orders,
                          f_22,
                          f_2321)
    
    rdata_factory_land_taxes_BOP_RP_grades_bulkOrder_rework_productivity = \
        add_reworking_productivity(rdata_factory_land_taxes_BOP_RP_grades_bulkOrder,
                                    rpower,
                                    reactor_type,
                                    n_th,
                                    design_completion_0,
                                    ae_exp_0,
                                    N_AE,
                                    ce_exp_0,
                                    N_cons)
    
    return update_high_level_costs(rdata_factory_land_taxes_BOP_RP_grades_bulkOrder_rework_productivity, rpower)





def update_cons_dur(rdata,
                    rdata_updated,
                    mod_0,
                    reactor_type = 'Concept B'):
    """
    Update construction duration from labor hours

    Parameters
    ----------
    rdata

    rdata_updated

    mod_0

    Returns
    -------
    float: Construction duration
    """
    if reactor_type != 'Concept B':
        raise NotImplementedError
    
    sum_old_lab_hrs = rdata['site_labor_hrs'][21] + rdata['site_labor_hrs'][22] + rdata['site_labor_hrs'][23] + rdata['site_labor_hrs'][24] + rdata['site_labor_hrs'][26]
    #rdata.loc[rdata.Account == 21, 'Site Labor Hours'].values +\
    #rdata.loc[rdata.Account == 22, 'Site Labor Hours'].values +\
    #rdata.loc[rdata.Account == 23, 'Site Labor Hours'].values +\
    #rdata.loc[rdata.Account == 24, 'Site Labor Hours'].values +\
    #rdata.loc[rdata.Account == 26, 'Site Labor Hours'].values

    sum_new_lab_hrs = rdata_updated['site_labor_hrs'][21] + rdata_updated['site_labor_hrs'][22] + rdata_updated['site_labor_hrs'][23] + rdata_updated['site_labor_hrs'][24] + rdata_updated['site_labor_hrs'][26]
    #rdata_updated.loc[rdata_updated.Account == 21, 'Site Labor Hours'].values +\
    #rdata_updated.loc[rdata_updated.Account == 22, 'Site Labor Hours'].values +\
    #rdata_updated.loc[rdata_updated.Account == 23, 'Site Labor Hours'].values +\
    #rdata_updated.loc[rdata_updated.Account == 24, 'Site Labor Hours'].values +\
    #rdata_updated.loc[rdata_updated.Account == 26, 'Site Labor Hours'].values
    
    labor_hour_ratio = sum_new_lab_hrs / sum_old_lab_hrs
    
    #if mod_0 == 0: # stick built
    #    mod_factor = 0.8
    #elif mod_0 == 1: # modularized
    #    mod_factor = 1

    mod_factor = mod_0
    mod_factor[mod_0 == 0] = 0.8

    baseline_construction_duration = 64 / mod_factor

    return baseline_construction_duration * (0.3 * labor_hour_ratio + 0.7)



def learning_effect(rdata,
                    rpower,
                    n_th,
                    standardization_0):
    """
    Learning by doing effect on the cost

    Parameters
    ----------
    rdata

    rpower

    n_th

    standardization_0

    Returns
    -------
    pd.DataFrame
    Structure identical to rdata with updated values
    """
    standardization = np.zeros(shape = standardization_0.shape)
    for i in range(standardization_0.shape[0]):
        for j in range(standardization_0.shape[1]):
            if n_th[i,j] > 1:
                standardization[i,j] = standardization_0[i,j]
            else:
                standardization[i,j] = 0.7

    accts = [212, 213, '211 plus 214 to 219', 22, 232.1, 233, 24, 26]

    material_learning_factor = dict(
        zip(
            accts,
            np.array(
                [0.099588665391,
                 0.099588665391,
                 0.099588665391,
                 0.080817992281,
                 0.0,
                 0.099588665391,
                 0.099588665391,
                 0.099588665391]
            )
        )
    )

    labor_learning_factor = dict(
        zip(
            accts,
            np.array(
                [0.180678729399,
                 0.180678729399,
                 0.180678729399,
                 0.146555539499,
                 0.137148574884,
                 0.180678729399,
                 0.180678729399,
                 0.180678729399]
            )
        )
    )

    rdata_updated = copy.deepcopy(rdata)
    
    for x in accts:
        rdata_updated['site_matrl_cost'][x] = rdata['site_matrl_cost'][x] * (1 - material_learning_factor[x] * standardization / 0.7) ** np.log2(n_th)
        rdata_updated['site_labor_hrs'][x] = rdata['site_labor_hrs'][x] * (1 - labor_learning_factor[x] * standardization / 0.7) ** np.log2(n_th)
        rdata_updated['site_labor_cost'][x] = rdata['site_labor_cost'][x] * (1 - labor_learning_factor[x] * standardization / 0.7) ** np.log2(n_th)
    
    return rdata_updated


def act_cons_duration_plus_delay(reactor_type,
                                 n_th,
                                 Design_Maturity_0,
                                 proc_exp_0,
                                 N_proc,
                                 cons_duration_no_delay):
    """
    Supply chain delays

    Parameters
    ----------
    reactor_type

    n_th

    Design_Maturity_0

    proc_exp_0

    N_proc

    cons_duration_no_delay

    Returns
    -------
    float: Construction duration
    """
    if reactor_type != 'Concept B':
        raise NotImplementedError

    task_length_multiplier = 1
    ref_construction_duration = 64
    
    B_21 = 42.1 * task_length_multiplier
    B_22 = 60.2 * task_length_multiplier
    B_23 = 14.8 * task_length_multiplier
    B_24 = 3.6 * task_length_multiplier
    B_25 = 10.1 * task_length_multiplier
    B_26 = 43.9 * task_length_multiplier

    #if n_th == 1:
    #    Design_Maturity = Design_Maturity_0
    #    proc_exp = proc_exp_0
    #elif n_th > 1:
    #    Design_Maturity = 2
    #    proc_exp = min(proc_exp_0 + 2 / N_proc * (n_th - 1), 2)

    proc_exp = np.zeros(shape = proc_exp_0.shape)
    Design_Maturity = np.zeros(shape = proc_exp_0.shape)
    for i in range(proc_exp_0.shape[0]):
        for j in range(proc_exp_0.shape[1]):
            if n_th[i,j] > 1:
                proc_exp[i,j] = min(proc_exp_0[i,j] + 2 / N_proc[i,j] * (n_th[i,j] - 1), 2)
                Design_Maturity[i,j] = 2
            else:
                proc_exp[i,j] = proc_exp_0[i,j]
                Design_Maturity[i,j] = Design_Maturity_0[i,j]
    

    D_21 = -6 * Design_Maturity - 3 * proc_exp + 18
    D_22 = -6 * Design_Maturity - 3 * proc_exp + 18
    D_23 = -6 * Design_Maturity - 3 * proc_exp + 18
    D_24 = -6 * Design_Maturity - 3 * proc_exp + 18
    D_25 = -6 * Design_Maturity - 3 * proc_exp + 18
    D_26 = -6 * Design_Maturity - 3 * proc_exp + 18
    T_21 = B_21 + D_21
    T_22 = 0.09 * (B_21 + D_21) + B_22 + D_22
    T_23 = 0.24 * (B_21 + D_21) + B_23 + D_23
    T_24 = 0.24 * (B_21 + D_21) + 0.34 * (B_23 + D_23) + B_24 + D_24
    T_25 = 0.18 * (B_21 + D_21) + B_25 + D_25
    T_26 = 0.21 * (B_21 + D_21) + B_26 + D_26
    
    T_all = np.array([T_21, T_22, T_23, T_24, T_25, T_26])
    
    T_end = np.max(T_all, axis=0)

    T_end_increase = T_end - ref_construction_duration
    
    T_end_increase[T_end_increase < 0] = 0

    supply_chain_delay = T_end_increase

    actual_construction_duration_plus_delay = cons_duration_no_delay + supply_chain_delay
    
    return actual_construction_duration_plus_delay



def duration_learning_effect(n_th,
                              standardization_0,
                              actual_construction_duration_plus_delay):
    """
    Learning by doing effect on the construction duration

    Parameters
    ----------
    n_th

    standardization_0

    actual_construction_duration_plus_delay

    Returns
    -------
    float: construction duration    
    """
    standardization = np.zeros(shape = standardization_0.shape)
    for i in range(standardization_0.shape[0]):
        for j in range(standardization_0.shape[1]):
            if n_th[i,j] > 1:
                standardization[i,j] = standardization_0[i,j]
            else:
                standardization[i,j] = 0.7

    fitted_LR_duration = 0.15 * standardization / 0.7

    duration_multiplier = (1 - fitted_LR_duration) ** np.log2(n_th)

    return duration_multiplier * actual_construction_duration_plus_delay



def update_indirect_cost(n_th,
                         rpower,
                         standardization_0,
                         rdata,
                         final_construction_duration):
    """
    Calculate the Indirect Cost and the standardization impact

    Parameters
    ----------
    n_th

    rpower

    standardization_0

    rdata

    final_construction_duration

    Returns
    -------
    pd.DataFrame
    Structure identical to rdata with updated values
    """
    standardization = np.zeros(shape = standardization_0.shape)
    for i in range(standardization_0.shape[0]):
        for j in range(standardization_0.shape[1]):
            if n_th[i,j] > 1:
                standardization[i,j] = standardization_0[i,j]
            else:
                standardization[i,j] = 0.7
    
    factor_35 = -3.33 * standardization + 3.331

    db = copy.deepcopy(rdata)

    #for x in [31, 32, 33, 34, 35]:
    #    db.loc[db.Account == x, 'Total Cost (USD)'] = None

    sum_new_mat_cost = 0
    sum_new_lab_cost = 0
    sum_new_lab_hrs = 0
    for x in [21, 22, 23, 24, 26]:
        sum_new_mat_cost = sum_new_mat_cost + db['site_matrl_cost'][x] #db.loc[db.Account == x, 'Site Material Cost'].values
        sum_new_lab_cost = sum_new_lab_cost + db['site_labor_cost'][x] #db.loc[db.Account == x, 'Site Labor Cost'].values
        sum_new_lab_hrs = sum_new_lab_hrs + db['site_labor_hrs'][x] #db.loc[db.Account == x, 'Site Labor Hours'].values

    db['total_cost'][31] = sum_new_mat_cost * 0.785 * sum_new_lab_hrs / final_construction_duration / 160 / 1058 + sum_new_lab_cost * 0.36
    #db.loc[db.Account == 31, 'Total Cost (USD)'] = sum_new_mat_cost * 0.785 * sum_new_lab_hrs / final_construction_duration / 160 / 1058 + sum_new_lab_cost * 0.36

    db['total_cost'][32] = sum_new_lab_cost * 0.36 * 3.661 * final_construction_duration / 72
    #db.loc[db.Account == 32, 'Total Cost (USD)'] = sum_new_lab_cost * 0.36 * 3.661 * final_construction_duration / 72

    db['total_cost'][33] = 0.042 * db['total_cost'][32]
    #db.loc[db.Account == 33, 'Total Cost (USD)'] = 0.042 *\
    #    db.loc[db.Account == 32, 'Total Cost (USD)'].values[0]
    db['total_cost'][34] = 0.0035 * db['total_cost'][32]
    #db.loc[db.Account == 34, 'Total Cost (USD)'] = 0.0035 *\
    #    db.loc[db.Account == 32, 'Total Cost (USD)'].values[0]
    db['total_cost'][35] = 0.27 * factor_35 * db['total_cost'][32]
    #db.loc[db.Account == 35, 'Total Cost (USD)'] = 0.27 * factor_35 *\
    #    db.loc[db.Account == 32, 'Total Cost (USD)'].values[0]

    #rdata_updated = update_high_level_costs(db, rpower)

    return db


def calculate_base_cost(reactor_type,
                        n_th,
                        f_22,
                        f_2321,
                        land_cost_per_acre_0,
                        RB_grade_0,
                        BOP_grade_0,
                        num_orders,
                        design_completion_0,
                        ae_exp_0,
                        N_AE,
                        ce_exp_0,
                        N_cons,
                        mod_0,
                        Design_Maturity_0,
                        proc_exp_0,
                        N_proc,
                        standardization_0):
    """
    Combine the previous functions in one function

    Parameters
    ----------
    reactor_type

    n_th

    f_22

    f_2321

    land_cost_per_acre_0

    RB_grade_0

    BOP_grade_0

    num_orders

    design_completion_0

    ae_exp_0

    N_AE

    ce_exp_0

    N_cons

    mod_0

    Design_Maturity_0

    proc_exp_0

    N_proc

    standardization_0

    Returns
    -------
    tuple(pd.DataFrame, float)
    DataFrame of updated costs, final construction duration
    """
    if reactor_type != 'Concept B':
        raise NotImplementedError

    reactor_data = reactor_data_read(reactor_type)[0]
    reactor_power = reactor_data_read(reactor_type)[1]

    direct_cost_updated = update_direct_cost(reactor_type,
                                              n_th,
                                              f_22,
                                              f_2321,
                                              land_cost_per_acre_0,
                                              RB_grade_0,
                                              BOP_grade_0,
                                              num_orders,
                                              design_completion_0,
                                              ae_exp_0,
                                              N_AE,
                                              ce_exp_0,
                                              N_cons)
    
    act_con_duration = update_cons_dur(reactor_data, direct_cost_updated, mod_0)
    
    cons_duration_plus_delay = act_cons_duration_plus_delay(reactor_type,
                                                            n_th,
                                                            Design_Maturity_0,
                                                            proc_exp_0,
                                                            N_proc,
                                                            act_con_duration)

    final_con_duration = duration_learning_effect(n_th,
                                                  standardization_0,
                                                  cons_duration_plus_delay)

    direct_cost_updated_plus_learning = learning_effect(direct_cost_updated,
                                                        reactor_power,
                                                        n_th,
                                                        standardization_0)
    
    direct_cost_updated_plus_learning_with_indirect_cost = update_indirect_cost(n_th,
                                                                                reactor_power,
                                                                                standardization_0,
                                                                                direct_cost_updated_plus_learning,
                                                                                final_con_duration)
    base_cost_updated = update_high_level_costs(direct_cost_updated_plus_learning_with_indirect_cost, reactor_power)

    return (base_cost_updated, final_con_duration)




def insurance_cost_update(rdata,
                          rpower,
                          rdata_tot_base_cost):
    """
    Insurance

    Parameters
    ----------
    rdata

    rpower

    rdata_tot_base_cost

    Returns
    -------
    pd.DataFrame
    Structure identical to rdata with updated values
    """
    db = copy.deepcopy(rdata_tot_base_cost)

    db0 = update_high_level_costs(rdata, rpower)

    #db.loc[db.Account == 52, 'Total Cost (USD)'] = None

    change_in_insurance_cost = (db['total_cost']['20s - Subtotal (USD)'] + db['total_cost']['30s - Subtotal (USD)']) / (db0['total_cost']['20s - Subtotal (USD)'] + db0['total_cost']['30s - Subtotal (USD)'])
    #change_in_insurance_cost = (db.loc[db.Title == '20s - Subtotal', 'Total Cost (USD)'].values +\
    #                           db.loc[db.Title == '30s - Subtotal', 'Total Cost (USD)'].values) / \
    #(db0.loc[db0.Title == '20s - Subtotal', 'Total Cost (USD)'].values +\
    # db0.loc[db0.Title == '30s - Subtotal', 'Total Cost (USD)'].values)

    db['total_cost'].update(
        {52: change_in_insurance_cost * db['total_cost'][52]}
    )
    #db.loc[db.Account == 52, 'Total Cost (USD)'] = change_in_insurance_cost[0] *\
    #    rdata_tot_base_cost.loc[db.Account == 52, 'Total Cost (USD)']

    #rdata_updated = update_high_level_costs(db, rpower)

    return update_high_level_costs(db, rpower)



def update_interest_cost(rdata,
                          rpower,
                          final_construction_duration,
                          interest_rate,
                          startup_0,
                          n_th):
    """
    Interest

    Parameters
    ----------
    rdata,

    rpower,

    final_construction_duration,

    interest_rate,

    startup_0,

    n_th    

    Returns
    -------
    tuple(pd.DataFrame, float, float)
    Cost data frame, overnight capital cost, total capital investment
    """
    db = copy.deepcopy(rdata)
    db['total_cost'].update({62: np.zeros(final_construction_duration.shape)})

    sp = reactor_data_read()[2]

    Months = sp['Month'].tolist()
    CDFs = sp['CDF'].tolist()

    #annual_periods = np.ones(final_construction_duration.shape).tolist()

    
    for i in range(final_construction_duration.shape[0]):
        for j in range(final_construction_duration.shape[1]):

            if n_th[i,j] == 1:
                startup = startup_0[i,j]
            elif n_th[i,j] > 1:
                startup = max(7, startup_0[i,j] * (1 - 0.3) ** np.log2(n_th[i,j]))
            
            _annual_periods = np.linspace(12, 12 * int(final_construction_duration[i,j] / 12), int(final_construction_duration[i,j] / 12))

            if max(_annual_periods) < int(final_construction_duration[i,j]) - 1:
                annual_periods_1 = np.append(_annual_periods, final_construction_duration[i,j] - 1)
            else:
                annual_periods_1 = _annual_periods

            annual_cum_spend = []

            for period in annual_periods_1:
                new_period = 103 * period / int(final_construction_duration[i,j])
                annual_cum_spend.append(np.interp(new_period, Months, CDFs))

            annual_cum_spend1 = np.append(annual_cum_spend[0], np.diff(annual_cum_spend))
            
            tot_overnight_cost = rdata['total_cost']['Total Overnight Cost (Accounts 10 to 50) (USD)'][i,j]
            #tot_overnight_cost = rdata.loc[
            #    rdata.Title == 'Total Overnight Cost (Accounts 10 to 50)',
            #    'Total Cost (USD)'
            #    ].values[0]

            annual_loan_add = annual_cum_spend1 * tot_overnight_cost

            interest_exp = (1 + interest_rate[i,j]) ** ((final_construction_duration[i,j] - annual_periods_1) / 12) * annual_loan_add - annual_loan_add

            tot_int_exp_construction = sum(interest_exp)

            int_exp_startup = (tot_int_exp_construction + tot_overnight_cost) * (1 + interest_rate[i,j]) ** (startup / 12) - (tot_int_exp_construction + tot_overnight_cost)
            
            db['total_cost'][62][i,j] = int_exp_startup + tot_int_exp_construction
        
        
        #db.loc[db.Account == 62, 'Total Cost (USD)'] = None
        #db.loc[db.Account == 62, 'Total Cost (USD)'] = int_exp_startup + tot_int_exp_construction

    rdata_updated = update_high_level_costs(db, rpower)

    tot_cap_investment = rdata_updated['total_cost']['Total Capital Investment Cost (All Accounts) (USD)']
    tot_overnight_cost = rdata_updated['total_cost']['Total Overnight Cost (Accounts 10 to 50) (USD)']
    #tot_cap_investment = rdata_updated.loc[
    #    rdata_updated.Title == 'Total Capital Investment Cost (All Accounts)',
    #    'Total Cost (USD)'].values

    return (copy.deepcopy(rdata_updated),
            tot_overnight_cost,
            tot_cap_investment)




def update_itc(rdata,
                rpower,
                tot_overnight_cost,
                tot_cap_investment,
                n_th,
                ITC_0,
                n_ITC):
    """
    Investment tax credit subsidies

    Parameters
    ----------
    rdata,
                rpower,
                tot_overnight_cost,
                tot_cap_investment,
                n_th,
                ITC_0,
                n_ITC

    Returns
    -------
    tuple(DataFrame, float, float)
    """
    ITC = np.zeros(n_th.shape)

    for i in range(n_th.shape[0]):
        for j in range(n_th.shape[1]):
            if n_th[i,j] <= n_ITC[i,j]:
                ITC[i,j] = ITC_0[i,j]
            else:
                ITC[i,j] = 0

    db1 = copy.deepcopy(rdata)

    ITC_cost_reduction_factor = ITC_reduction_factor(ITC)
    
    ITC_reduced_OCC = tot_overnight_cost * ITC_cost_reduction_factor

    OCC_cost_reduction_due_to_TCI = tot_overnight_cost - ITC_reduced_OCC

    #db1.loc[db1.Title == 'Total Overnight Cost - ITC reduced', 'Total Cost (USD)'] = None
    #db1.loc[db1.Title == 'Total Overnight Cost -ITC reduced (US$/kWe)', 'Total Cost (USD)'] = None
    #db1.loc[db1.Title == 'Total Capital Investment Cost - ITC reduced', 'Total Cost (USD)'] = None
    #db1.loc[db1.Title == 'Total Capital Investment Cost - ITC reduced (US$/kWe)', 'Total Cost (USD)'] = None
    
    db1['total_cost']['Total Overnight Cost - ITC reduced (USD)'] = ITC_reduced_OCC
    #db1.loc[db1.Title == 'Total Overnight Cost - ITC reduced',
    #        'Total Cost (USD)'] = ITC_reduced_OCC

    db1['total_cost']['Total Overnight Cost - ITC reduced (US$/kWe)'] = ITC_reduced_OCC / rpower
    #db1.loc[db1.Title == 'Total Overnight Cost -ITC reduced (US$/kWe)', 
    #        'Total Cost (USD)'] = ITC_reduced_OCC / rpower

    db1['total_cost']['Total Capital Investment Cost - ITC reduced (USD)'] = tot_cap_investment - OCC_cost_reduction_due_to_TCI
    #db1.loc[db1.Title == 'Total Capital Investment Cost - ITC reduced',
    #        'Total Cost (USD)'] = tot_cap_investment - OCC_cost_reduction_due_to_TCI

    levelized_NCI = db1['total_cost']['Total Capital Investment Cost - ITC reduced (USD)'] / rpower
    #levelized_NCI = db1.loc[db1.Title == 'Total Capital Investment Cost - ITC reduced',
    #    'Total Cost (USD)'].values[0] / rpower
    db1['total_cost']['Total Capital Investment Cost - ITC reduced (US$/kWe)'] = levelized_NCI
    #db1.loc[db1.Title == 'Total Capital Investment Cost - ITC reduced (US$/kWe)',
    #    'Total Cost (USD)'] = levelized_NCI

    rdata_updated = update_high_level_costs(db1, rpower)

    return (copy.deepcopy(rdata_updated),
            ITC_reduced_OCC / rpower,
            levelized_NCI)


def calculate_final_result(reactor_type,
                            n_th,
                            f_22,
                            f_2321,
                            land_cost_per_acre_0,
                            RB_grade_0,
                            BOP_grade_0,
                            num_orders,
                            design_completion_0,
                            ae_exp_0,
                            N_AE,
                            ce_exp_0,
                            N_cons,
                            mod_0,
                            Design_Maturity_0,
                            proc_exp_0,
                            N_proc,
                            standardization_0,
                            interest_rate_0,
                            ITC_0,
                            n_ITC,
                            startup_0,
                            om_variable,
                            om_fixed,
                            spent_fuel_cost,
                            capacity_factor = 0.95):
    """

    Parameters
    ----------
    reactor_type,
    n_th,
    f_22,
    f_2321,
    land_cost_per_acre_0,
    RB_grade_0,
    BOP_grade_0,
    num_orders,
    design_completion_0,
    ae_exp_0,
    N_AE,
    ce_exp_0,
    N_cons,
    mod_0,
    Design_Maturity_0,
    proc_exp_0,
    N_proc,
    standardization_0,
    interest_rate_0,
    ITC_0,
    n_ITC,
    startup_0
    om_variable
    om_fixed
    capacity_factor

    Returns
    -------
    tuple    
    """
    if reactor_type == 'Concept A':
        raise NotImplementedError

    reactor_data = reactor_data_read(reactor_type)[0]
    reactor_power = reactor_data_read(reactor_type)[1]

    tot_base_cost_results = calculate_base_cost(reactor_type,
                                                n_th,
                                                f_22,
                                                f_2321,
                                                land_cost_per_acre_0,
                                                RB_grade_0,
                                                BOP_grade_0,
                                                num_orders,
                                                design_completion_0,
                                                ae_exp_0,
                                                N_AE,
                                                ce_exp_0,
                                                N_cons,
                                                mod_0,
                                                Design_Maturity_0,
                                                proc_exp_0,
                                                N_proc,
                                                standardization_0)
    
    tot_base_cost = tot_base_cost_results[0]
    final_construction_duration = tot_base_cost_results[1]

    tot_base_cost_wz_insurance = insurance_cost_update(reactor_data, reactor_power, tot_base_cost)
    
    tot_base_cost_wz_insurance_interest_results = update_interest_cost(tot_base_cost_wz_insurance,
                                                                        reactor_power, 
                                                                        final_construction_duration,
                                                                        interest_rate_0,
                                                                        startup_0,
                                                                        n_th)

    tot_base_cost_wz_insurance_interest = tot_base_cost_wz_insurance_interest_results[0]
    tot_overnight_cost = tot_base_cost_wz_insurance_interest_results[1]
    tot_cap_investment = tot_base_cost_wz_insurance_interest_results[2]

    Final_Result = update_itc(tot_base_cost_wz_insurance_interest,
                              reactor_power,
                              tot_overnight_cost,
                              tot_cap_investment,
                              n_th,
                              ITC_0,
                              n_ITC)
    
    Final_Result_COA = Final_Result[0]
    levelized_net_OCC = Final_Result[1]
    levelized_NCI = Final_Result[2]
    
    # Annual fixed operating and maintenance costs, including spent fuel cost
    # om_fixed is USD/kWe-year and spent_fuel_cost is in USD/MWh
    # To scale the spent fuel cost, reactor_power is converted to MWh using
    # hours/year and capacity factor, then dividing by 1000
    fixed_costs = om_fixed * reactor_power + spent_fuel_cost * (reactor_power*8760*capacity_factor/1000)

    # Annual variable operating and maintenance costs
    variable_costs = om_variable * (reactor_power*8760*capacity_factor/1000)

    # For use with Tyche, sum the fixed and variable costs together
    om_costs = fixed_costs + variable_costs

    # MWh of electricity produced in a year - for production function
    elec_out = reactor_power * capacity_factor * 8760.0 / 1000.0

    # total overnight cost - ITC reduced - USD/kWe
    occ_kwe = Final_Result_COA['total_cost']['Total Overnight Cost - ITC reduced (US$/kWe)']
    #occ_kwe = Final_Result_COA.iloc[-4]['Total Cost (USD)']

    # total capital investment cost - ITC reduced - USD/kWe
    tci_kwe = Final_Result_COA['total_cost']['Total Capital Investment Cost - ITC reduced (US$/kWe)']
    #tci_kwe = Final_Result_COA.iloc[-1]['Total Cost (USD)']

    return (Final_Result_COA,
            levelized_net_OCC,
            levelized_NCI,
            final_construction_duration,
            om_costs,
            elec_out,
            Final_Result_COA['total_cost']['Total Overnight Cost - ITC reduced (USD)'])



def capital_cost(scale, parameter, atb_data = None):
  """
  Capital cost function.

  Parameters
  ----------
  scale : float
    The scale of operation.
  parameter : array
    The technological parameterization.
  """
  # See the input dataset for parameter definitions, units, and ranges
  all_results = calculate_final_result(
    reactor_type = 'Concept B',
    n_th = parameter[15],
    f_22 = parameter[19],
    f_2321 = parameter[20],
    land_cost_per_acre_0 = parameter[5],
    RB_grade_0 = parameter[10],
    BOP_grade_0 = parameter[9],
    num_orders = parameter[14],
    design_completion_0 = parameter[1],
    ae_exp_0 = parameter[3],
    N_AE = parameter[16],
    ce_exp_0 = parameter[4],
    N_cons = parameter[18],
    mod_0 = parameter[11],
    Design_Maturity_0 = parameter[0],
    proc_exp_0 = parameter[2],
    N_proc = parameter[17],
    standardization_0 = parameter[12],
    interest_rate_0 = parameter[8],
    ITC_0 = parameter[6],
    n_ITC = parameter[7],
    startup_0 = parameter[13],
    om_fixed = parameter[22],
    om_variable = parameter[21],
    spent_fuel_cost = parameter[23],
  )

  # Stack the capital cost values into a single array to return.
  # The second element of the tuple returned by calculate_final_result is the
  # total overnight capital cost for the entire reactor.
  return np.stack(all_results[0]['total_cost']['Total Capital Investment Cost - ITC reduced (USD)'] * scale**0.6)


def fixed_cost(scale, parameter, atb_data = None):
  """
  Fixed O&M cost function.

  Parameters
  ----------
  scale : float
    The scale of operation.
  parameter : array
    The technological parameterization.
  """
  all_results = calculate_final_result(
    reactor_type = 'Concept B',
    n_th = parameter[15],
    f_22 = parameter[19],
    f_2321 = parameter[20],
    land_cost_per_acre_0 = parameter[5],
    RB_grade_0 = parameter[10],
    BOP_grade_0 = parameter[9],
    num_orders = parameter[14],
    design_completion_0 = parameter[1],
    ae_exp_0 = parameter[3],
    N_AE = parameter[16],
    ce_exp_0 = parameter[4],
    N_cons = parameter[18],
    mod_0 = parameter[11],
    Design_Maturity_0 = parameter[0],
    proc_exp_0 = parameter[2],
    N_proc = parameter[17],
    standardization_0 = parameter[12],
    interest_rate_0 = parameter[8],
    ITC_0 = parameter[6],
    n_ITC = parameter[7],
    startup_0 = parameter[13],
    om_fixed = parameter[22],
    om_variable = parameter[21],
    spent_fuel_cost = parameter[23],
  )

  return np.stack(all_results[4] * scale)


def production(scale, capital, lifetime, fixed, input, parameter, atb_data = None):
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
  all_results = calculate_final_result(
    reactor_type = 'Concept B',
    n_th = parameter[15],
    f_22 = parameter[19],
    f_2321 = parameter[20],
    land_cost_per_acre_0 = parameter[5],
    RB_grade_0 = parameter[10],
    BOP_grade_0 = parameter[9],
    num_orders = parameter[14],
    design_completion_0 = parameter[1],
    ae_exp_0 = parameter[3],
    N_AE = parameter[16],
    ce_exp_0 = parameter[4],
    N_cons = parameter[18],
    mod_0 = parameter[11],
    Design_Maturity_0 = parameter[0],
    proc_exp_0 = parameter[2],
    N_proc = parameter[17],
    standardization_0 = parameter[12],
    interest_rate_0 = parameter[8],
    ITC_0 = parameter[6],
    n_ITC = parameter[7],
    startup_0 = parameter[13],
    om_fixed = parameter[22],
    om_variable = parameter[21],
    spent_fuel_cost = parameter[23],
  )
  # Return: MWh electricity produced in a year
  # Constant value, does not change with parameters
  # Accounts for capacity factor
  _elec_out = all_results[5] * np.ones(scale.shape) * scale
  return np.stack(_elec_out)


def metrics(scale, capital, lifetime, fixed, input_raw, input, input_price, output_raw, output, cost, parameter, atb_data = None):
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
  all_results = calculate_final_result(
    reactor_type = 'Concept B',
    n_th = parameter[15],
    f_22 = parameter[19],
    f_2321 = parameter[20],
    land_cost_per_acre_0 = parameter[5],
    RB_grade_0 = parameter[10],
    BOP_grade_0 = parameter[9],
    num_orders = parameter[14],
    design_completion_0 = parameter[1],
    ae_exp_0 = parameter[3],
    N_AE = parameter[16],
    ce_exp_0 = parameter[4],
    N_cons = parameter[18],
    mod_0 = parameter[11],
    Design_Maturity_0 = parameter[0],
    proc_exp_0 = parameter[2],
    N_proc = parameter[17],
    standardization_0 = parameter[12],
    interest_rate_0 = parameter[8],
    ITC_0 = parameter[6],
    n_ITC = parameter[7],
    startup_0 = parameter[13],
    om_fixed = parameter[22],
    om_variable = parameter[21],
    spent_fuel_cost = parameter[23],
  )
  # Metrics: construction duration (months), levelized net overnight capital cost,
  # levelized net capital investment
  return np.stack([all_results[3],
                   all_results[1] * scale**0.6,
                   all_results[2],
                   all_results[6] * scale**0.6])