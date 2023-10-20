import os
import sys
sys.path.insert(0, os.path.abspath("../"))
import numpy             as np
import matplotlib.pyplot as pl
import pandas            as pd
import seaborn           as sb
import tyche             as ty


def path_change(data_to_tyche,path):
    
    """
    Changes the working directory to the technology case study under study.
    not doing this results in issues while running Tyche and can be resolved later. 

    Parameters
    ----------
    data_to_tyche: dictionary
        information obtained from the GUI
        
    path: str
        path to the technology case under study

    Returns
    -------

    """

    path2 = path + data_to_tyche['name']+"/"
    os.chdir(path2)

def evaluate_without_slider_input(data_to_tyche,path,sample_count=100):
    
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

    path_change(data_to_tyche,path)
    my_designs = ty.Designs(path = ".",
                        name = 'pv-residential-simple.xlsx')
    
    my_designs.compile()

    investments = ty.Investments(path = '.',name = 'pv-residential-simple.xlsx')
    
    tranche_results = investments.evaluate_tranches(my_designs, sample_count=sample_count)
    
    results_to_gui = {}
    results_to_gui['id'] = data_to_tyche['id']
    results_to_gui['results'] = {}

    res = tranche_results.metrics.reset_index()
    metrics_list = list(pd.unique(res['Index']))
    categories_list = list(pd.unique(res['Category']))
 
    for c in categories_list:
        df_c = res[res['Category'] == c]
        try:
            results_to_gui['results'][c]
        except:
            results_to_gui['results'][c] = {}
    
        for m in metrics_list:
            df_m = df_c[df_c['Index'] == m]
            try:
                results_to_gui['results'][c][m]
            except:
                results_to_gui['results'][c][m] = {}
            results_to_gui['results'][c][m]=list(df_m['Value'])
    
    return results_to_gui



def evaluate_with_slider_input(data_to_tyche,path,sample_count=100):
    
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
    
    #Creating Dataframe        
    #Here all we need to do is point to the correct Tyche technology, create the evaluator and run the evaluator with the dataframe with
    #category names in one column the investments in another

    investment = []
    name = []
    for st in data_to_tyche['states']['category_states']:
        name.append(st['name'])
        investment.append(st['investment'])

    
    investment_df = pd.DataFrame()
    investment_df['Amount'] = investment
    investment_df['Category'] = name
    investment_df = investment_df.set_index('Category')
    investment_impact = evaluator.evaluate(investment_df)
    

    results_to_gui = {}
    results_to_gui['id'] = data_to_tyche['id']
    results_to_gui['results'] = {}
    res = investment_impact.reset_index()
    metrics_list = list(pd.unique(res['Index']))
    categories_list = list(pd.unique(res['Category']))
    
    
    for c in categories_list:
        df_c = res[res['Category'] == c]
        try:
            results_to_gui['results'][c]
        except:
            results_to_gui['results'][c] = {}
        for m in metrics_list:
            df_m = df_c[df_c['Index'] == m]
            try:
                results_to_gui['results'][c][m]
            except:
                results_to_gui['results'][c][m] = {}
            a = []
            for n in  list(df_m['Value']):
                a.append(float(n))
            results_to_gui['results'][c][m]=a
            
            
    return results_to_gui
    