"""
Fast evaluation of technology investments.
"""

import numpy  as np
import pandas as pd

from scipy.interpolate import interp1d


class Evaluator:
  """
  Evalutate technology investments using a response surface.

  Attributes
  ----------
  amounts : DataFrame
    Cost of tranches.
  categories : DataFrame
    Categories of investment.
  metrics : DataFrame
    Metrics for technologies.
  units : DataFrame
    Units of measure for metrics.
  interpolators : DataFrame
    Interpolation functions for technology metrics.
  """

  def __init__(self, tranches, summary):
    """
    Parameters
    ----------
    tranches : DataFrame
      The tranches of investment.
    summary : DataFrame
      The summary of evaluating the tranches.
    """

    self.amounts    = tranches.groupby(["Category", "Tranche"]).sum()
    self.categories = summary.reset_index()["Category"].unique()
    self.metrics    = summary.reset_index()["Index"   ].unique()
    self.units      = summary[["Units"]].groupby("Index").max()
    self.interpolators = summary.join(
      self.amounts
    ).groupby(
      ["Category", "Index", "Sample"]
    ).apply(
      lambda df: interp1d(
        np.append(df.Amount, 0),
        np.append(df.Value , 0),
        kind = "linear"        ,
        fill_value = "extrapolate",
        assume_sorted = False  ,
      )
    ).rename(
      "Interpolator"
    )
    self.max_amount = self.amounts.groupby("Category").max()
    self.min_metric = summary.groupby(["Category", "Index"]).min(numeric_only = True).groupby("Index").sum()
    self.max_metric = summary.groupby(["Category", "Index"]).max(numeric_only = True).groupby("Index").sum()

  def evaluate(self, amounts):
    """
    Sample the distribution for an investment.

    Parameters
    ----------
    amounts : DataFrame
      The investment levels.
    """

    return amounts.join(
      self.interpolators
    ).apply(
      lambda row: row["Interpolator"](row["Amount"]), axis = 1
    ).rename(
      "Value"
    )

  def evaluate_statistic(self, amounts, statistic = np.mean):
    """
    Evaluate a statistic for an investment.

    Parameters
    ----------
    amounts : DataFrame
      The investment levels.
    statistics : DataFrame
      The statistic to evaluate.
    """

    return self.evaluate(
      pd.DataFrame(amounts)
    ).groupby(
      ["Index", "Sample"]
    ).sum(
    ).groupby(
      "Index"
    ).aggregate(
      statistic
    )
