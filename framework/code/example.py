#!/usr/bin/env python
# coding: utf-8

# # Tyche Example

# ## Set up.


# ### Import packages.

# In[1]:


import numpy             as np
import matplotlib.pyplot as pl
import pandas            as pd
import re                as re

# The `tyche` package is located at <https://github.com/NREL/portfolio/tree/master/production-function/framework/code/tyche/>.
import tyche             as ty


# ## Load data.

# ### The data are stored in a set of tab-separated value files in a folder.

# In[2]:


scenarios = ty.Designs("../data")


# ### Compile the production and metric functions for each technology in the dataset.

# In[3]:


scenarios.compile()


# ## Examine the data.

# ### The `functions` table specifies where the Python code for each technology resides.

# In[4]:


scenarios.functions


# ### The `indices` table defines the subscripts for variables.

# In[5]:


scenarios.indices


# ### The `designs` table contains the cost, input, efficiency, and price data for a scenario.

# In[6]:


scenarios.designs


# ### The `parameters` table contains additional techno-economic parameters for each technology.

# In[7]:


scenarios.parameters


# ### The `results` table specifies the units of measure for results of computations.

# In[8]:


scenarios.results


# ## Evaluate the designs in the dataset.

# In[9]:


results = scenarios.evaluate_all()


# In[10]:


results


# ## Sensitity analysis.

# ### Vary the four efficiencies in the design.

# In[11]:


# Four variables are involved.
variables = [
    ("Input efficiency" , "Water"      ),
    ("Input efficiency" , "Electricity"),
    ("Output efficiency", "Oxygen"     ),
    ("Output efficiency", "Hydrogen"   ),
]


# In[12]:


# Let efficiencies range from 0.75 to 0.975.
efficiencies = np.arange(0.750, 1.000, 0.025)
efficiencies


# ### Start from the base case.

# In[13]:


base_design = scenarios.designs.xs("Base", level=1, drop_level=False)
base_design


# In[14]:


base_parameters = scenarios.parameters.xs("Base", level=1, drop_level=False)
base_parameters


# ### Generate the new scenarios and append them to the previous ones.

# In[15]:


# Iterate over variables and efficiencies.
for variable, index in variables:
    for efficiency in efficiencies:

        # Name the scenario.
        scenario = "Let " + variable + " @ " + index + " = " + str(round(efficiency, 3))
        
        # Alter the base case.
        vary_design = base_design.rename(index={"Base" : scenario}, level=1)
        vary_design.loc[("Simple electrolysis", scenario, variable, index), "Value"] = efficiency
        
        # Keep the parameters the same.
        vary_parameters = base_parameters.rename(index={"Base" : scenario}, level=1)
        
        # Append the results to the existing table of scenarios.
        scenarios.designs = scenarios.designs.append(vary_design)
        scenarios.parameters = scenarios.parameters.append(vary_parameters)


# #### See how many rows there are in the tables now.

# In[16]:


scenarios.designs.shape


# In[17]:


scenarios.parameters.shape


# ### Compute the results.

# In[18]:


results = scenarios.evaluate_all()
results


# ### Plot the cost results.

# In[19]:


cost_results = results.xs("Cost", level=3).reset_index()[["Scenario", "Value"]].iloc[2:]


# In[20]:


cost_results["Variable"  ] = cost_results["Scenario"].apply(lambda x: re.sub(r'^Let (.*) @ (.*) =.*$', '\\1[\\2]', x))
cost_results["Efficiency"] = cost_results["Scenario"].apply(lambda x: float(re.sub(r'^.*= (.*)$', '\\1', x)))
cost_results["Cost [USD/mole]"] = cost_results["Value"]


# In[21]:


cost_results = cost_results[["Variable", "Efficiency", "Cost [USD/mole]"]]
cost_results[1:10]


# In[22]:


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

