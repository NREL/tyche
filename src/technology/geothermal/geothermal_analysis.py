#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geothermal model analysis

@author: aayad
"""
#%%
import os
import sys
sys.path.insert(0, os.path.abspath("../../../src"))
import numpy             as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas            as pd
import seaborn           as sb
import tyche             as ty
from pathlib import Path
from tyche.Designs       import sampler

# set paths
cur_dir =  Path(__file__).parent.absolute()
technology_dir = cur_dir.parent
src_dir = technology_dir.parent
atb_dir = os.path.join(src_dir, 'atb')


#%% Set global inputs
ATB_dir = "/Users/aayad/Work/repos/ATB-calc"
technology_name = "Geothermal"

atb_filename = 'geo_atb_2025.csv'
ATB_display_name = "Geothermal - Hydro / Flash"
scenario = "Moderate"
year = 2023
CRPYears = 20
TaxCreditCase = "None"
case = "R&D"

#%% Create ATB data model
atb_geo_input = {
              'tech_name': technology_name,
              'tech_filename': atb_filename,
              'output_path': cur_dir,
              'ATB-calc_dir': ATB_dir,
              'Case': case,
              'TaxCreditCase': TaxCreditCase,
              'CRPYears': CRPYears,
              'Technology': technology_name,
              'DisplayName': ATB_display_name,
              'Scenario': scenario,
              'variable': year
              }
# geo_atb = ty.ATB(path = cur_dir,
#              tech_name = technology_name.lower(),
#              tech_filename = atb_filename,
#              output_path = cur_dir,
#              parameters = geo_parameters)
#%%
geo_design = ty.Designs(
    path = '.',
    name = f'{technology_name.lower()}.xlsx', 
    atb_input = atb_geo_input
)

geo_investments = ty.Investments(
    path = '.',
    name = f'{technology_name.lower()}.xlsx'
)

geo_design.compile()


#%%

# Designs.evaluate

technology = 'geohydro'
sample_count = 10000
f_capital    = geo_design.compiled_functions[technology].capital
f_fixed      = geo_design.compiled_functions[technology].fixed        
f_production = geo_design.compiled_functions[technology].production
f_metrics    = geo_design.compiled_functions[technology].metric

indices = geo_design.vectorize_indices(technology)
tranches = geo_design.vectorize_tranches(technology)
n = tranches.shape[0]

design    = geo_design.vectorize_designs(technology, n, sample_count)
parameter = geo_design.vectorize_parameters(technology, n, sample_count)

capital_cost = f_capital(design.scale, parameter, geo_design.ATB)
fixed_cost   = f_fixed  (design.scale, parameter, geo_design.ATB)

input_raw = design.input
input = design.input_efficiency * input_raw

output_raw = f_production(design.scale, capital_cost,
                          design.lifetime, fixed_cost,
                          input, parameter, geo_design.ATB)

output = design.output_efficiency * output_raw

cost = np.sum(capital_cost / design.lifetime, axis=0) / design.scale + \
       np.sum(fixed_cost, axis=0) / design.scale +                     \
       np.sum(design.input_price  * input , axis=0) -                  \
       np.sum(design.output_price * output, axis=0)

metric = f_metrics(design.scale, capital_cost, design.lifetime,
                   fixed_cost, input_raw, input, design.input_price,
                   output_raw, output, cost, parameter, geo_design.ATB)

def organize(df, ix):
  ix1 = pd.MultiIndex.from_product(
    [ix, tranches, range(1, sample_count + 1)],
    names=["Index", "Tranche", "Sample"]
  )
  df1 = pd.DataFrame({"Value" : df.flatten()}, index=ix1)
  df1["Technology"] = technology
  return df1.set_index(
    ["Technology"],
    append=True
  ).reorder_levels(
    ["Technology", "Tranche", "Sample", "Index"]
  ).sort_index()

res_cost   = organize(cost.reshape(cost.shape + (1,)), ["Cost"]      )
res_output = organize(output                         , indices.output)
res_metric = organize(metric                         , indices.metric)

#%%
tranche_results = geo_investments.evaluate_tranches(geo_design, 
                                                    sample_count=sample_count).metrics
tranche_results.xs(1, level="Sample", drop_level=False)

#%%
# g = sb.boxenplot(
#     x="Tranche",
#     y="Value",
#     hue="Technology",
#     data=tranche_results.xs(
#         "LCOE",
#         level="Index"
#     ).reset_index(
#     )[["Technology", "Category", "Tranche", "Value"]],
#     order=[
#         "Baseline_conservative",
#         "Sensitivity_conservative",
#         "Baseline_moderate",
#         "Sensitivity_moderate",
#         "Baseline_advanced",
#         "Sensitivity_advanced",                           
#         ]
#     )
# g.set(ylabel="LCOE",
#      ylim=(0,10000)
#      )
# g.set_xticklabels(g.get_xticklabels(), rotation=30, ha='right', rotation_mode='anchor')

#%%
g = sb.boxenplot(
    x="Tranche",
    y="Value",
    hue="Technology",
    data=tranche_results.xs(
        "OCC",
        level="Index"
    ).reset_index(
    )[["Technology", "Category", "Tranche", "Value"]],
    order=[
        "Baseline_conservative",
        "Sensitivity_conservative",
        "Baseline_moderate",
        "Sensitivity_moderate",
        "Baseline_advanced",
        "Sensitivity_advanced",                
        ]
    )
g.set(ylabel="Overnight capital cost (1000$/ MW)",
     # ylim=(400,1400)
     )
g.set_xticklabels(g.get_xticklabels(), rotation=30, ha='right', rotation_mode='anchor')


#==============================================================================================
file_dir = "/Users/aayad/Work/repos/tyche/src/technology/geothermal"


tech_name = "geo"
ATB_year = "2025"
ATB_scenario = "advanced"
tech = "geohydro"
tech_class_column = "Geo class"

file_name = f"{tech_name}_ATB_{ATB_year}_{ATB_scenario}.csv"
file_path = os.path.join(file_dir, file_name)

df = pd.read_csv(file_path)
df = df[df.Tech==tech]

def plot_df(df, atb_metric, tyche_metric, tech, st_year, end_year):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    linestyle = "solid"
    
    tech_classes = df[tech_class_column].unique()
    
    y_lim = (0, 18000)

    c = np.arange(1, len(tech_classes) + 1) * 0.4
    norm = mpl.colors.Normalize(vmin=c.min(), vmax=c.max())
    cmap = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.Blues)
    cmap.set_array([])

    for idx, tech_class in enumerate(tech_classes):
        df_class = df[df[tech_class_column]==tech_class]    
        df_class = df_class[(df_class.Year >=st_year) & (df_class.Year <=end_year)]
        df_depth = df_class["Depth"].unique()[0]
        ax1.plot(df_class['Year'],
                df_class[atb_metric],
                c=cmap.to_rgba(idx + 1),
                markersize = 4,
                # markevery = 10,
                # marker = marker,
                linestyle = linestyle,
                # color = colors[y_idx],
                label = f"{tech_class}-{df_depth}")
                
    ax1.set_ylabel(f"{atb_metric}")
    ax1.set_xlabel("Year")
    # ax.set_yscale('log')
    # plt.xlim(-10, 1000)
    # ax1.set_ylim(y_lim)
    ax1.set_title(f"{tech_name}-ATB_{ATB_year}-{ATB_scenario}")
    # plt.grid(True)
    ax1.legend(ncol=5, markerscale=0.1, fontsize=7)
    
    
    sb.boxenplot(
        x="Tranche",
        y="Value",
        hue="Technology",
        ax = ax2,
        data=tranche_results.xs(
            tyche_metric,
            level="Index"
        ).reset_index(
        )[["Technology", "Category", "Tranche", "Value"]],
        order=[
            "Baseline_conservative",
            "Sensitivity_conservative",
            "Baseline_moderate",
            "Sensitivity_moderate",
            "Baseline_advanced",
            "Sensitivity_advanced",                
            ]
        )
    ax2.set(ylabel="Overnight capital cost (1000$/ MW)",
         ylim=y_lim
         )
    ax2.set_xticklabels(g.get_xticklabels(), rotation=30, ha='right', rotation_mode='anchor')
    ax2.set_title(f"Tyche-{technology_name}-{technology}")
    # # ax2.legend(ncol=5, markerscale=0.1, fontsize=7)
    legend = ax2.legend(loc = 'upper right')
    # legend.set_visible(False) # Hide the legend

    plt.show()

atb_metric = "Cap cost 1000$/MW"
tyche_metric = "OCC"
st_year = 2025
end_year = 2050
plot_df(df, atb_metric, tyche_metric, tech, st_year, end_year)



