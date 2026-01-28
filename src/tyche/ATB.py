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
# from .Designs       import sampler
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

FINANCIAL_PARAMETERS = ['CRF']

ATB_COLUMNS = (
    {"name": "Technology", "type": str, "index": True,  "backfill": None},
    {"name": "Tranche"  , "type": str, "index": True,  "backfill": None},
    {"name": "Variable"  , "type": str, "index": True,  "backfill": None},
    {"name": "Index"     , "type": str, "index": True,  "backfill": None},
    {"name": "Value"     , "type": str, "index": False, "backfill": None},
    {"name": "Units"     , "type": str, "index": False, "backfill": None},
    {"name": "Notes"     , "type": str, "index": False, "backfill": None}
  )

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
            # tech_name,
            # output_path = None, 
            # tech_filename = None,
            parameters = {}
    ):
        """
        Parameters
        ----------
        path : str
          Path to directory where ATB technology files are stored
        tech_name : str
          Name of ATB technology to process
        tech_filename : str
          CSV Filename where technology data is stored
        parameters : dict
                Dictionnary of technology parameters
        """
        self.path = path
        self.parameters = parameters
        
        self.tech_name = self.parameters["tech_name"]
        
        if self.parameters["output_path"] is not None:
            self.output_path = self.parameters["output_path"]
        else:
            self.output_path = path

        if self.parameters["tech_filename"] is not None:    
            self.read_data(self.parameters["tech_filename"])            
        else:
            self.call_ATB_calc()
        
        
    def read_data(self, tech_filename):
        """
        Read ATB data from CSV file
        """
        if not os.path.isfile(os.path.join(self.path, tech_filename)):
          print(f"No ATB data found in {os.path.join(self.path, self.tech_name)}")
          sys.exit(1)
        
        self.tech_filename = tech_filename
        self.data = pd.read_csv(os.path.join(self.path, self.tech_filename),
                                 keep_default_na=False)
        self.data.drop(columns = ["Unnamed: 0", "Reference", 
                                  "Type of Evidence", "Escalation Index", "Zotero_Key", 
                                  "Summary", "Bib_HTML"], inplace = True)

    def create_tyche_data(self, designs):
        """
        Create an ATB data and copy it to the tyche workbook
        This method should be called after checking if ATB data is NOT already stored in the workbook
        """
        # Check if tyche workbook has already an ATB
        # If there's data, clear the workbook. 
        
    def extract_values(self, parameter):
        """
        Extract values from ATB data
        """ 
        if parameter in FINANCIAL_PARAMETERS:
            display_name = "*"
        else:
            display_name = self.parameters["DisplayName"]        
        try:
            atb_val = self.data.loc[(self.data["Parameter"] == parameter) & 
                    (self.data["Case"] == self.parameters["Case"]) & 
                    (self.data["TaxCreditCase"] == self.parameters["TaxCreditCase"]) & 
                    (self.data["CRPYears"] == self.parameters["CRPYears"]) & 
                    (self.data["Technology"] == self.parameters["Technology"]) & 
                    (self.data["DisplayName"] == display_name) & 
                    (self.data["Scenario"] == self.parameters["Scenario"]) & 
                    (self.data["variable"] == self.parameters["variable"]),
                    'value'
                    ].iloc[0]
            print(f"ATB: extracted {parameter} = {round(atb_val, 2)}")
            return atb_val
        except ValueError:
            raise Exception(f"ATB: {parameter} was not found with combinations of passed ATB parameters.")
    
    
    def call_ATB_calc(self):
        """
        Call ATB-calc to get values
        """
        ##TODO: implement ATB-calc call
        
        print(f"No filename was provided for {self.tech_name}, calling ATB-calc to get ATB parameters")
        
        tech_name = ATB_TECHNOLOGIES.get(self.tech_name.title(), None)
        if tech_name is None:
            print(f"Technology {self.tech_name.title()} is not found")
            sys.exit(1)
        
        import_atb(self.parameters["ATB-calc_dir"])
    
        # self.tech_filename = f"{self.tech_name}_atb.csv"
        # self.data = call to atb-calc to process the technology
    

    def export_data(self):
        """
        export technology data to match ReEDS format
        """
        
        self.data.to_csv(os.path.join(self.output_path, f"{self.tech_name}_atb_calc.csv"), index=False)
        





    


    
            
    