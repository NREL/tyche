import os, sys
import numpy             as np
import matplotlib.pyplot as pl
import pandas            as pd
import seaborn           as sb
from pathlib import Path
sys.path.insert(0, os.path.abspath("../../../src"))
import tyche             as ty

cur_dir =  Path(__file__).parent.absolute()
technology_dir = cur_dir.parent
src_dir = technology_dir.parent

atb_dir = os.path.join(src_dir, 'atb')

geo_parameters = {
               'ATB-calc_dir': '/Users/aayad/Work/repos/ATB-calc',
              'Case': 'Market',
              'TaxCreditCase': 'ITC',
              'CRPYears': 20,
              'Technology': 'Geothermal',
              'DisplayName': 'Geothermal - Hydro / Flash',
              'Scenario': 'Moderate',
              'variable': 2022
              }

atb_geo = ty.ATB(path = atb_dir,
             atb_tech = 'geothermal',
             tech_filename = 'geothermal_atb.csv',
             parameters = geo_parameters)


# designs = ty.Designs(path = ".",
#                     name = 'geothermal.xlsx')

