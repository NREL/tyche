# server program
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
import uuid
from run_tyche import *

import os
import pandas as pd
# Call by client
from jsonrpclib import Server

conn = Server('http://localhost:1080')
path="/Users/tghosh/Library/CloudStorage/OneDrive-NREL/work_NREL/tyche/src/technology/"


os.chdir(path)
os.popen('find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf')   
os.chdir('./') 

def get_categories(technology_name):
    datafile=pd.read_excel(path+technology_name+"/"+technology_name+".xlsx",sheet_name = "tranches")
    categories = list(pd.unique(datafile['Category']))
    category_list = []
    for c in categories:
        d = datafile[datafile['Category'] == c]
        category={
                  'name':c,
                  'description':list(pd.unique(d['Notes'])),
                  'starting_investment': min(d['Amount']),
                  'max_investment': max(d['Amount'])
                 }
        category_list.append(category)
    return category_list



def get_metrics(technology_name):
    
    datafile=pd.read_excel(path+technology_name+"/"+technology_name+".xlsx",sheet_name = "results")
    d_metrics = datafile[datafile['Variable'] == 'Metric']
    
    metrics = list(pd.unique(d_metrics['Index']))
    metric_list = []
    for m in metrics:
        d = d_metrics[d_metrics['Index'] == m]
        metric={
                  'name':list(pd.unique(d['Index'])),
                  'description':list(pd.unique(d['Notes']))
                 }
        metric_list.append(metric)
    return metric_list    


    

def create_technology(technology_name):

     
    technology={
            "name" : technology_name,
            "description" : 'from file containing technology information',
            "image" : path+'image.png',
            "id" : uuid.uuid4(),
            "category_defs" : get_categories(technology_name),
            "metric_defs" : get_metrics(technology_name)
            } 
    
    return technology

def get_technology():
    #Returns the technology list
    directories=[d for d in os.listdir(path) if os.path.isdir(path+d)]

    technology_list= []
    for d in directories:
        print(d)
        technology_list.append(create_technology(d))
        
    return technology_list


#Get technology list
data_to_gui = get_technology()
    
    
#User chooses a technology   
#normal mode appears
#User changes sliders which brings in results

#Min max slider are obtained from the user input data. 

#Information from the GUI ---->
category_list=[]
category_list.append({
                 'name':'Rotor Investment Only',
                  'investment':50
                 })

category_list.append({
                 'name':'Drive Investment Only',
                  'investment':50
                 })
category_list.append({
                 'name':'Tower Investment Only',
                  'investment':50
                 })
technology_state={
                'id':data_to_gui[0]['id'],
                'category_states':category_list
                }
#using the technology id we make sure to call the proper technology 
for d in data_to_gui:
    if d['id'] == technology_state['id']:
        data_to_tyche = d
        data_to_tyche['states'] = technology_state

cat_list = []
inv_list = []


data_to_tyche['states']['category_states']

for d in data_to_tyche['states']['category_states']:
            cat_list.append(d['name'])
            inv_list.append(d['investment'])
            pass
            
evaluate_df = pd.DataFrame()
evaluate_df['category'] = cat_list   
evaluate_df['investment'] = inv_list         
#Creating Dataframe        
#Here all we need to do is point to the correct Tyche technology, create the evaluator and run the evaluator with the dataframe with
#category names in one column the investments in another

res_to_gui = run_tyche(data_to_tyche,path)


print(res_to_gui.xs(("Wind Turbine", "Metric", "LCOE"),level = ("Technology", "Variable", "Index")).reset_index())
