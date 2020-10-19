#!/usr/bin/env python
# coding: utf-8

# # Multiple Objectives for Residential PV

# ## Set up.

# ### Import packages.

# In[1]:


import os
import sys
sys.path.insert(0, os.path.abspath(".."))


# In[2]:


import numpy             as np
import matplotlib.pyplot as pl
import pandas            as pd
import seaborn           as sb
import tyche             as ty


# ## Load data.

# ### The data are stored in a set of tab-separated value files in a folder.

# In[3]:


designs = ty.Designs("../../data/residential_pv_multiobjective")


# In[4]:


investments = ty.Investments("../../data/residential_pv_multiobjective")


# ### Compile the production and metric functions for each technology in the dataset.

# In[5]:


designs.compile()


# ## Multi-objective decision analysis.

# ### Compute costs and metrics for tranches.

# Tranches are atomic units for building investment portfolios. Evaluate all of the tranches, so we can assemble them into investments (portfolios).

# In[6]:


tranche_results = investments.evaluate_tranches(designs, sample_count=50)


# ### Fit a response surface to the results.

# The response surface interpolates between the discrete set of cases provided in the expert elicitation. This allows us to study funding levels intermediate between those scenarios.

# In[7]:


evaluator = ty.Evaluator(investments.tranches, tranche_results.summary)


# Here are the categories of investment and the maximum amount that could be invested in each:

# In[8]:


evaluator.max_amount


# Here are the metrics and their units of measure:

# In[9]:


evaluator.units


# #### Example interpolation.

# Let's evaluate the case where each category is invested in at half of its maximum amount.

# In[10]:


example_investments = evaluator.max_amount / 2
example_investments


# In[11]:


evaluation = evaluator.evaluate(example_investments)
evaluation


# In[12]:


evaluator.units.loc["GHG"]


# In[13]:


summary = evaluation.xs("GHG", level = "Index")
values = summary.xs("Module R&D", level = "Category")
plt = sb.boxplot(y = values)
y0 = min(0, evaluator.min_metric.loc["GHG"][0])
y1 = max(0, evaluator.max_metric.loc["GHG"][0])
dy = (y1 - y0) / 20
plt.set(
  xlabel = "Module R&D",
  ylabel = "GHG [" + evaluator.units.loc["GHG"].values[0] + "]",
  ylim = (y0 - dy, y1 + dy),
);


# Let's evaluate the mean instead of outputing the whole distribution.

# In[14]:


evaluator.evaluate_statistic(example_investments, np.mean)


# Here is the standard deviation:

# In[15]:


evaluator.evaluate_statistic(example_investments, np.std)


# A risk-averse decision maker might be interested in the 10% percentile:

# In[16]:


evaluator.evaluate_statistic(example_investments, lambda x: np.quantile(x, 0.1))


# ### ε-Constraint multiobjective optimization

# In[17]:


optimizer = ty.EpsilonConstraintOptimizer(evaluator)


# In order to meaningfully map the decision space, we need to know the maximum values for each of the metrics.

# In[18]:


metric_max = optimizer.max_metrics()
metric_max


# #### Example optimization.

# Limit spending to $3M.

# In[19]:


investment_max = 3e6


# Require that the GHG reduction be at least 40 gCO2e/system and that the Labor wages not decrease.

# In[20]:


metric_min = pd.Series([40, 0], name = "Value", index = ["GHG", "Labor"])
metric_min


# Compute the ε-constrained maximum for the LCOE.

# In[21]:


optimum = optimizer.maximize_slsqp(
    "LCOE"                       ,
    total_amount = investment_max,
    min_metric   = metric_min    ,
    statistic    = np.mean       ,
)
optimum.exit_message


# Here are the optimal spending levels:

# In[22]:


np.round(optimum.amounts)


# Here are the three metrics at that optimum:

# In[23]:


optimum.metrics


# *Thus, by putting all of the investment into Module R&D, we can expected to achieve a mean 3.75 ¢/kWh reduction in LCOE under the GHG and Labor constraints.*

# It turns out that there is no solution for these constraints if we evaluate the 10th percentile of the metrics, for a risk-averse decision maker.

# In[24]:


optimum = optimizer.maximize_slsqp(
    "LCOE"                       ,
    total_amount = investment_max,
    min_metric   = metric_min    ,
    statistic    = lambda x: np.quantile(x, 0.1),
)
optimum.exit_message


# Let's try again, but with a less stringent set of constraints, only constraining GHG somewhat but not Labor at all.

# In[25]:


optimum = optimizer.maximize_slsqp(
    "LCOE"                                                         ,
    total_amount = investment_max                                  ,
    min_metric   = pd.Series([30], name = "Value", index = ["GHG"]),
    statistic    = lambda x: np.quantile(x, 0.1)                   ,
)
optimum.exit_message


# In[26]:


np.round(optimum.amounts)


# In[27]:


optimum.metrics

