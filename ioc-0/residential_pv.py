#!/usr/bin/env python
# coding: utf-8

# # Residential Rooftop PV Example

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


# ## Scenario analyses.

# ### Load data.

# #### The data are stored in a set of tab-separated value files in a folder.

# In[3]:


designs = ty.Designs("../data/residential_pv")


# #### Compile the production and metric functions for each technology in the dataset.

# In[4]:


designs.compile()


# ### Examine the data.

# #### The `functions` table specifies where the Python code for each technology resides.

# In[5]:


designs.functions


# Right now, only the style `numpy` is supported.

# #### The `indices` table defines the subscripts for variables.

# In[6]:


designs.indices.sort_values(["Technology", "Type", "Offset"])


# #### The `designs` table contains the cost, input, efficiency, and price data for a scenario.

# In[7]:


designs.designs.xs("2015 Actual", level="Scenario", drop_level=False)


# #### The `parameters` table contains additional techno-economic parameters for each technology.

# In[8]:


designs.parameters.xs("2015 Actual", level="Scenario", drop_level=False).sort_values(["Technology", "Scenario", "Offset"])


# #### The `results` table specifies the units of measure for results of computations.

# In[9]:


designs.results


# #### Here is the source code for the computations.

# In[10]:


get_ipython().system('cat ../src/technology/residential_pv.py')


# ### Evaluate the scenarios in the dataset.

# In[11]:


scenario_results = designs.evaluate_scenarios(sample_count=500)


# In[12]:


scenario_results


# #### Plot the results.

# In[13]:


expert_results = scenario_results[["Value"]].xs(
    "LCOE", level="Index"
).rename(
    columns={"Value" : "LCOE [$/kWh]"}
).unstack(
    ["Scenario"]
).xs("LCOE [$/kWh]", axis=1, drop_level=True).reset_index(drop=True)
expert_results.plot.hist(bins=30)


# ### Make tornado plots for Expert A.

# #### Remember base case LCOE.

# In[14]:


base_lcoe = scenario_results.xs(["2015 Actual", "LCOE"], level=["Scenario", "Index"])[["Value"]].agg(np.mean)[0]
base_lcoe


# #### Define the factors.

# In[15]:


tornado_factors = [
    "MCC", "MLT", "MEF", "MAP", "MOM",
    "MDR", "ICC", "ILT", "IRC", "IEF",
    "BCC", "BLR", "BPR", "BCA", "BOH",
]


# #### Add the scenarios to the design.

# In[16]:


design_2015_actual    = designs.designs.xs   ("2015 Actual", level="Scenario")
parameter_2015_actual = designs.parameters.xs("2015 Actual", level="Scenario")
parameter_expert_a    = designs.parameters.xs("Expert A"   , level="Scenario")
for factor in tornado_factors:
    scenario_new = factor
    design_new = design_2015_actual.copy()
    design_new["Scenario"] = scenario_new
    designs.designs = designs.designs.append(design_new.reset_index().set_index(["Technology", "Scenario", "Variable", "Index"]))
    parameter_new = pd.concat([
        parameter_2015_actual[parameter_2015_actual["Notes"] != factor],
        parameter_expert_a   [parameter_expert_a   ["Notes"] == factor],
    ])
    parameter_new["Scenario"] = factor
    designs.parameters = designs.parameters.append(parameter_new.reset_index().set_index(["Technology", "Scenario", "Parameter"]))


# #### Recompile the design.

# In[17]:


designs.compile()


# #### Compute the results.

# In[18]:


scenario_results = designs.evaluate_scenarios(sample_count=500)
scenario_results.shape


# #### Make the tornado plot.

# In[19]:


tornado_results = scenario_results[["Value"]].xs(
    "LCOE", level="Index"
).rename(
    columns={"Value" : "LCOE [$/kWh]"}
).reset_index(
    ["Technology", "Sample", "Variable"], drop=True
).groupby("Scenario").agg(np.min).drop(["2015 Actual", "Expert A", "Expert B", "Expert C"])
tornado_results["LCOE Reduction[%]"] = 1 - tornado_results["LCOE [$/kWh]"] / base_lcoe
tornado_results[["LCOE Reduction[%]"]].sort_values("LCOE Reduction[%]", ascending=True).plot.barh()


# #### Look at the uncertainties.

# In[20]:


sb.boxplot(
    data = scenario_results[["Value"]].xs(
        "LCOE", level="Index"
    ).rename(
        columns={"Value" : "LCOE [$/kWh]"}
    ).reset_index(
        ["Technology", "Sample", "Variable"], drop=True
    ).drop(["2015 Actual", "Expert A", "Expert B", "Expert C"]).reset_index().sort_values("LCOE [$/kWh]"),
    x = "Scenario",
    y = "LCOE [$/kWh]"
)

