#!/usr/bin/env python
# coding: utf-8

# Created 4/13 by Rebecca Hanes as copy of example.py in same directory
# Altered to run biorefinery example instead of simple electrolysis

# # Tyche Biorefinery Example

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

# The `tyche` package is located at <https://github.com/NREL/portfolio/tree/master/production-function/framework/src/tyche/>.
import tyche             as ty


# ## Load data.

# ### The data are stored in a set of tab-separated value files in a folder.

# In[3]:


scenarios = ty.Designs("data/biorefinery")


# ### Compile the production and metric functions for each technology in the dataset.

# In[4]:


scenarios.compile()


# ## Examine the data.

# ### The `functions` table specifies where the Python code for each technology resides.

# In[5]:


scenarios.functions


# ### The `indices` table defines the subscripts for variables.

# In[6]:


scenarios.indices


# ### The `designs` table contains the cost, input, efficiency, and price data for a scenario.

# In[7]:


scenarios.designs


# ### The `parameters` table contains additional techno-economic parameters for each technology.

# In[8]:


scenarios.parameters


# ### The `results` table specifies the units of measure for results of computations.

# In[9]:


scenarios.results


# ## Evaluate the designs in the dataset.

# In[10]:


results = scenarios.evaluate_scenarios()


# In[11]:


results

