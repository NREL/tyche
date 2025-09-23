"""
Get ATB parameters and assumptions
# Either call the atb-calc to read the ATB values, or read the values from a processed csv file
https://github.com/NREL/ATB-calc
"""

import os
import sys
import numpy  as np
import pandas as pd

from .Distributions import parse_distribution
from .IO            import check_tables
from .DataManager   import TranchesDataset, InvestmentsDataset
from .Designs       import sampler
from .Types         import Evaluations


# To import ATB-calc 
def import_atb(atb_calc_path):
    sys.path.append(atb_calc_path)
    from lcoe_calculator.process_all import ProcessAll
    from lcoe_calculator.tech_processors import (ALL_TECHS,
        FixedOffShoreWindProc, FloatingOffShoreWindProc, LandBasedWindProc, DistributedWindProc,
        UtilityPvProc, CommPvProc, ResPvProc, UtilityPvPlusBatteryProc,
        CspProc, GeothermalProc, HydropowerProc, PumpedStorageHydroProc,
        PumpedStorageHydroOneResProc,
        CoalProc, NaturalGasProc, NuclearProc, BiopowerProc,
        UtilityBatteryProc, CommBatteryProc, ResBatteryProc,
        CoalRetrofitProc, NaturalGasRetrofitProc, NaturalGasFuelCellProc)


ATB_TECHNOLOGIES = {
    "Geothermal": "GeothermalProc",
    "Nuclear": "NuclearProc",
}

#TODO: add ATB-calc
class ATB:
    """
    Read ATB technologies

    Attributes
    ----------
    """
    def __init__(
            self,
            path, 
            atb_tech, 
            tech_filename = None,
            parameters = {}
    ):
        """
        Parameters
        ----------
        path : str
          Path to directory where ATB technology files are stored
        atb_tech : str
          Name of ATB technology to process
        tech_filename : str
          CSV Filename where technology data is stored
        parameters : dict
                Dictionnary of technology parameters
        """
        self.path = path
        self.atb_tech = atb_tech
        self.parameters = parameters
        
        if tech_filename is not None:
            self.read_atb_data(path, tech_filename)            
        else:
            self.call_ATB_calc()

        
    def read_atb_data(self, tech_filename):
        """
        Read ATB data from CSV file
        """
        if not os.path.isfile(os.path.join(self.path, self.tech_filename)):
          print(f"Investments: No input data found in {os.path.join(self.path, self.atb_tech)}")
          sys.exit(1)
        else:
            self.atb_data = pd.read_csv(os.path.join(self.path, self.tech_filename))
            self.tech_filename = tech_filename

    def extract_values(self, parameter):
        """
        Extract values from ATB data
        """       
        return self.atb_data.loc[(self.atb_data["Parameter"] == parameter) & 
                    (self.atb_data["Case"] == self.parameters["Case"]) & 
                    (self.atb_data["TaxCreditCase"] == self.parameters["TaxCreditCase"]) & 
                    (self.atb_data["CRPYears"] == self.parameters["CRPYears"]) & 
                    (self.atb_data["Technology"] == self.parameters["Technology"]) & 
                    (self.atb_data["DisplayName"] == self.parameters["DisplayName"]) & 
                    (self.atb_data["Scenario"] == self.parameters["Scenario"]) & 
                    (self.atb_data["variable"] == self.parameters["variable"]),
                    'value'
                    ].iloc[0]
    
    def call_ATB_calc(self):
        """
        Call ATB-calc to get values
        """
        ##TODO: implement ATB-calc call
        
        print(f"No filename was provided for {self.atb_tech}, calling ATB-calc to get ATB parameters")
        
        tech_name = ATB_TECHNOLOGIES.get(self.atb_tech.title(), None)
        if tech_name is None:
            print(f"Technology {self.atb_tech.title()} is not found")
            sys.exit(1)
        
        import_atb(self.parameters["ATB-calc_dir"])
    
        
            
        print(tech_name)
        # self.tech_filename = f"{self.atb_tech}_atb.csv"
        # self.atb_data = call to atb-calc to process the technology





    


    
            
    