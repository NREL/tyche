import os
import sys
sys.path.insert(0, os.path.abspath("../../tyche/src/"))
print(os.getcwd())

import numpy             as np
import matplotlib.pyplot as pl
import pandas            as pd
import seaborn           as sb
import tyche             as ty


def run_tyche(data_to_tyche,path):
    
    path2 = path + data_to_tyche['name']+"/"
    my_designs = ty.Designs(path = path2,
                        name = 'tutorial-basic.xlsx')