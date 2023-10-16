# server program
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
import uuid
#from run_tyche import *

import os
import pandas as pd
# Call by client
from jsonrpclib import Server
from functions import *





conn = Server('http://localhost:1080')

path="/Users/tghosh/Library/CloudStorage/OneDrive-NREL/work_NREL/tyche/tyche/src/technology/"
os.chdir("/Users/tghosh/Library/CloudStorage/OneDrive-NREL/work_NREL/tyche/tyche/src/tyche-gui/")


dic = conn.get_technology()
data_to_gui = dic


#User chooses a technology   
#normal mode appears
#User changes sliders which brings in results

#Min max slider are obtained from the user input data. 

#Information from the GUI ---->
#This information is what the Tyche function needs from the GUI to operate.
category_list=[]
category_list.append({
                 'name':'Module R&D',
                  'investment':50,
                  'id':data_to_gui[5]['category_defs'][0]['id']
                 })

category_list.append({
                 'name':'Inverter R&D',
                  'investment':50,
                  'id':data_to_gui[5]['category_defs'][1]['id']
                 })
category_list.append({
                 'name':'BoS R&D',
                  'investment':50,
                  'id':data_to_gui[5]['category_defs'][2]['id']
                 })
technology_state={
                'id':data_to_gui[5]['id'],
                'category_states':category_list
                }


#using the technology id we make sure to call the proper technology 
for d in data_to_gui:
    if d['id'] == technology_state['id']:
        data_to_tyche = d
        data_to_tyche['states'] = technology_state

cat_list = []
inv_list = []



for d in data_to_tyche['states']['category_states']:
            cat_list.append(d['name'])
            inv_list.append(d['investment'])
            pass



res_to_gui2 = conn.evaluate_without_slider_input(data_to_tyche,path,10)
res_to_gui1 = conn.evaluate_with_slider_input(data_to_tyche,path,10)


'''
This information is for running optimization. Optimization needs to several inputs from user.

Please check issue on Github
The following directory opt_parameters is an user input from the user GUI
'''
opt_parameters = {}
opt_parameters['optimized_metric']= "LCOE"                  
opt_parameters['optimization_sense']=    None  
opt_parameters['max_amount']=  None  
opt_parameters['investment_max']=   None   
opt_parameters['metric_df']=  None    
opt_parameters['statistic']=  'np.mean'  
opt_parameters['initial'] =  None    
opt_parameters['tol']=      1e-8
opt_parameters['maxiter']=    50  
opt_parameters['verbose']=  0     

#Run optimization
res_to_gui3 = conn.evaluate_opt(data_to_tyche,path,opt_parameters,10)

#We can add all these parameters from the user if data is provided. An example of constraint created on metric values is provided
metric_df = {}
metric_df['GHG'] = {}
metric_df['Labor'] = {}
metric_df['GHG']['limit'] = 30
metric_df['GHG']['sense'] = 'upper'
metric_df['Labor']['limit'] = 0
metric_df['Labor']['sense'] = 'lower' 

   
#If user puts in metric contraints, the opt_parameters should be updated 
opt_parameters['metric_df']=  metric_df
#Run optimization again
res_to_gui3 = conn.evaluate_opt(data_to_tyche,path,opt_parameters,10)
         
'''
This will probably be information from the GUI and be used for the calculation directly. 
Please do not include this in the code
'''

