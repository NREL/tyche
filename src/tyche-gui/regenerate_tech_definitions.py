#!/usr/bin/env python3

"""
This tool builds a database for the tyche-gui server. 

This database holds a list of technologies, needed paths, generated UUIDs.

If each were to generate UUIDs on launch, we cannot use multiple scripts to serve requests

"""

import logging
import os
import json
import random
import server_common
import pandas as pd
import uuid

def get_image(this_tech_image,seed):

    if this_tech_image != None:
        isExisting = os.path.exists(this_tech_image)
    else:
        isExisting = False
    if isExisting == True:
         return str(this_tech_image)
    else:
        return f"https://picsum.photos/seed/{seed}/128/128"

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

        starting_investment = min(d['Amount'])
        max_investment = max(d['Amount'])

        if starting_investment == 0:
            starting_investment = int((random.random()*.2 + .1) * max_investment)

        cat_id = str(uuid.uuid4())

        category = {
            'name': c,
            'description': str(pd.unique(d['Category'])[0]),
            'starting_investment': starting_investment,
            'max_investment': max_investment,
            'image' : get_image(None,cat_id),
            'id': cat_id
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

    datafile = pd.read_excel(tech_source, sheet_name="indices")
    d_metrics = datafile[datafile['Type'] == 'Metric']

    metrics = list(pd.unique(d_metrics['Index']))
    metric_list = []
    for m in metrics:
        d = d_metrics[d_metrics['Index'] == m]

        metric_id = str(uuid.uuid4())

        metric = {
            'name': m,
            'description': str(pd.unique(d['Description'])[0]),
            'image' : get_image(None,metric_id),
            'id': metric_id
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

    this_tech_path = (server_common.technology_path / technology_name / technology_name).with_suffix(".xlsx")
    this_tech_image = (server_common.technology_path / technology_name / technology_name).with_suffix(".jpg")
    
    logging.debug("Building technology %s", technology_name)

    tech_id = uuid.uuid4()
    datafile = pd.read_excel(this_tech_path, sheet_name="designs")

    technology = {
        "name": technology_name,
        "description": str(pd.unique(datafile['Technology'])[0]),
        "image": get_image(this_tech_image,str(tech_id)),
        "id": str(tech_id),
        "category_defs": get_categories(this_tech_path),
        "metric_defs": get_metrics(this_tech_path)
    }

    return technology

def is_valid_tech_dir(a_path):
    return os.path.isdir(a_path) and "__" not in a_path

def build_all_techs():
    directories = [
        d 
        for d in os.listdir(server_common.technology_path) 
        if is_valid_tech_dir(os.path.join(server_common.technology_path,d))
    ]

    logging.debug(f"Scanning tech directories: {directories}")

    technology_list = [ create_technology(d) for d in directories ]

    tech_uuid_map = { 
        tech["id"] : tech_dir 
        for (tech, tech_dir) in zip(technology_list, directories) 
    }

    return {
        "technology_list" : technology_list, 
        "tech_uuid_to_dir" : tech_uuid_map
    }

if __name__ == '__main__':  
    logging.basicConfig(level=logging.DEBUG)

    db = build_all_techs()

    with open(server_common.tech_database_path, 'w') as db_file:
        json.dump(db, db_file, indent=4)

