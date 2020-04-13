#!/usr/bin/env python
# coding: utf-8

# Created 4/13 by Rebecca Hanes as copy of example.py in same directory
# Altered to run biorefinery example instead of simple electrolysis

# # Tyche Biorefinery Example

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

scenarios = ty.Designs("../data-biorefinery")

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

