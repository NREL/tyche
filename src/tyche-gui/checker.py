import os
import sys
sys.path.insert(0, os.path.abspath("../"))
import numpy             as np
import matplotlib.pyplot as pl
import pandas            as pd
import seaborn           as sb
import tyche             as ty
def evaluate_without_slider_input(sample_count=100):
    
    """
    Evaluates Tranche impcats

    Parameters
    ----------
    data_to_tyche: dictionary
        information obtained from the GUI
        
    path: str
        path to the technology case under study
        
    sample_count: int
         number of samples for calculation

    Returns
    -------
    tranche_results: DataFrame
        tranche evaluation results for plotting

    """

    os.chdir("/Users/tghosh/Library/CloudStorage/OneDrive-NREL/work_NREL/tyche/src/technology/pv-residential-simple/")

    my_designs = ty.Designs(path = ".",
                        name = 'pv-residential-simple.xlsx')
    
    my_designs.compile()

    investments = ty.Investments(path = '.',name = 'pv-residential-simple.xlsx')
    
    tranche_results = investments.evaluate_tranches(my_designs, sample_count=sample_count)
    
    results_to_gui = {}
    results_to_gui['id'] = data_to_tyche['id']
    results_to_gui['results'] = {}

    res = tranche_results.metrics.reset_index()
    return res
    
    
    
res=evaluate_without_slider_input(sample_count=100).reset_index()

#
cat_df_name = []
cat_id = []
cat_id_df = pd.DataFrame()
for d in data_to_tyche['category_defs']:
    cat_df_name.append(d['name'])
    cat_id.append(d['id'])

cat_id_df['Category'] = cat_df_name
cat_id_df['category_id'] = cat_id

met_df_name = []
met_id = []
met_id_df = pd.DataFrame()
for d in data_to_tyche['metric_defs']:
    met_df_name.append(d['name'])
    met_id.append(d['id'])

met_id_df['Index'] = met_df_name
met_id_df['metric_id'] = met_id


res = res.merge(cat_id_df,on='Category')
res = res.merge(met_id_df,on='Index')

results_to_gui = {}

metrics_list = list(pd.unique(res['metric_id']))
categories_list = list(pd.unique(res['category_id']))





for c in categories_list:
    df_c = res[res['category_id'] == c]
    try:
        results_to_gui[c]
    except:
        results_to_gui[c] = {}
    for m in metrics_list:
        df_m = df_c[df_c['metric_id'] == m]
        try:
            results_to_gui[c][m]
        except:
            results_to_gui[c][m] = {}
        a = []
        for n in  list(df_m['Value']):
            a.append(float(n))
        results_to_gui[c][m]=a
        
        
    
    
    