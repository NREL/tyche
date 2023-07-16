

import os
import sys

sys.path.insert(0, os.path.abspath("../../tyche/src/"))


import numpy             as np
import matplotlib.pyplot as pl
import pandas            as pd
import seaborn           as sb
import tyche             as ty


def run_tyche(data_to_tyche,path):
    sys.path.insert(1, os.path.abspath("../../tyche/src/technology/"))
    path2 = path + data_to_tyche['name']+"/"
    os.chdir(path2)

    my_designs = ty.Designs(path = path2,
                        name = 'tutorial-basic.xlsx')
    
    my_designs.compile()
    #print(my_designs.designs.reset_index(["Variable", "Index"]).sort_values(["Variable", "Index"]))
    answers = my_designs.evaluate_tranche_impacts(sample_count=100)
    return answers