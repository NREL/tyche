# server program
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
import uuid
from functions import *
import os
import pandas as pd
# Call by client
from jsonrpclib import Server
import sys






conn = Server('http://localhost:8080')

dic = conn.get_scenarios()
data_to_gui = dic
selected_tech = 'pv-residential-simple'

path = "/Users/tghosh/Library/CloudStorage/OneDrive-NREL/work_NREL/tyche/tyche/src/technology/pv-residential-simple"

scenario_state = {}
scenario_state['scenario_id'] = data_to_gui[5]['id']
scenario_state['category_states'] = {}
scenario_state['category_states'][data_to_gui[5]['category_defs'][0]['id']] = 50
scenario_state['category_states'][data_to_gui[5]['category_defs'][1]['id']] = 50
scenario_state['category_states'][data_to_gui[5]['category_defs'][2]['id']] = 50
df = conn.run_scenario(scenario_state)

opt_parameters = {}
opt_parameters['optimized_metric']= "LCOE"                  
opt_parameters['optimization_sense']= None  
opt_parameters['max_amount']=  None  
opt_parameters['investment_max']=   None   
opt_parameters['metric_df']=  None    
opt_parameters['statistic']=  'np.mean'  
opt_parameters['initial'] =  None    
opt_parameters['tol']=      1e-8
opt_parameters['maxiter']=    50  
opt_parameters['verbose']=  0

metric_df = {}
metric_df['GHG'] = {}
metric_df['Labor'] = {}
metric_df['GHG']['limit'] = 30
metric_df['GHG']['sense'] = 'upper'
metric_df['Labor']['limit'] = 0
metric_df['Labor']['sense'] = 'lower'

#If user puts in metric contraints, the opt_parameters should be updated
opt_parameters['metric_df']= metric_df

#Run optimization
res_to_gui3 = conn.run_optimization(scenario_state,opt_parameters)

sys.exit(0)

