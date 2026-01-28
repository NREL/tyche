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