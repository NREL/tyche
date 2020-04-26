import numpy  as np
import pandas as pd

from .IO    import make_table, read_table
from .Types import Evaluations


class Investments:
    
    tranches    = None
    investments = None
    
    _tranches_dtypes = {
        "Category"   : np.str_   ,
        "Tranche"    : np.str_   ,
        "Scenario"   : np.str_   ,
        "Notes"      : np.str_   ,
    }
    _investments_dtypes = {
        "Investment" : np.str_   ,
        "Category"   : np.str_   ,
        "Tranche"    : np.str_   ,
        "Amount"     : np.float64,
        "Notes"      : np.str_   ,
    }
    
    _tranches_index    = ["Category"  , "Tranche" , "Scenario" ,        ]
    _investments_index = ["Investment", "Category", "Tranche"  ,        ]
    
    def __init__(
        self                           ,
        path        = None             ,
        tranches    = "tranches.tsv"   ,
        investments = "investments.tsv",
    ):
        if path == None:
            self._make()
        else:
            self._read(path, tranches, investments)
            
    def _make(self):
        self.tranches    = make_table(self._tranches_dtypes   , self._tranches_index   )
        self.investments = make_table(self._investments_dtypes, self._investments_index)
        
    def _read(self, path, tranches, investments):
        self.tranches    = read_table(path, tranches   , self._tranches_dtypes   , self._tranches_index   )
        self.investments = read_table(path, investments, self._investments_dtypes, self._investments_index)
        
    def evaluate_investments(self, designs):
        amounts = self.investments.sum(
            level=["Investment"]
        )
        metrics = self.investments.drop(
            columns=["Amount", "Notes"]
        ).join(
            self.tranches.drop(columns=["Notes"])
        ).join(
            designs.evaluate_scenarios().xs("Metric", level="Variable")
        ).reorder_levels(
            ["Investment", "Category", "Tranche", "Scenario", "Technology", "Index"]
        )
        return Evaluations(
            amounts = amounts,
            metrics = metrics,
            summary = metrics.set_index(
                "Units",
                append=True
            ).sum(
                level=["Investment", "Index", "Units"]
            ).reset_index(
                "Units"
            )[["Value", "Units"]],
        )
