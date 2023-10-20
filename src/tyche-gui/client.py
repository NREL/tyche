# server program
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
import uuid
#from run_tyche import *

import os
import pandas as pd
# Call by client
from jsonrpclib import Server
from functions import *





conn = Server('http://localhost:8080')

dic = conn.build_all_techs()
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
            
'''
This will probably be information from the GUI and be used for the calculation directly. 
Please do not include this in the code
'''

res_to_gui2 = conn.evaluate_without_slider_input(data_to_tyche,technology_path,10)
res_to_gui1 = conn.evaluate_with_slider_input(data_to_tyche,technology_path,10)
