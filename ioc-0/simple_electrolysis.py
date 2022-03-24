#!/usr/bin/env python
# coding: utf-8

# # Tyche Example for Simple Electrolysis

# ## Set up.

# ### One only needs to execute the following line once, in order to make sure recent enough packages are installed.

# In[ ]:


#!pip install 'numpy>=1.17.2' 'pandas>=0.25.1'


# ### Import packages.

# In[1]:


import os
import sys
sys.path.insert(0, os.path.abspath("../src"))


# In[2]:


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

# In[3]:


designs = ty.Designs("data/simple_electrolysis")


# In[4]:


investments = ty.Investments("data/simple_electrolysis")


# ### Compile the production and metric functions for each technology in the dataset.

# In[5]:


designs.compile()


# ## Examine the data.

# ### The `functions` table specifies where the Python code for each technology resides.

# In[6]:


designs.functions


# Right now, only the style `numpy` is supported.

# ### The `indices` table defines the subscripts for variables.

# In[7]:


designs.indices


# ### The `designs` table contains the cost, input, efficiency, and price data for a scenario.

# In[8]:


designs.designs


# ### The `parameters` table contains additional techno-economic parameters for each technology.

# In[9]:


designs.parameters


# ### The `results` table specifies the units of measure for results of computations.

# In[10]:


designs.results


# ### The `tranches` table specifies multually exclusive possibilities for investments: only one `Tranch` may be selected for each `Cateogry`.

# In[11]:


investments.tranches


# ### The `investments` table bundles a consistent set of tranches (one per category) into an overall investment.

# In[12]:


investments.investments


# ## Evaluate the scenarios in the dataset.

# In[13]:


scenario_results = designs.evaluate_scenarios(sample_count=50)


# In[14]:


scenario_results.xs(1, level="Sample", drop_level=False)


# ### Save results.

# In[15]:


scenario_results.to_csv("output/simple_electrolysis/example-scenario.csv")


# ### Plot GHG metric.

# In[16]:


g = sb.boxplot(
    x="Scenario",
    y="Value",
    data=scenario_results.xs(
        ["Metric", "GHG"],
        level=["Variable", "Index"]
    ).reset_index()[["Scenario", "Value"]],
    order=["Base Electrolysis", "Slow Progress on Electrolysis", "Moderate Progress on Electrolysis", "Fast Progress on Electrolysis"]
)
g.set(ylabel="GHG Footprint [gCO2e / gH2]")
g.set_xticklabels(g.get_xticklabels(), rotation=15);


# ### Plot cost metric.

# In[17]:


g = sb.boxplot(
    x="Scenario",
    y="Value",
    data=scenario_results.xs(
        ["Metric", "Cost"],
        level=["Variable", "Index"]
    ).reset_index()[["Scenario", "Value"]],
    order=["Base Electrolysis", "Slow Progress on Electrolysis", "Moderate Progress on Electrolysis", "Fast Progress on Electrolysis"]
)
g.set(ylabel="Cost [USD / gH2]")
g.set_xticklabels(g.get_xticklabels(), rotation=15);


# ### Plot employment metric.

# In[18]:


g = sb.boxplot(
    x="Scenario",
    y="Value",
    data=scenario_results.xs(
        ["Metric", "Jobs"],
        level=["Variable", "Index"]
    ).reset_index()[["Scenario", "Value"]],
    order=["Base Electrolysis", "Slow Progress on Electrolysis", "Moderate Progress on Electrolysis", "Fast Progress on Electrolysis"]
)
g.set(ylabel="Employment [job / gH2]")
g.set_xticklabels(g.get_xticklabels(), rotation=15);


# ## Evaluate the investments in the dataset.

# In[19]:


investment_results = investments.evaluate_investments(designs, sample_count=50)


# ### Costs of investments.

# In[20]:


investment_results.amounts


# ### Benefits of investments.

# In[21]:


investment_results.metrics.xs(1, level="Sample", drop_level=False)


# In[22]:


investment_results.summary.xs(1, level="Sample", drop_level=False)


# ### Save results.

# In[23]:


investment_results.amounts.to_csv("output/simple_electrolysis/example-investment-amounts.csv")


# In[24]:


investment_results.metrics.to_csv("output/simple_electrolysis/example-investment-metrics.csv")


# ### Plot GHG metric.

# In[25]:


g = sb.boxplot(
    x="Investment",
    y="Value",
    data=investment_results.metrics.xs(
        "GHG",
        level="Index"
    ).reset_index()[["Investment", "Value"]],
    order=["No R&D Spending", "Low R&D Spending", "Medium R&D Spending", "High R&D Spending"]
)
g.set(ylabel="GHG Footprint [gCO2e / gH2]")
g.set_xticklabels(g.get_xticklabels(), rotation=15);


# ### Plot cost metric.

# In[26]:


g = sb.boxplot(
    x="Investment",
    y="Value",
    data=investment_results.metrics.xs(
        "Cost",
        level="Index"
    ).reset_index()[["Investment", "Value"]],
    order=["No R&D Spending", "Low R&D Spending", "Medium R&D Spending", "High R&D Spending"]
)
g.set(ylabel="Cost [USD / gH2]")
g.set_xticklabels(g.get_xticklabels(), rotation=15);


# ### Plot employment metric.

# In[27]:


g = sb.boxplot(
    x="Investment",
    y="Value",
    data=investment_results.metrics.xs(
        "Jobs",
        level="Index"
    ).reset_index()[["Investment", "Value"]],
    order=["No R&D Spending", "Low R&D Spending", "Medium R&D Spending", "High R&D Spending"]
)
g.set(ylabel="Employment [job / gH2]")
g.set_xticklabels(g.get_xticklabels(), rotation=15);


# ## Sensitity analysis.

# ### Vary the four efficiencies in the design.

# In[28]:


# Four variables are involved.
variables = [
    ("Input efficiency" , "Water"      ),
    ("Input efficiency" , "Electricity"),
    ("Output efficiency", "Oxygen"     ),
    ("Output efficiency", "Hydrogen"   ),
]


# In[29]:


# Let efficiencies range from 0.75 to 0.975.
efficiencies = np.arange(0.750, 1.000, 0.025)
efficiencies


# ### Start from the base case.

# In[30]:


base_design = designs.designs.xs("Base Electrolysis", level=1, drop_level=False)
base_design


# In[31]:


base_parameters = designs.parameters.xs("Base Electrolysis", level=1, drop_level=False)
base_parameters


# ### Generate the new scenarios and append them to the previous ones.

# In[32]:


sensitivities = deepcopy(designs)
sensitivities.designs = sensitivities.designs[0:0]
sensitivities.parameters = sensitivities.parameters[0:0]


# In[33]:


# Iterate over variables and efficiencies.
for variable, index in variables:
    for efficiency in efficiencies:

        # Name the scenario.
        scenario = "Let " + variable + " @ " + index + " = " + str(round(efficiency, 3))
        
        # Alter the base case.
        vary_design = base_design.rename(index={"Base Electrolysis" : scenario}, level=1)
        vary_design.loc[("Simple electrolysis", scenario, variable, index), "Value"] = efficiency
        
        # Keep the parameters the same.
        vary_parameters = base_parameters.rename(index={"Base Electrolysis" : scenario}, level=1)
        
        # Append the results to the existing table of scenarios.
        sensitivities.designs = sensitivities.designs.append(vary_design)
        sensitivities.parameters = sensitivities.parameters.append(vary_parameters)


# #### Remember to compile the design, since we've added scenarios.

# In[34]:


sensitivities.compile()


# #### See how many rows there are in the tables now.

# In[35]:


sensitivities.designs.shape


# In[36]:


sensitivities.parameters.shape


# In[37]:


sensitivities.designs


# ### Compute the results.

# In[38]:


results = sensitivities.evaluate_scenarios(1)
results


# ### Plot the cost results.

# In[39]:


cost_results = results.xs("Cost", level="Variable").reset_index()[["Scenario", "Value"]]


# In[40]:


cost_results[0:10]


# In[41]:


cost_results["Variable"  ] = cost_results["Scenario"].apply(lambda x: re.sub(r'^Let (.*) @ (.*) =.*$', '\\1[\\2]', x))
cost_results["Efficiency"] = cost_results["Scenario"].apply(lambda x: float(re.sub(r'^.*= (.*)$', '\\1', x)))
cost_results["Cost [USD/mole]"] = cost_results["Value"]


# In[42]:


cost_results = cost_results[["Variable", "Efficiency", "Cost [USD/mole]"]]
cost_results[0:10]


# In[43]:


# Here is a really simple plot.
cost_results.plot(
    x="Efficiency",
    y="Cost [USD/mole]",
    c=cost_results["Variable"].apply(lambda v: {
        "Input efficiency[Water]"       : "blue"  ,
        "Input efficiency[Electricity]" : "orange",
        "Output efficiency[Oxygen]"     : "green" ,
        "Output efficiency[Hydrogen]"   : "red"   ,
    }[v]),
    kind="scatter"
)

