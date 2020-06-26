#!/usr/bin/env python
# coding: utf-8

# # Multiple Objectives for Residential PV

# ## Set up.

# ### One only needs to execute the following line once, in order to make sure recent enough packages are installed.

# In[1]:


#!pip install 'numpy>=1.17.2' 'pandas>=0.25.1'


# ### Import packages.

# In[2]:


import os
import sys
sys.path.insert(0, os.path.abspath("../src"))


# In[3]:


import numpy             as np
import matplotlib.pyplot as pl
import pandas            as pd
import re                as re
import scipy.stats       as st
import seaborn           as sb

# The `tyche` package is located at <https://github.com/NREL/portfolio/tree/master/production-function/framework/src/tyche/>.
import tyche             as ty

from copy import deepcopy


# ## Load data.

# ### The data are stored in a set of tab-separated value files in a folder.

# In[4]:


designs = ty.Designs("../data/residential_pv_multiobjective")


# In[5]:


investments = ty.Investments("../data/residential_pv_multiobjective")


# ### Compile the production and metric functions for each technology in the dataset.

# In[6]:


designs.compile()


# ## Examine the data.

# ### The `functions` table specifies where the Python code for each technology resides.

# In[7]:


designs.functions


# Right now, only the style `numpy` is supported.

# ### The `indices` table defines the subscripts for variables.

# In[8]:


designs.indices


# ### The `designs` table contains the cost, input, efficiency, and price data for a scenario.

# In[9]:


designs.designs


# ### The `parameters` table contains additional techno-economic parameters for each technology.

# In[10]:


designs.parameters


# ### The `results` table specifies the units of measure for results of computations.

# In[11]:


designs.results


# ### The `tranches` table specifies multually exclusive possibilities for investments: only one `Tranch` may be selected for each `Category`.

# In[12]:


investments.tranches


# ### The `investments` table bundles a consistent set of tranches (one per category) into an overall investment.

# In[13]:


investments.investments


# ## Evaluate the scenarios in the dataset.

# In[14]:


scenario_results = designs.evaluate_scenarios(sample_count=50)


# In[15]:


scenario_results.xs(1, level="Sample", drop_level=False)


# ### Save results.

# In[16]:


scenario_results.to_csv("output/residential_pv_multiobjective/example-scenario.csv")


# ### Plot GHG metric.

# In[17]:


g = sb.boxplot(
    x="Scenario",
    y="Value",
    data=scenario_results.xs(
        ["Metric", "GHG"],
        level=["Variable", "Index"]
    ).reset_index()[["Scenario", "Value"]],
    order=[
        "2015 Actual"              ,
        "Module Slow Progress"      ,
        "Module Moderate Progress"  ,
        "Module Fast Progress"      ,
        "Inverter Slow Progress"    ,
        "Inverter Moderate Progress",
        "Inverter Fast Progress"    ,
        "BoS Slow Progress"         ,
        "BoS Moderate Progress"     ,
        "BoS Fast Progress"         ,
    ]
)
g.set(ylabel="GHG Reduction [gCO2e / system]")
g.set_xticklabels(g.get_xticklabels(), rotation=30);


# ### Plot LCOE metric.

# In[18]:


g = sb.boxplot(
    x="Scenario",
    y="Value",
    data=scenario_results.xs(
        ["Metric", "LCOE"],
        level=["Variable", "Index"]
    ).reset_index()[["Scenario", "Value"]],
    order=[
        "2015 Actual"              ,
        "Module Slow Progress"      ,
        "Module Moderate Progress"  ,
        "Module Fast Progress"      ,
        "Inverter Slow Progress"    ,
        "Inverter Moderate Progress",
        "Inverter Fast Progress"    ,
        "BoS Slow Progress"         ,
        "BoS Moderate Progress"     ,
        "BoS Fast Progress"         ,
    ]
)
g.set(ylabel="LCOE Reduction [USD / kWh]")
g.set_xticklabels(g.get_xticklabels(), rotation=30);


# ### Plot labor metric.

# In[19]:


g = sb.boxplot(
    x="Scenario",
    y="Value",
    data=scenario_results.xs(
        ["Metric", "Labor"],
        level=["Variable", "Index"]
    ).reset_index()[["Scenario", "Value"]],
    order=[
        "2015 Actual"              ,
        "Module Slow Progress"      ,
        "Module Moderate Progress"  ,
        "Module Fast Progress"      ,
        "Inverter Slow Progress"    ,
        "Inverter Moderate Progress",
        "Inverter Fast Progress"    ,
        "BoS Slow Progress"         ,
        "BoS Moderate Progress"     ,
        "BoS Fast Progress"         ,
    ]
)
g.set(ylabel="Labor Increase [USD / system]")
g.set_xticklabels(g.get_xticklabels(), rotation=15);


# ## Evaluate the investments in the dataset.

# In[20]:


investment_results = investments.evaluate_investments(designs, sample_count=50)


# ### Costs of investments.

# In[21]:


investment_results.amounts


# ### Benefits of investments.

# In[22]:


investment_results.metrics.xs(1, level="Sample", drop_level=False)


# In[23]:


investment_results.summary.xs(1, level="Sample", drop_level=False)


# ### Save results.

# In[24]:


investment_results.amounts.to_csv("output/residential_pv_multiobjective/example-investment-amounts.csv")


# In[25]:


investment_results.metrics.to_csv("output/residential_pv_multiobjective/example-investment-metrics.csv")


# ### Plot GHG metric.

# In[26]:


g = sb.boxplot(
    x="Investment",
    y="Value",
    data=investment_results.metrics.xs(
        "GHG",
        level="Index"
    ).reset_index()[["Investment", "Value"]],
    order=[
        "Low R&D"   ,
        "Medium R&D",
        "High R&D"  ,
    ]
)
g.set(ylabel="GHG Reduction [gCO2e / system]")
g.set_xticklabels(g.get_xticklabels(), rotation=15);


# ### Plot LCOE metric.

# In[27]:


g = sb.boxplot(
    x="Investment",
    y="Value",
    data=investment_results.metrics.xs(
        "LCOE",
        level="Index"
    ).reset_index()[["Investment", "Value"]],
    order=[
        "Low R&D"   ,
        "Medium R&D",
        "High R&D"  ,
    ]
)
g.set(ylabel="LCOE Reduction [USD / kWh]")
g.set_xticklabels(g.get_xticklabels(), rotation=15);


# ### Plot labor metric.

# In[28]:


g = sb.boxplot(
    x="Investment",
    y="Value",
    data=investment_results.metrics.xs(
        "Labor",
        level="Index"
    ).reset_index()[["Investment", "Value"]],
    order=[
        "Low R&D"   ,
        "Medium R&D",
        "High R&D"  ,
    ]
)
g.set(ylabel="Labor Increase [USD / system]")
g.set_xticklabels(g.get_xticklabels(), rotation=15);


# ## Multi-objective decision analysis.

# <font color="red">**THIS IS A WORK IN PROGRESS.**</font>

# ### Compute costs and metrics for tranches.

# Tranches are atomic units for building investment portfolios. Evaluate all of the tranches, so we can assemble them into investments (portfolios).

# In[29]:


tranche_results = investments.evaluate_tranches(designs, sample_count=500)


# Display the cost of each tranche.

# In[30]:


tranche_results.amounts


# Display the metrics for each tranche.

# In[31]:


tranche_results.summary


# Save the results.

# In[32]:


tranche_results.amounts.to_csv("output/residential_pv_multiobjective/example-tranche-amounts.csv")
tranche_results.summary.to_csv("output/residential_pv_multiobjective/example-tranche-summary.csv")


# Here is an <font color="red">incomplete work-in-progress</font> on plotting metrics for tranches. <font color="red">The axis labels etc. need fixing.</font>

# In[33]:


g = sb.FacetGrid(
    tranche_results.summary.reset_index(),#.set_index(["Category", "Tranche"])join(tranche_results.amount).reset_index(),
    row="Index",
    col="Category",
#    row_order=["LCOE", "GHG", "Labor"],
#    col_order=["Module R&D", "Inverter R&D", "BoS R&D"],
    sharex=True,
    sharey=False,
)
g.map(sb.boxplot, "Tranche", "Value")


# ### Compute all combinations of tranches.

# #### Set up investment scenarios.

# We're just building all legal combinations of tranches into investment portfolios.

# In[34]:


z = None
for imod in np.append(investments.tranches.xs("Module R&D").reset_index("Scenario").index.unique().values, ""):
    for iinv in np.append(investments.tranches.xs("Inverter R&D").reset_index("Scenario").index.unique().values, ""):
        for ibos in np.append(investments.tranches.xs("BoS R&D").reset_index("Scenario").index.unique().values, ""):
            w = None
            name = imod 
            if iinv != "":
                if name != "":
                    name = name + " + "
                name = name + iinv
            if ibos != "":
                if name != "":
                    name = name + " + "
                name = name + ibos
            if imod != "":
                w = pd.DataFrame({
                    "Investment" : [name        ],
                    "Category"   : ["Module R&D"],
                    "Tranche"    : [imod        ],
                    "Notes"      : [""          ],
                }).append(w)
            if iinv != "":
                w = pd.DataFrame({
                    "Investment" : [name          ],
                    "Category"   : ["Inverter R&D"],
                    "Tranche"    : [iinv          ],
                    "Notes"      : [""            ],
                }).append(w)
            if ibos != "":
                w = pd.DataFrame({
                    "Investment" : [name     ],
                    "Category"   : ["BoS R&D"],
                    "Tranche"    : [ibos     ],
                    "Notes"      : [""       ],
                }).append(w)
            if w is not None:
                z = w.append(z)
z.set_index(["Investment", "Category", "Tranche"], inplace=True)
investments.investments = z
z


# #### Evaluate the investments.

# In[35]:


investment_results = investments.evaluate_investments(designs, sample_count=50)


# In[36]:


investment_results.amounts


# In[37]:


investment_results.summary.xs(1, level="Sample", drop_level=False)


# #### Plot the results.

# In[38]:


w = investment_results.summary.reset_index(
).set_index(
    ["Investment"]
).join(
    investment_results.amounts
).reset_index(
).set_index(
    ["Index"]
)
ww = investment_results.amounts.reset_index().sort_values("Amount")["Investment"]


# In[39]:


sb.set(rc={'figure.figsize':(6, 10)})


# ##### Cost of investments.

# In[40]:


www = investment_results.amounts.reset_index()
www["Amount"] = www["Amount"] / 1e6
g = sb.boxplot(data=www, y="Investment", x="Amount", orient="h", order=ww)
g.set(xlabel="Investment Cost [M$]");
#pl.savefig('example-amounts.png')


# #### LOCE benefits.

# In[41]:


g = sb.boxplot(data=w.xs("LCOE"), y="Investment", x="Value", orient="h", order=ww)
g.set(xlabel="LCOE Reduction [$/kWh]");


# ##### GHG benefits.

# In[42]:


g = sb.boxplot(data=w.xs("GHG"), y="Investment", x="Value", orient="h", order=ww)
g.set(xlabel="GHG Reduction [gCO2e/system]");


# ##### Labor benefits.

# In[43]:


g = sb.boxplot(data=w.xs("Labor"), y="Investment", x="Value", orient="h", order=ww)
g.set(xlabel="Labor Increase [$/system]");

