import marimo

__generated_with = "0.15.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # Derived from The Algorithm for the Capital Cost Estimation of Reactor Technologies (ACCERT)
    # See original repo at: https://github.com/accert-dev/ACCERT/
    # Original code is Copyright © 2023 UChicago Argonne, LLC

    # Code adaptation: Rebecca Hanes, 2025, NREL
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    <center><table>
        <tr>
            <th><img src="./INL1.png",align="middle",height="10000"/></th>
            <th><img src="./MIT1.png",align="middle",height="10"\></th>
            <th><img src="./ANL.png",align="middle",height="10"/></th>
        </tr>
    </table>
    </center>
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# <center>Cost Reduction Framework for Nuclear Reactor Power Plants</center>""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""###  Importing the libraries""")
    return


@app.cell
def _():
    import pandas as pd
    import numpy as np
    from src import update_high_level_costs, ITC_reduction_factor

    import warnings

    pd.set_option('display.max_rows', None)
    return ITC_reduction_factor, np, pd, update_high_level_costs


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Section 1 : Reading the Baseline reactor Cost Summary Table""")
    return


@app.cell
def _(pd):
    def reactor_data_read(rtype = 'Concept B',
                          datafilepath = 'Cost_Reduction/conceptb-inputs.xlsx'):
        """
        Read in baseline cost data for a 300 MWe small modular reactor using
        sodium fast reactor technology.

        Parameters
        ----------
        rtype : string, Default = 'Concept B'
        Reactor type. Calculations are only implemented for Concept B types.

        datafilepath : string, Default = 'Cost_Reduction/conceptb-inputs.xlsx'
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
        rpower = 310.8 * 1000
        sp = pd.read_excel(datafilepath,
                           sheet_name='Ref Spending Curve',
                           usecols='A : D')

        return (rdata,
                rpower,
                sp)
    return (reactor_data_read,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Section - 2 : User Inputs""")
    return


@app.cell
def _():
    # User specified parameters

    # DO NOT CHANGE this one
    reactor_type = 'Concept B'

    # OK to change the rest of these
    n_th = 1
    num_orders = 13
    land_cost_per_acre_0 = 22000
    startup_0 = 16
    interest_rate_0 = 0.06
    design_completion_0 = 0.8
    Design_Maturity_0 = 1
    proc_exp_0 = 0.5
    ae_exp_0 = 0.5
    ce_exp_0 = 1
    N_proc = 3
    N_AE = 4
    N_cons = 5
    mod_0 = 'modularized'
    standardization_0 = 0.8
    BOP_grade_0 = 'non_nuclear'
    RB_grade_0 = 'nuclear'
    ITC_0 = 0
    n_ITC = 3
    f_22 = 250000000
    f_2321 = 150000000
    return (
        BOP_grade_0,
        Design_Maturity_0,
        ITC_0,
        N_AE,
        N_cons,
        N_proc,
        RB_grade_0,
        ae_exp_0,
        ce_exp_0,
        design_completion_0,
        f_22,
        f_2321,
        interest_rate_0,
        land_cost_per_acre_0,
        mod_0,
        n_ITC,
        n_th,
        num_orders,
        proc_exp_0,
        reactor_type,
        standardization_0,
        startup_0,
    )


@app.cell
def _(
    BOP_grade_0,
    Design_Maturity_0,
    ITC_0,
    RB_grade_0,
    ae_exp_0,
    ce_exp_0,
    design_completion_0,
    interest_rate_0,
    land_cost_per_acre_0,
    mod_0,
    pd,
    proc_exp_0,
    standardization_0,
    startup_0,
):
    global_levers = pd.read_csv('Cost_Reduction/global_levers_baselines.csv')

    global_levers.loc[:, 'User-Input Value'] = [Design_Maturity_0,
                                                design_completion_0,
                                                proc_exp_0,
                                                ae_exp_0,
                                                ce_exp_0,
                                                land_cost_per_acre_0,
                                                ITC_0,
                                                interest_rate_0,
                                                BOP_grade_0,
                                                RB_grade_0,
                                                mod_0,
                                                standardization_0,
                                                startup_0]

    global_levers
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### The Cost reduction framework: levers and variables impact the costs as shown in the figure (below)

    <center><table>
        <tr>
            <th><img src="./framework_diagram.png",align="middle",height="10000"/></th>
        </tr>
    </table>
    </center>
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Section - 3 : Updating the Cost Summary based on user inputs""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Section - 3-0 : Adding the factory cost to accounts 22 and 232.1""")
    return


@app.cell
def _(num_orders, update_high_level_costs):
    def add_factory_cost(rdata, 
                         rpower,
                         f_22,
                         f_2321):
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

        # Clear old values
        db.loc[db.Account == 22, 'Factory Equipment Cost'] = None
        db.loc[db.Account == 232.1, 'Factory Equipment Cost'] = None

        db.loc[db.Account == 22, 'Factory Equipment Cost'] = rdata.loc[
            rdata.Account == 22,
            'Factory Equipment Cost'
            ] + f_22 / num_orders

        db.loc[db.Account == 232.1, 'Factory Equipment Cost'] = rdata.loc[
            rdata.Account == 232.1,
            'Factory Equipment Cost'
            ] + f_2321 / num_orders

        rdata_updated = update_high_level_costs(db, rpower)

        return rdata_updated.copy()
    return (add_factory_cost,)


@app.cell
def _(reactor_data_read, reactor_type):
    reactor_data = (reactor_data_read(reactor_type))[0]
    reactor_power = (reactor_data_read(reactor_type))[1]
    return reactor_data, reactor_power


@app.cell
def _(add_factory_cost, f_22, f_2321, reactor_data, reactor_power):
    reactor_data_factory = add_factory_cost(reactor_data,
                                            reactor_power,
                                            f_22,
                                            f_2321)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Section 3-1 : The land cost & Taxes""")
    return


@app.cell
def _(pd, update_high_level_costs):
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
        db = pd.DataFrame()

        db = rdata.copy()

        db.loc[db.Account == 11, 'Total Cost (USD)'] = None
        db.loc[db.Account == 12, 'Total Cost (USD)'] = None
        db.loc[db.Account == 51, 'Total Cost (USD)'] = None

        db.loc[db.Account == 11, 'Total Cost (USD)'] = land_cost_per_acre / 22000 *\
            rdata.loc[rdata.Account == 11, 'Total Cost (USD)'].values

        db.loc[db.Account == 12, 'Total Cost (USD)'] = land_cost_per_acre / 22000 *\
            rdata.loc[rdata.Account == 12, 'Total Cost (USD)'].values

        # The taxes scale with increasing the land cost 
        db.loc[db.Account == 51, 'Total Cost (USD)'] = land_cost_per_acre / 22000 *\
            rdata.loc[rdata.Account == 51, 'Total Cost (USD)'].values

        rdata_updated = update_high_level_costs(db, rpower)

        return rdata_updated.copy()

    return (add_land_cost,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Section 3-2 : Whether the Reactor Building and BOP are nuclear grade equipment""")
    return


@app.cell
def _(update_high_level_costs):
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
        RB_grade = RB_grade_0
        BOP_grade = BOP_grade_0

        db = rdata.copy()

        db.loc[db.Account == 212, 'Site Material Cost'] = None
        db.loc[db.Account == 212, 'Site Labor Cost'] = None
        db.loc[db.Account == 212, 'Site Labor Hours'] = None
        db.loc[db.Account == 212, 'Factory Equipment Cost'] = None
        db.loc[db.Account == 213, 'Site Material Cost'] = None
        db.loc[db.Account == 213, 'Site Labor Cost'] = None
        db.loc[db.Account == 213, 'Site Labor Hours'] = None
        db.loc[db.Account == 213, 'Factory Equipment Cost'] = None
        db.loc[db.Account == 232.1, 'Factory Equipment Cost'] = None
        db.loc[db.Account == 232.1, 'Site Labor Cost'] = None
        db.loc[db.Account == 232.1, 'Site Labor Hours'] = None

        if RB_grade == 'non_nuclear':
            db.loc[db.Account == 212, 'Site Material Cost'] = 0.6 *\
                rdata.loc[rdata.Account == 212, 'Site Material Cost'].values[0]
            db.loc[db.Account == 212, 'Site Labor Cost'] = 0.6 *\
                rdata.loc[rdata.Account == 212, 'Site Labor Cost'].values[0]
            db.loc[db.Account == 212, 'Site Labor Hours'] = 0.6 *\
                rdata.loc[rdata.Account == 212, 'Site Labor Hours'].values[0]
            db.loc[db.Account == 212, 'Factory Equipment Cost'] = 0.6 *\
                rdata.loc[rdata.Account == 212, 'Factory Equipment Cost'].values[0]
        else:
            db.loc[db.Account == 212, 'Site Material Cost'] = \
                rdata.loc[rdata.Account == 212, 'Site Material Cost'].values[0]
            db.loc[db.Account == 212, 'Site Labor Cost'] = \
                rdata.loc[rdata.Account == 212, 'Site Labor Cost'].values[0]
            db.loc[db.Account == 212, 'Site Labor Hours'] = \
                rdata.loc[rdata.Account == 212, 'Site Labor Hours'].values[0]
            db.loc[db.Account == 212, 'Factory Equipment Cost'] = \
                rdata.loc[rdata.Account == 212, 'Factory Equipment Cost'].values[0]

        if BOP_grade == 'non_nuclear':
            db.loc[db.Account == 213, 'Site Material Cost'] = 0.6 * rdata.loc[rdata.Account == 213, 'Site Material Cost'].values[0]
            db.loc[db.Account == 213, 'Site Labor Cost'] = 0.6 *\
                rdata.loc[rdata.Account == 213, 'Site Labor Cost'].values[0]
            db.loc[db.Account == 213, 'Site Labor Hours'] = 0.6 *\
                rdata.loc[rdata.Account == 213, 'Site Labor Hours'].values[0]
            db.loc[db.Account == 213, 'Factory Equipment Cost'] = 0.6 *\
                rdata.loc[rdata.Account == 213, 'Factory Equipment Cost'].values[0]
            db.loc[db.Account == 232.1, 'Factory Equipment Cost'] = 0.6 *\
                rdata.loc[rdata.Account == 232.1, 'Factory Equipment Cost'].values[0]
            db.loc[db.Account == 232.1, 'Site Labor Hours'] = 0.6 *\
                rdata.loc[rdata.Account == 232.1, 'Site Labor Hours'].values[0]
            db.loc[db.Account == 232.1, 'Site Labor Cost'] = 0.6 *\
                rdata.loc[rdata.Account == 232.1, 'Site Labor Cost'].values[0]
        else:
            db.loc[db.Account == 213, 'Site Material Cost'] = \
                rdata.loc[rdata.Account == 213, 'Site Material Cost'].values[0]
            db.loc[db.Account == 213, 'Site Labor Cost'] = \
                rdata.loc[rdata.Account == 213, 'Site Labor Cost'].values[0]
            db.loc[db.Account == 213, 'Site Labor Hours'] = \
                rdata.loc[rdata.Account == 213, 'Site Labor Hours'].values[0]
            db.loc[db.Account == 213, 'Factory Equipment Cost'] = \
                rdata.loc[rdata.Account == 213, 'Factory Equipment Cost'].values[0]
            db.loc[db.Account == 232.1, 'Factory Equipment Cost'] = \
                rdata.loc[rdata.Account == 232.1, 'Factory Equipment Cost'].values[0]
            db.loc[db.Account == 232.1, 'Site Labor Hours'] = \
                rdata.loc[rdata.Account == 232.1, 'Site Labor Hours'].values[0]
            db.loc[db.Account == 232.1, 'Site Labor Cost'] = \
                rdata.loc[rdata.Account == 232.1, 'Site Labor Cost'].values[0]

        rdata_updated = update_high_level_costs(db, rpower)

        return rdata_updated.copy()
    return (add_BOP_RP_grades,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Section 3-3 : Bulk Ordering""")
    return


@app.cell
def _(np, update_high_level_costs):
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

        reduction_factor_22 = 0
        reduction_factor_2321 = 0

        for ith_unit in range(1, num_orders + 1):
            reduction_factor_22 = reduction_factor_22 + (1 - lr22) ** np.log2(ith_unit) / num_orders
            reduction_factor_2321 = reduction_factor_2321 + (1 - lr2321) ** np.log2(ith_unit) / num_orders

        for x in [22, 232.1]:
            db.loc[db.Account == x, 'Factory Equipment Cost'] = None

        db.loc[db.Account == 22, 'Factory Equipment Cost'] = reduction_factor_22 * \
            (rdata.loc[rdata.Account == 22, 'Factory Equipment Cost'] - f_22 / num_orders) + f_22 / num_orders

        db.loc[db.Account == 232.1, 'Factory Equipment Cost'] = reduction_factor_2321 * \
            (rdata.loc[rdata.Account == 232.1, 'Factory Equipment Cost'] - f_2321 / num_orders) + f_2321 / num_orders

        rdata_updated = update_high_level_costs(db, rpower)

        return rdata_updated.copy()
    return (add_bulk_ordering,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Section 3-4 : Reworking and labor productivity""")
    return


@app.cell
def _(update_high_level_costs):
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
        if n_th == 1:
            design_completion = design_completion_0
            ae_exp = ae_exp_0
            ce_exp = ce_exp_0
        elif n_th > 1:
            design_completion = 1
            ae_exp = min(ae_exp_0 + 2 / N_AE * (n_th - 1), 2)
            ce_exp = min(ce_exp_0 + 2 / N_cons * (n_th - 1), 2)

        productivity = 0.145 * ce_exp + 0.71
    
        if reactor_type != 'Concept B':
            raise NotImplementedError
    
        reworking_factor = (-0.9 * design_completion + 1.9) * (-0.15 * ae_exp + 1.3) * (-0.15 * ce_exp + 1.3)

        db = rdata.copy()

        for x in [212, 213, '211 plus 214 to 219', 22, 232.1, 233, 24, 26]:
            db.loc[db.Account == x, 'Factory Equipment Cost'] = None
            db.loc[db.Account == x, 'Site Labor Hours'] = None
            db.loc[db.Account == x, 'Site Labor Cost'] = None
            db.loc[db.Account == x, 'Site Material Cost'] = None

        for x in [212, 213, '211 plus 214 to 219', 22, 232.1, 233, 24, 26]:
            db.loc[db.Account == x, 'Factory Equipment Cost'] = reworking_factor *\
                rdata.loc[rdata.Account == x,'Factory Equipment Cost'].values[0]
            db.loc[db.Account == x, 'Site Labor Hours'] = reworking_factor / productivity *\
                rdata.loc[rdata.Account == x, 'Site Labor Hours'].values[0]
            db.loc[db.Account == x, 'Site Labor Cost'] = reworking_factor / productivity *\
                rdata.loc[rdata.Account == x, 'Site Labor Cost'].values[0]
            db.loc[db.Account == x, 'Site Material Cost'] = reworking_factor *\
                rdata.loc[rdata.Account == x, 'Site Material Cost'].values[0]

        rdata_updated = update_high_level_costs(db, rpower)

        return rdata_updated[['Account',
                              'Title',
                              'Total Cost (USD)',
                              'Factory Equipment Cost',
                              'Site Labor Hours',
                              'Site Labor Cost',
                              'Site Material Cost']].copy()
    return (add_reworking_productivity,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""#### Combine the previous functions in one function""")
    return


@app.cell
def _(
    add_BOP_RP_grades,
    add_bulk_ordering,
    add_factory_cost,
    add_land_cost,
    add_reworking_productivity,
    reactor_data_read,
):
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
                                         f_2321)

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

        return rdata_factory_land_taxes_BOP_RP_grades_bulkOrder_rework_productivity
    return (update_direct_cost,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Section 3-5 :Update construction duration from labor hours""")
    return


@app.cell
def _(reactor_type):
    def update_cons_dur(rdata,
                        rdata_updated,
                        mod_0):
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
    
        sum_old_lab_hrs = rdata.loc[rdata.Account == 21, 'Site Labor Hours'].values +\
        rdata.loc[rdata.Account == 22, 'Site Labor Hours'].values +\
        rdata.loc[rdata.Account == 23, 'Site Labor Hours'].values +\
        rdata.loc[rdata.Account == 24, 'Site Labor Hours'].values +\
        rdata.loc[rdata.Account == 26, 'Site Labor Hours'].values

        sum_new_lab_hrs = rdata_updated.loc[rdata_updated.Account == 21, 'Site Labor Hours'].values +\
        rdata_updated.loc[rdata_updated.Account == 22, 'Site Labor Hours'].values +\
        rdata_updated.loc[rdata_updated.Account == 23, 'Site Labor Hours'].values +\
        rdata_updated.loc[rdata_updated.Account == 24, 'Site Labor Hours'].values +\
        rdata_updated.loc[rdata_updated.Account == 26, 'Site Labor Hours'].values

        labor_hour_ratio = sum_new_lab_hrs / sum_old_lab_hrs

        if mod_0 == 'stick_built':
            mod_factor = 0.8
        elif mod_0 == 'modularized':
            mod_factor = 1
    
        baseline_construction_duration = 64 / mod_factor

        return baseline_construction_duration * (0.3 * labor_hour_ratio + 0.7)
    return (update_cons_dur,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Section 3-6 Learning by doing effect on the cost""")
    return


@app.cell
def _(np, pd, update_high_level_costs):
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
        if n_th == 1:
            standardization = 0.7
        elif n_th > 1:
            standardization = standardization_0

        fitted_LR = pd.DataFrame()
        fitted_LR.loc[:, 'Account'] = rdata.loc[:, 'Account']
        fitted_LR.loc[:, 'Title'] = rdata.loc[:, 'Title']

        fitted_LR = fitted_LR.loc[fitted_LR['Account'].isin([212, 213, '211 plus 214 to 219', 22, 232.1, 233, 24, 26])]

        fitted_LR['Mat LR'] = np.array(
            [0.099588665391,
             0.099588665391,
             0.099588665391,
             0.080817992281,
             0.0,
             0.099588665391,
             0.099588665391,
             0.099588665391]
        ) * standardization / 0.7

        fitted_LR['Lab LR'] = np.array(
            [0.180678729399,
             0.180678729399,
             0.180678729399,
             0.146555539499,
             0.137148574884,
             0.180678729399,
             0.180678729399,
             0.180678729399]
        ) * standardization / 0.7

        db = rdata.copy()

        for x in [212, 213, '211 plus 214 to 219', 22, 232.1, 233, 24, 26]:
            db.loc[db.Account == x, 'Site Labor Hours'] = None
            db.loc[db.Account == x, 'Site Labor Cost'] = None
            db.loc[db.Account == x, 'Site Material Cost'] = None

        for x in [212, 213, '211 plus 214 to 219', 22, 232.1, 233, 24, 26]:
            mat_cost_reduction_multiplier = (1 - fitted_LR.loc[fitted_LR.Account == x, 'Mat LR'].values[0]) ** np.log2(n_th)
            lab_cost_reduction_multiplier = (1 - fitted_LR.loc[fitted_LR.Account == x, 'Lab LR'].values[0]) ** np.log2(n_th)

            db.loc[db.Account == x, 'Site Material Cost'] = mat_cost_reduction_multiplier *\
                rdata.loc[rdata.Account == x, 'Site Material Cost']
            db.loc[db.Account == x, 'Site Labor Hours'] = lab_cost_reduction_multiplier *\
                rdata.loc[rdata.Account == x, 'Site Labor Hours']
            db.loc[db.Account == x, 'Site Labor Cost'] = lab_cost_reduction_multiplier *\
                rdata.loc[rdata.Account == x, 'Site Labor Cost']

        rdata_updated = update_high_level_costs(db, rpower)

        return rdata_updated.copy()
    return (learning_effect,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Section 3-7 supply chain delays""")
    return


@app.function
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
    
    if n_th == 1:
        Design_Maturity = Design_Maturity_0
        proc_exp = proc_exp_0
    elif n_th > 1:
        Design_Maturity = 2
        proc_exp = min(proc_exp_0 + 2 / N_proc * (n_th - 1), 2)        

    B_21 = 42.1 * task_length_multiplier
    B_22 = 60.2 * task_length_multiplier
    B_23 = 14.8 * task_length_multiplier
    B_24 = 3.6 * task_length_multiplier
    B_25 = 10.1 * task_length_multiplier
    B_26 = 43.9 * task_length_multiplier
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

    T_end = max(T_21, T_22, T_23, T_24, T_25, T_26)

    supply_chain_delay = max(T_end - ref_construction_duration, 0)

    actual_construction_duration_plus_delay = cons_duration_no_delay + supply_chain_delay

    return actual_construction_duration_plus_delay


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Section 3-8 Learning by doing effect on the construction duration""")
    return


@app.cell
def _(np):
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
        if n_th == 1:
            standardization = 0.7
        elif n_th > 1:
            standardization = standardization_0

        fitted_LR_duration = 0.15 * standardization / 0.7

        duration_multiplier = (1 - fitted_LR_duration) ** np.log2(n_th)
    
        return duration_multiplier * actual_construction_duration_plus_delay[0]
    return (duration_learning_effect,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Section 3-9 Calculate the Indirect Cost and the standardization impact""")
    return


@app.cell
def _(update_high_level_costs):
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
        if n_th == 1:
            standardization = 0.7
        elif n_th > 1:
            standardization = standardization_0

        factor_35 = -3.33 * standardization + 3.331

        db = rdata.copy()

        for x in [31, 32, 33, 34, 35]:
            db.loc[db.Account == x, 'Total Cost (USD)'] = None

        sum_new_mat_cost = 0
        sum_new_lab_cost = 0
        sum_new_lab_hrs = 0
        for x in [21, 22, 23, 24, 26]:
            sum_new_mat_cost = sum_new_mat_cost + db.loc[db.Account == x, 'Site Material Cost'].values
            sum_new_lab_cost = sum_new_lab_cost + db.loc[db.Account == x, 'Site Labor Cost'].values
            sum_new_lab_hrs = sum_new_lab_hrs + db.loc[db.Account == x, 'Site Labor Hours'].values

        db.loc[db.Account == 31, 'Total Cost (USD)'] = sum_new_mat_cost * 0.785 * sum_new_lab_hrs / final_construction_duration / 160 / 1058 + sum_new_lab_cost * 0.36

        db.loc[db.Account == 32, 'Total Cost (USD)'] = sum_new_lab_cost * 0.36 * 3.661 * final_construction_duration / 72

        db.loc[db.Account == 33, 'Total Cost (USD)'] = 0.042 *\
            db.loc[db.Account == 32, 'Total Cost (USD)'].values[0]
        db.loc[db.Account == 34, 'Total Cost (USD)'] = 0.0035 *\
            db.loc[db.Account == 32, 'Total Cost (USD)'].values[0]
        db.loc[db.Account == 35, 'Total Cost (USD)'] = 0.27 * factor_35 *\
            db.loc[db.Account == 32, 'Total Cost (USD)'].values[0]

        rdata_updated = update_high_level_costs(db, rpower)

        return rdata_updated.copy()
    return (update_indirect_cost,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""#### Combine the previous functions in one function""")
    return


@app.cell
def _(
    duration_learning_effect,
    learning_effect,
    reactor_data_read,
    update_cons_dur,
    update_direct_cost,
    update_indirect_cost,
):
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

        return (direct_cost_updated_plus_learning_with_indirect_cost, final_con_duration)
    return (calculate_base_cost,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Section 3-10 :  Insurance""")
    return


@app.cell
def _(update_high_level_costs):
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
        db = rdata_tot_base_cost.copy()

        db0 = rdata.copy()

        db.loc[db.Account == 52, 'Total Cost (USD)'] = None

        change_in_insuance_cost = (db.loc[db.Title == '20s - Subtotal', 'Total Cost (USD)'].values +\
                                   db.loc[db.Title == '30s - Subtotal', 'Total Cost (USD)'].values) / \
        (db0.loc[db0.Title == '20s - Subtotal', 'Total Cost (USD)'].values +\
         db0.loc[db0.Title == '30s - Subtotal', 'Total Cost (USD)'].values)

        db.loc[db.Account == 52, 'Total Cost (USD)'] = change_in_insuance_cost[0] *\
            rdata_tot_base_cost.loc[db.Account == 52, 'Total Cost (USD)']

        rdata_updated = update_high_level_costs(db, rpower)

        return rdata_updated.copy()
    return (insurance_cost_update,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Section 3-11 :  Interest""")
    return


@app.cell
def _(np, reactor_data_read, update_high_level_costs):
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
        sp = reactor_data_read()[2]

        Months = sp['Month'].tolist()
        CDFs = sp['CDF'].tolist()
    
        annual_periods = np.linspace(12, 12 * int(final_construction_duration / 12), int(final_construction_duration / 12))

        if max(annual_periods) < int(final_construction_duration) - 1:
            annual_periods_1 = np.append(annual_periods, final_construction_duration - 1)
        else:
            annual_periods_1 = annual_periods

        annual_cum_spend = []

        for period in annual_periods_1:
            new_period = 103 * period / int(final_construction_duration)
            annual_cum_spend.append(np.interp(new_period, Months, CDFs))

        annual_cum_spend1 = np.append(annual_cum_spend[0], np.diff(annual_cum_spend))

        tot_overnight_cost = rdata.loc[
            rdata.Title == 'Total Overnight Cost (Accounts 10 to 50)',
            'Total Cost (USD)'
            ].values[0]

        annual_loan_add = annual_cum_spend1 * tot_overnight_cost

        interest_exp = (1 + interest_rate) ** ((final_construction_duration - annual_periods_1) / 12) * annual_loan_add - annual_loan_add

        tot_int_exp_construction = sum(interest_exp)

        if n_th == 1:
            startup = startup_0
        elif n_th > 1:
            startup = max(7, startup_0 * (1 - 0.3) ** np.log2(n_th))

        int_exp_startup = (tot_int_exp_construction + tot_overnight_cost) * (1 + interest_rate) ** (startup / 12) - (tot_int_exp_construction + tot_overnight_cost)

        db = rdata.copy()

        db.loc[db.Account == 62, 'Total Cost (USD)'] = None
        db.loc[db.Account == 62, 'Total Cost (USD)'] = int_exp_startup + tot_int_exp_construction

        rdata_updated = update_high_level_costs(db, rpower)

        tot_cap_investment = rdata_updated.loc[
            rdata_updated.Title == 'Total Capital Investment Cost (All Accounts)',
            'Total Cost (USD)'].values

        return (rdata_updated.copy(),
                tot_overnight_cost,
                tot_cap_investment)
    return (update_interest_cost,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Section 3 - 12 :  ITC Subsidies""")
    return


@app.cell
def _(ITC_reduction_factor, update_high_level_costs):
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
        if n_th <= n_ITC:
            ITC = ITC_0
        else:
            ITC = 0

        db1 = rdata.copy()

        ITC_cost_reduction_factor = ITC_reduction_factor(ITC)

        ITC_reduced_OCC = tot_overnight_cost * ITC_cost_reduction_factor

        OCC_cost_reduction_due_to_TCI = tot_overnight_cost - ITC_reduced_OCC

        db1.loc[db1.Title == 'Total Overnight Cost - ITC reduced', 'Total Cost (USD)'] = None
        db1.loc[db1.Title == 'Total Overnight Cost -ITC reduced (US$/kWe)', 'Total Cost (USD)'] = None
        db1.loc[db1.Title == 'Total Capital Investment Cost - ITC reduced', 'Total Cost (USD)'] = None
        db1.loc[db1.Title == 'Total Capital Investment Cost - ITC reduced (US$/kWe)', 'Total Cost (USD)'] = None

        db1.loc[db1.Title == 'Total Overnight Cost - ITC reduced',
                'Total Cost (USD)'] = ITC_reduced_OCC

        db1.loc[db1.Title == 'Total Overnight Cost -ITC reduced (US$/kWe)', 
                'Total Cost (USD)'] = ITC_reduced_OCC / rpower

        db1.loc[db1.Title == 'Total Capital Investment Cost - ITC reduced',
                'Total Cost (USD)'] = tot_cap_investment - OCC_cost_reduction_due_to_TCI

        levelized_NCI = db1.loc[db1.Title == 'Total Capital Investment Cost - ITC reduced',
            'Total Cost (USD)'].values[0] / rpower
        db1.loc[db1.Title == 'Total Capital Investment Cost - ITC reduced (US$/kWe)',
            'Total Cost (USD)'] = levelized_NCI

        rdata_updated = update_high_level_costs(db1, rpower)

        return (rdata_updated.copy(),
                ITC_reduced_OCC / rpower,
                levelized_NCI)
    return (update_itc,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""#### A Python function to combine all the previous ones""")
    return


@app.cell
def _(
    ITC_0,
    calculate_base_cost,
    insurance_cost_update,
    n_ITC,
    reactor_data_read,
    update_interest_cost,
    update_itc,
):
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
                               startup_0):
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
        startup_0

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

        return (Final_Result_COA, levelized_net_OCC, levelized_NCI, final_construction_duration)
    return (calculate_final_result,)


@app.cell
def _(
    BOP_grade_0,
    Design_Maturity_0,
    N_AE,
    N_cons,
    N_proc,
    RB_grade_0,
    ae_exp_0,
    calculate_final_result,
    ce_exp_0,
    design_completion_0,
    f_22,
    f_2321,
    interest_rate_0,
    land_cost_per_acre_0,
    mod_0,
    n_th,
    num_orders,
    proc_exp_0,
    reactor_type,
    standardization_0,
    startup_0,
):
    final_result_all = calculate_final_result(reactor_type,
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
                               startup_0)

    final_coa = final_result_all[0]

    levelized_net_occ = final_result_all[1]

    levelized_nci = final_result_all[2]

    construction_duration = final_result_all[3]
    return


@app.cell
def _():
    #final_coa.to_csv('Cost_Reduction/final_coa.csv', index=False)
    return


if __name__ == "__main__":
    app.run()
