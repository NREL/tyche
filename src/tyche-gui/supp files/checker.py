import os
import sys
sys.path.insert(0, os.path.abspath("../"))
import numpy             as np
import matplotlib.pyplot as pl
import pandas            as pd
import seaborn           as sb
import tyche             as ty

        
def evaluate_opt(data_to_tyche,path,sample_count=100):
    
    """
    Evaluates investment impcats

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
    evaluator: Evaluator object from Tyche
        Evaluator object can be extracted to get investment results data

    """
    path_change(data_to_tyche,path)

    my_designs = ty.Designs(path = ".",
                        name = 'pv-residential-simple.xlsx')
    
    my_designs.compile()

    investments = ty.Investments(path = '.',name = 'pv-residential-simple.xlsx')
    
    tranche_results = investments.evaluate_tranches(my_designs, sample_count=sample_count)
    
    evaluator = ty.Evaluator(tranche_results)
    
    return evaluator



evaluator = evaluate_opt(data_to_tyche,path,sample_count=100)


'''
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


metrics_list = list(pd.unique(res['metric_id']))
categories_list = list(pd.unique(res['category_id']))


for c in categories_list:
    df_c = res[res['category_id'] == c]
    try:
        results_to_gui['results'][c]
    except:
        results_to_gui['results'][c] = {}
    for m in metrics_list:
        df_m = df_c[df_c['metric_id'] == m]
        try:
            results_to_gui['results'][c][m]
        except:
            results_to_gui['results'][c][m] = {}
        a = []
        for n in  list(df_m['Value']):
            a.append(float(n))
        results_to_gui['results'][c][m]=a
        
        
return results_to_gui
'''


metric_df = {}
metric_df['GHG'] = {}
metric_df['Labor'] = {}
metric_df['GHG']['limit'] = 30
metric_df['GHG']['sense'] = 'upper'
metric_df['Labor']['limit'] = 0
metric_df['Labor']['sense'] = 'lower' 
optimizer = ty.EpsilonConstraintOptimizer(evaluator)
investment_max = 3e6
optimum = optimizer.opt_slsqp(
    "LCOE"                          
)
print(optimum.exit_message)
print(optimum.amounts)
    