import sys
import os
import uuid
from pathlib import Path
import logging
import functools
from jsonrpcserver import method, Success
import pandas as pd

this_script_path = os.path.realpath(__file__)
this_script_dir  = os.path.dirname(this_script_path)
parent_dir       = os.path.abspath(os.path.join(this_script_dir, os.pardir))

sys.path.append(parent_dir)

import tyche as ty

technology_path = Path(os.path.abspath(os.path.join(parent_dir, "technology")))

os.chdir('./')

def get_categories(tech_source):
    """
    Obtains the categories within a technology

    Parameters
    ----------
    technology name : str
        Name of the technology        
    Returns
    -------
    category_list: list
        list of categories within a technology
    """

    datafile = pd.read_excel(tech_source, sheet_name="tranches")
    categories = list(pd.unique(datafile['Category']))
    category_list = []
    for c in categories:
        d = datafile[datafile['Category'] == c]
        category = {
            'name': c,
            'description': str(pd.unique(d['Notes'])[0]),
            'starting_investment': min(d['Amount']),
            'max_investment': max(d['Amount']),
            'id': str(uuid.uuid4())
        }
        category_list.append(category)
    return category_list


def get_metrics(tech_source):
    """
    Obtains the metrics within a technology case study

    Parameters
    ----------
    technology name : str
        Name of the technology

    Returns
    -------
    metric_list: list
        list of metrics within a technology
    """

    datafile = pd.read_excel(tech_source, sheet_name="results")
    d_metrics = datafile[datafile['Variable'] == 'Metric']

    metrics = list(pd.unique(d_metrics['Index']))
    metric_list = []
    for m in metrics:
        d = d_metrics[d_metrics['Index'] == m]
        metric = {
            'name': m,
            'description': str(pd.unique(d['Notes'])[0]),
            'id': str(uuid.uuid4())
        }
        metric_list.append(metric)
    return metric_list


def create_technology(technology_name):
    """
    Creates a dictionary for the technologies

    Parameters
    ----------
    technology name : str
        Name of the technology

    Returns
    -------
    technology: dict
        dictionary with relevant information
    """

    this_tech_path = (technology_path / technology_name / technology_name).with_suffix(".xlsx")

    logging.debug("Building technology %s", technology_name)

    technology = {
        "name": technology_name,
        "description": 'from file containing technology information',
        "image": str(technology_path / 'image.png'),
        "id": str(uuid.uuid4()),
        "category_defs": get_categories(this_tech_path),
        "metric_defs": get_metrics(this_tech_path)
    }

    return technology

@functools.lru_cache(maxsize=2)
def fetch_technologies():
    directories = [d for d in os.listdir(technology_path) if os.path.isdir(os.path.join(technology_path,d))]

    logging.debug(f"Scanning tech directories: {directories}")

    technology_list = [ create_technology(d) for d in directories ]

    return technology_list

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


def evaluate_without_slider_input(data_to_tyche, path, sample_count=100):
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

    path_change(data_to_tyche, path)
    my_designs = ty.Designs(path=".",
                            name='pv-residential-simple.xlsx')

    my_designs.compile()

    investments = ty.Investments(path='.', name='pv-residential-simple.xlsx')

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

@method
def evaluate_with_slider_input(data_to_tyche, path, sample_count=100):
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
    path_change(data_to_tyche, path)

    my_designs = ty.Designs(path=".",
                            name='pv-residential-simple.xlsx')

    my_designs.compile()

    investments = ty.Investments(path='.', name='pv-residential-simple.xlsx')

    tranche_results = investments.evaluate_tranches(
        my_designs, sample_count=sample_count)

    evaluator = ty.Evaluator(tranche_results)

    # Creating Dataframe
    # Here all we need to do is point to the correct Tyche technology, create the evaluator and run the evaluator with the dataframe with
    # category names in one column the investments in another

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
            a = []
            for n in list(df_m['Value']):
                a.append(float(n))
            results_to_gui['results'][c][m] = a

    return results_to_gui


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
