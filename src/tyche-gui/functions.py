import server_common

import sys
import os
import json
from pathlib import Path
import logging
import functools
from jsonrpcserver import method, Success
import pandas as pd
import numpy as np

this_script_path = os.path.realpath(__file__)
this_script_dir  = os.path.dirname(this_script_path)
parent_dir       = os.path.abspath(os.path.join(this_script_dir, os.pardir))

sys.path.append(parent_dir)

import tyche as ty

technology_path = Path(os.path.abspath(os.path.join(parent_dir, "technology")))


@functools.lru_cache(maxsize=2)
def fetch_technologies():
    with open(server_common.tech_database_path) as db_file:
        db = json.load(db_file)
        return db["technology_list"]
    
@functools.lru_cache(maxsize=2)
def fetch_tech_uuid_map():
    with open(server_common.tech_database_path) as db_file:
        db = json.load(db_file)
        return db["tech_uuid_to_dir"]


def resolve_categories(selected_tech, category_id_list):
    cid_list = { i["id"]: i for i in selected_tech["category_defs"] }
    return [ cid_list[to_resolve_cid] for to_resolve_cid in category_id_list ]

def resolve_categories_name(selected_tech, category_id_list):
    clist = resolve_categories(selected_tech, category_id_list)
    return [i["name"] for i in clist]

def extract_category_investment(selected_tech, scenario_request):
    rq_list = list(server_common.to_dict(scenario_request.category_states).items())
    names = resolve_categories_name(selected_tech, [i[0] for i in rq_list])
    return (names, [i[1] for i in rq_list])


def resolve_metrics(selected_tech, metric_id_list):
    mid_list = { i["id"]: i for i in selected_tech["metric_defs"] }

    return [ mid_list[to_resolve_mid] for to_resolve_mid in metric_id_list ]

def resolve_metrics_name(selected_tech, metric_id_list):
    clist = resolve_metrics(selected_tech, metric_id_list)
    return [i["name"] for i in clist]

'''
def path_change(data_to_tyche, path):
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
'''

def evaluate_without_slider_input(data_to_tyche,path,selected_tech,sample_count=100):
    """
    Evaluates Tranche impacts

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

    chosen_tech_name = selected_tech['name']

    xls_file = (server_common.technology_path / path)

    my_designs = ty.Designs(path=str(xls_file),
                            name=chosen_tech_name + ".xlsx")

    my_designs.compile()

    investments = ty.Investments(path=str(xls_file), 
                                 name=chosen_tech_name + ".xlsx")

    tranche_results = investments.evaluate_tranches(
        my_designs, sample_count=sample_count)

    results_to_gui = {}
    results_to_gui['id'] = data_to_tyche['id']
    results_to_gui['results'] = {}

    res = tranche_results.metrics.reset_index()

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

    res = res.merge(cat_id_df, on='Category')
    res = res.merge(met_id_df, on='Index')

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
            results_to_gui['results'][c][m] = list(df_m['Value'])

    return results_to_gui

def evaluate_with_slider_input(data_to_tyche, path, selected_tech, sample_count=100):
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
    #path_change(data_to_tyche, path)

    chosen_tech_name = selected_tech['name']

    xls_file = (server_common.technology_path / path)

    my_designs = ty.Designs(path=str(xls_file),
                            name=chosen_tech_name + ".xlsx")

    my_designs.compile()

    investments = ty.Investments(path=str(xls_file), 
                                 name=chosen_tech_name + ".xlsx")

    tranche_results = investments.evaluate_tranches(
        my_designs, sample_count=sample_count)

    evaluator = ty.Evaluator(tranche_results)

    # Creating Dataframe
    # Here all we need to do is point to the correct Tyche technology, create the evaluator and run the evaluator with the dataframe with
    # category names in one column the investments in another

    (name, investment) = extract_category_investment(selected_tech, data_to_tyche)

    logging.debug("Category investment: %s", str(list(zip(name, investment))))

    investment_df = pd.DataFrame()
    investment_df['Amount'] = investment
    investment_df['Category'] = name
    investment_df = investment_df.set_index('Category')
    investment_impact = evaluator.evaluate(investment_df)

    
    res = investment_impact.reset_index()

    cat_df_name = []
    cat_id = []
    cat_id_df = pd.DataFrame()
    for d in selected_tech['category_defs']:
        cat_df_name.append(d['name'])
        cat_id.append(d['id'])

    cat_id_df['Category'] = cat_df_name
    cat_id_df['category_id'] = cat_id

    met_df_name = []
    met_id = []
    met_id_df = pd.DataFrame()
    for d in selected_tech['metric_defs']:
        met_df_name.append(d['name'])
        met_id.append(d['id'])

    met_id_df['Index'] = met_df_name
    met_id_df['metric_id'] = met_id

    res = res.merge(cat_id_df, on='Category')
    res = res.merge(met_id_df, on='Index')

    metrics_list = list(pd.unique(res['metric_id']))
    categories_list = list(pd.unique(res['category_id']))

    sim_results = {}

    for c in categories_list:
        df_c = res[res['category_id'] == c]
        try:
            sim_results[c]
        except:
            sim_results[c] = {}
        for m in metrics_list:
            df_m = df_c[df_c['metric_id'] == m]
            try:
                sim_results[c][m]
            except:
                sim_results[c][m] = {}
            a = []
            for n in list(df_m['Value']):
                a.append(float(n))
            sim_results[c][m] = a

    results_to_gui = {}
    results_to_gui['scenario_id'] = data_to_tyche.scenario_id
    results_to_gui['category_state'] = server_common.to_dict(data_to_tyche.category_states)
    results_to_gui['cells'] = sim_results

    return results_to_gui

@method
def run_scenario(request_definition):
    request_definition = server_common.to_object(request_definition)

    chosen_tech = request_definition.scenario_id

    techs = fetch_technologies()
    tech_id_map = fetch_tech_uuid_map()

    chosen_tech = next(x for x in techs if chosen_tech == x["id"])
    chosen_tech_path = tech_id_map[chosen_tech["id"]]

    logging.debug("Request selected %s", repr(chosen_tech))

    results = evaluate_with_slider_input(request_definition, chosen_tech_path, chosen_tech)

    return Success(results)


@method
def get_scenarios():
    """
    Obtains the list of technology case study present within the tyche technology directory

    Parameters
    ----------

    Returns
    -------
    technology_list: list
        list of technologies within tyche
    """
    return Success(fetch_technologies())

@method
def evaluate_opt(data_to_tyche,path,opt_parameters,selected_tech,sample_count=100):
    
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
    chosen_tech_name = selected_tech['name']

    xls_file = (server_common.technology_path / path)

    my_designs = ty.Designs(path=str(xls_file),
                            name=chosen_tech_name + ".xlsx")

    my_designs.compile()

    investments = ty.Investments(path=str(xls_file), 
                                 name=chosen_tech_name + ".xlsx")

    tranche_results = investments.evaluate_tranches(
        my_designs, sample_count=sample_count)

    evaluator = ty.Evaluator(tranche_results)
    

    optimizer = ty.EpsilonConstraintOptimizer(evaluator)

        # Creating Dataframe
    # Here all we need to do is point to the correct Tyche technology, create the evaluator and run the evaluator with the dataframe with
    # category names in one column the investments in another

    (name, investment) = extract_category_investment(selected_tech, data_to_tyche)

    logging.debug("Category investment: %s", str(list(zip(name, investment))))
    

    if opt_parameters['statistic'] == "np.mean":
            opt_parameters['statistic'] = np.mean

    optimum = optimizer.opt_slsqp(
        metric = opt_parameters['optimized_metric'],                      
        sense = opt_parameters['optimization_sense'],
        max_amount = opt_parameters['max_amount'],
        total_amount = opt_parameters['investment_max'],
        eps_metric = opt_parameters['metric_df'],
        statistic    = opt_parameters['statistic'],
        initial =  opt_parameters['initial'] ,
        tol = opt_parameters['tol'],
        maxiter = opt_parameters['maxiter'],
        verbose = opt_parameters['verbose']
        )



    sim_results = {}

    cat_df_name = []
    cat_id = []
    cat_id_df = pd.DataFrame()
    for d in selected_tech['category_defs']:
        cat_df_name.append(d['name'])
        cat_id.append(d['id'])

    cat_id_df['Category'] = cat_df_name
    cat_id_df['category_id'] = cat_id

    met_df_name = []
    met_id = []
    met_id_df = pd.DataFrame()
    for d in selected_tech['metric_defs']:
        met_df_name.append(d['name'])
        met_id.append(d['id'])

    met_id_df['Index'] = met_df_name
    met_id_df['metric_id'] = met_id

    res_inv_df=optimum.amounts.to_frame()
    res_metric_df=optimum.metrics.to_frame()
    
    
    res_inv_df = res_inv_df.merge(cat_id_df,on='Category')
    res_metric_df = res_metric_df.merge(met_id_df,on='Index')
    
 
    metrics_list = list(pd.unique(res_metric_df['metric_id']))
    categories_list = list(pd.unique(res_inv_df['category_id']))
    
    sim_results['investments'] = {}
    sim_results['metrics'] = {}
    
    
    for c in categories_list:
        df_c = res_inv_df[res_inv_df['category_id'] == c].reset_index()
        if len(df_c) == 1:
            sim_results['investments'][c]=df_c['Amount'][0]
        else:
            print('Warning::Issue with results compilation. recheck')

            
            
    for m in metrics_list:
        df_m = res_metric_df[res_metric_df['metric_id'] == m].reset_index()
        if len(df_m) == 1:
            sim_results['metrics'][m]=df_m['Value'][0]
        else:
            print('Warning::Issue with results compilation. recheck')
    
    results_to_gui = {}
    results_to_gui['scenario_id'] = data_to_tyche.scenario_id
    results_to_gui['category_state'] = server_common.to_dict(data_to_tyche.category_states)
    results_to_gui['cells'] = sim_results      
            
    return results_to_gui


@method
def run_optimization(request_definition,opt_parameters):
    request_definition = server_common.to_object(request_definition)

    chosen_tech = request_definition.scenario_id

    techs = fetch_technologies()
    tech_id_map = fetch_tech_uuid_map()

    chosen_tech = next(x for x in techs if chosen_tech == x["id"])
    chosen_tech_path = tech_id_map[chosen_tech["id"]]

    logging.debug("Request selected %s", repr(chosen_tech))

    results = evaluate_opt(request_definition,chosen_tech_path,opt_parameters,chosen_tech,sample_count=100)

    return Success(results)
