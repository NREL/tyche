"""
Investments in technologies.
"""

import numpy  as np
import pandas as pd

from .Distributions import parse_distribution
from .IO    import make_table, read_table
from .Designs import sampler
from .Types import Evaluations


class Investments:
  """
  Investments in a technology.

  Attributes
  ----------
  tranches : DataFrame
    The *tranches* table.
  investments: DataFrame
    The *investments* table.
  """
  
  _tranches_dtypes = {
    "Category"   : np.str_,
    "Tranche"    : np.str_,
    "Scenario"   : np.str_,
    "Amount"     : np.str_,
    "Notes"      : np.str_,
  }
  _investments_dtypes = {
    "Investment" : np.str_,
    "Category"   : np.str_,
    "Tranche"    : np.str_,
    "Notes"      : np.str_,
  }
  
  _tranches_index    = ["Category"  , "Tranche" , "Scenario" ,        ]
  _investments_index = ["Investment", "Category", "Tranche"  ,        ]
  
  def __init__(
    self                           ,
    path        = None             ,
    uncertain   = False            ,
    tranches    = "tranches.csv"   ,
    investments = "investments.csv",
  ):
    """
    Parameters
    ----------
    path : str
      Path to directory where *tranches* and *investments* tables are saved.
    uncertain : Boolean
      Flag indicating whether probability distributions are present in the *tranches* table.
    tranches : str
      Filename for the *tranches* table.
    investments: str
      Filename for the *investments* table.
    """
    self.uncertain = uncertain
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

  def compile(self):
    """Parse any probability distributions in the tranches."""
    self.compiled_tranches = self.tranches.copy()
    self.compiled_tranches["Amount"] = self.compiled_tranches["Amount"].apply(parse_distribution)
  
  def evaluate_tranches(self, designs, sample_count=1):
    """
    Evaluate the tranches of investment for a design.

    Parameters
    ----------
    designs : tyche.Designs
      The designs.
    sample_count : int
      The number of random samples.
    """
    # Parse any probability distributions in the tranches table
    self.compile()

    # Check that only one of designs, investments contains uncertainty
    if self.uncertain + designs.uncertain > 1:
      print('Too much uncertainty. Remove probability distributions from tranches OR from technology data.')

    if self.uncertain:
      self.compiled_tranches["Samples"] = pd.Series(
        sampler(
          self.compiled_tranches.Amount,
          sample_count
          ).tolist(),
        index=self.compiled_tranches.index
      )
      samples = self.compiled_tranches.explode("Samples")
      samples["Amount"] = samples["Samples"]
      samples["Sample"] = pd.Series(
        np.tile(
          np.arange(sample_count)+1,
          len(self.compiled_tranches.index)
        ),
        index=samples.index
      )
      samples.reset_index(
        inplace=True
      )
      samples.set_index(
        keys = ["Category", "Tranche", "Sample"],
        inplace=True
      )
      amounts = samples.drop(
        columns=["Samples", "Notes"]
        ).sum(
          level=["Category", "Tranche", "Sample"]
      )
      metrics = amounts.drop(
        columns=["Amount"]
      ).join(
        designs.evaluate_scenarios(sample_count).xs("Metric", level="Variable")
      ).reorder_levels(
        ["Category", "Tranche", "Scenario", "Sample", "Technology", "Index"]
      )

    else:
      amounts = self.compiled_tranches.drop(
        columns=["Notes"]
      ).sum(
        level=["Category", "Tranche"]
      )
      metrics = self.compiled_tranches.drop(
        columns=["Amount", "Notes"]
      ).join(
        designs.evaluate_scenarios(sample_count).xs("Metric", level="Variable")
      ).reorder_levels(
        ["Category", "Tranche", "Scenario", "Sample", "Technology", "Index"]
      )

    return Evaluations(
      amounts = amounts,
      metrics = metrics,
      summary = metrics.set_index(
        "Units",
        append=True
      ).sum(
        level=["Category","Technology", "Tranche", "Sample", "Index", "Units"]
      ).reset_index(
        "Units"
      )[["Value", "Units"]],
      uncertain=self.uncertain,
    )
      
  def evaluate_investments(self, designs, sample_count=1):
    """
    Evaluate the investments for a design.

    Parameters
    ----------
    designs : tyche.Designs
      The designs.
    sample_count : int
      The number of random samples.
    """

    amounts = self.investments.drop(
      columns=["Notes"]
    ).join(
      self.tranches.drop(columns=["Notes"])
    ).sum(
      level=["Investment"]
    )
    metrics = self.investments.drop(
      columns=["Notes"]
    ).join(
      self.tranches.drop(columns=["Amount", "Notes"])
    ).join(
      designs.evaluate_scenarios(sample_count).xs("Metric", level="Variable")
    ).reorder_levels(
      ["Investment", "Category", "Tranche", "Scenario", "Sample", "Technology", "Index"]
    )
    return Evaluations(
      amounts = amounts,
      metrics = metrics,
      summary = metrics.set_index(
        "Units",
        append=True
      ).sum(
        level=["Investment", "Technology", "Sample", "Index", "Units"]
      ).reset_index(
        "Units"
      )[["Value", "Units"]],
    )
