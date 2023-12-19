import server_common

import sys
import os
import json
from pathlib import Path
import logging
import functools
from jsonrpcserver import method, Success, Error
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

def category_name_to_id(selected_tech, name):
    for cat in selected_tech['category_defs']:
        if cat["name"] == name:
            return cat["id"]

    raise Exception("Unknown category for this tech")

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
    results_to_gui['category_states'] = {
        cat_id : cat_val
        for cat_id, cat_val in server_common.to_dict(data_to_tyche.category_states).items()
    }

    results_to_gui['cells'] = sim_results

    return results_to_gui

@method
def run_scenario(request_definition):
    print("SIM", request_definition)
    request_definition = server_common.to_object(request_definition)

    chosen_tech = request_definition.scenario_id

    techs = fetch_technologies()
    tech_id_map = fetch_tech_uuid_map()

    chosen_tech = next(x for x in techs if chosen_tech == x["id"])
    chosen_tech_path = tech_id_map[chosen_tech["id"]]

    logging.debug("Request selected %s", repr(chosen_tech))

    results = evaluate_with_slider_input(request_definition, chosen_tech_path, chosen_tech)

    print("SIM RESULT", results)

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


def build_evaluator(path, chosen_tech_name, sample_count):
    xls_file = (server_common.technology_path / path)

    my_designs = ty.Designs(path=str(xls_file),
                            name=chosen_tech_name + ".xlsx")

    my_designs.compile()

    investments = ty.Investments(path=str(xls_file),
                                 name=chosen_tech_name + ".xlsx")

    tranche_results = investments.evaluate_tranches(
        my_designs, sample_count=sample_count)

    return ty.Evaluator(tranche_results)

def evaluate_opt(path,request_definition, opt_parameters, selected_tech,sample_count=100):

    category_optimization_limits = {}

    if hasattr(request_definition, "category_states"):
        category_optimization_limits = {
            cat['category_id'] : cat['value']
            for cat in server_common.to_dict(request_definition.category_states)
        }

    chosen_tech_name = selected_tech['name']

    evaluator = build_evaluator(path, chosen_tech_name, sample_count)
    
    optimizer = ty.EpsilonConstraintOptimizer(evaluator)

    print("Optimization params:", opt_parameters)

    optimum = optimizer.opt_slsqp(**opt_parameters)

    print(optimum)
    print(optimum.metrics)

    if optimum.exit_code != 0:
        raise Exception(optimum.exit_message)

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
    
    category_state = {}
    metric_state = {}
    
    
    for c in categories_list:
        df_c = res_inv_df[res_inv_df['category_id'] == c].reset_index()
        if len(df_c) == 1:
            category_state[c]= {
                "value" : df_c['Amount'][0]
            }

            print("CHECK", c, category_optimization_limits)

            if c in category_optimization_limits:
                category_state[c]["limit"] = category_optimization_limits[c]
        else:
            print('Warning::Issue with results compilation. recheck')

            
            
    for m in metrics_list:
        df_m = res_metric_df[res_metric_df['metric_id'] == m].reset_index()
        if len(df_m) == 1:
            metric_state[m]=df_m['Value'][0]
        else:
            print('Warning::Issue with results compilation. recheck')

    #print("DFM", df_m)
    #print("DFC", df_c)
    #print(sim_results)

    print(metric_state, request_definition.metric_states)
    
    results_to_gui = {}
    results_to_gui['scenario_id'] = selected_tech["id"]
    results_to_gui['category_limits'] = category_state
    results_to_gui['metric_limits'] = {
        opt_id : {
            'limit' : 0,
            'sense' : "min",
            'value' : opt_val,
        }
        for opt_id, opt_val in metric_state.items()
    }
    #results_to_gui['category_state'] = server_common.to_dict(data_to_tyche.category_states)
    #results_to_gui['cells'] = sim_results
    results_to_gui["opt_metric_id"] = request_definition.metric_target
            
    return results_to_gui

def metric_to_name(chosen_tech, metric_id):
    for mt in chosen_tech["metric_defs"]:
        if mt["id"] == metric_id:
            return mt["name"]
    raise Exception("Unknown metric")

@method
def optimize_scenario(request_definition):
    logging.debug("optimization request: %s", repr(request_definition))
    request_definition = server_common.to_object(request_definition)

    chosen_tech = request_definition.scenario_id

    techs = fetch_technologies()
    tech_id_map = fetch_tech_uuid_map()

    chosen_tech = next(x for x in techs if chosen_tech == x["id"])
    chosen_tech_path = tech_id_map[chosen_tech["id"]]

    logging.debug("Request selected %s", repr(chosen_tech))

    try:
        metric_target = metric_to_name(chosen_tech, request_definition.metric_target)
    except:
        metric_target = chosen_tech['metric_defs'][0]['name']

    # set up metric limits

    metric_df = {}

    for mt in request_definition.metric_states:
        metric_df[metric_to_name(chosen_tech, mt.metric_id)] = {
            "limit" : mt.value,
            "sense" : mt.bound_type
        }

    if len(metric_df) == 0:
        metric_df = None

    # set up sim sense
    sense = None

    try:
        #sanitize
        if request_definition.optimize_sense in ["min", "max"]:
            sense = request_definition.optimize_sense
    except:
        pass

    # set up total amount
    total_amount = request_definition.portfolio

    if total_amount <= 0.0:
        total_amount = None

    # set up category limits

    max_amounts = []

    # this is a bit ugly, as we need an evaluator to get category orders
    evaluator = build_evaluator(chosen_tech_path, chosen_tech["name"], 100)
    cat_order = evaluator.max_amount.index.tolist()

    for cat in cat_order:
        # we have a name, turn it into an id
        cat = category_name_to_id(chosen_tech, cat)
        print("Linked", cat)

        found = False

        # get the id from the request
        for req_cat in server_common.to_dict(request_definition.category_states):
            if req_cat["category_id"] == cat:
                max_amounts.append(max(req_cat["value"], 0.0000001))
                print(f"setting max for {cat} to {max_amounts[-1]}")
                found = True
                break

        if not found:
            # set an approx bound
            if total_amount is not None:
                max_amounts.append(total_amount)
            else:
                #unknown bound, just make it sky high
                max_amounts.append(100E6)

    if len(max_amounts) == 0:
        max_amounts = None
    else:
       max_amounts = pd.Series(max_amounts,
            index = evaluator.max_amount.index.tolist()
            )


    # wrap it all up
    param = {
        'metric' : metric_target,
        'sense' : sense,
        'max_amount' : max_amounts,
        'total_amount' : request_definition.portfolio,
        'eps_metric' : metric_df,
        'statistic' : np.mean,
        'initial' : None,
        'maxiter' : 50
    }

    try:
        opt_results = evaluate_opt(chosen_tech_path, request_definition, param, chosen_tech)
    except Exception as e:
        if hasattr(e, "message"):
            return Error(1, e.message)
        else:
            raise

    print("OPT_RESULTS", opt_results)


    return Success(opt_results)

