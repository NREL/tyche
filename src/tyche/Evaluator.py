"""
Fast evaluation of technology investments.
"""

import numpy  as np
import pandas as pd

from scipy.interpolate import interp1d

from .Types import Evaluations

import pdb
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

  def __init__(self, tranches):
    """
    Parameters
    ----------
    tranches : Evaluations
      Output of the evaluate_tranches method in Investments class. Named tuple with
      the following elements:
        amounts   : DataFrame
        metrics   : Data Frame
        summary   : Data Frame
        uncertain : Boolean
    """

    if tranches.uncertain:
      self.amounts    = tranches.amounts.groupby(["Category", "Tranche", "Sample"]).sum()
    else:
      self.amounts    = tranches.amounts.groupby(["Category", "Tranche"]).sum()
    self.categories = tranches.summary.reset_index()["Category"].unique()
    self.metrics    = tranches.summary.reset_index()["Index"   ].unique()
    self.units      = tranches.summary[["Units"]].groupby("Index").max()
    self.raw        = tranches.summary.join(self.amounts)
    self.interpolators = self.raw.groupby(
      ["Category", "Index", "Sample"]
    ).apply(
      lambda df: interp1d(
        df.Amount,
        df.Value ,
        kind = "linear"        ,
        fill_value = "extrapolate",
        assume_sorted = False  ,
      )
    ).rename(
      "Interpolator"
    )
    self.max_amount = self.amounts.groupby("Category").max()
    self.min_metric = tranches.summary.groupby(["Category", "Index"]).min(numeric_only = True).groupby("Index").sum()
    self.max_metric = tranches.summary.groupby(["Category", "Index"]).max(numeric_only = True).groupby("Index").sum()

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
    statistic : function
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

  def make_statistic_evaluator(self, statistic = np.mean):
    """
    Return a function that evaluates a statistic for an investment.

    Parameters
    ----------
    statistic : function
      The statistic to evaluate.
    """
    interpolators1 = self.raw.groupby(
      ["Category", "Tranche", "Index"]
    ).aggregate(
      statistic
    ).reset_index(
    ).groupby(
      ["Category", "Index"]
    ).apply(
      lambda df: interp1d(
        df.Amount,
        df.Value ,
        kind = "linear"        ,
        fill_value = "extrapolate",
        assume_sorted = False  ,
      )
    ).rename(
      "Interpolator"
    )
    def f(amounts):
      pdb.set_trace()
      return pd.DataFrame(
        amounts
      ).join(
        interpolators1
      ).apply(
        lambda row: row["Interpolator"](row["Amount"]), axis = 1
      ).groupby(
        "Index"
      ).sum( # @TODO replace with user-defined aggregation method - aggregate across categories
      ).rename(
        "Value"
      )
    return f

  def evaluate_corners_semilong(self, statistic = np.mean):
    """
    Return a dataframe indexed my investment amounts in each category,
    with columns for each metric.

    Parameters
    ----------
    statistic : function
      The statistic to evaluate.
    """

    return pd.DataFrame(
      self.raw.reset_index(
      ).set_index(
          ["Category","Amount", "Index"]
      ).drop(
          columns = ["Tranche","Technology","Sample", "Units"]
      ).apply(
          statistic, axis=1
      ).rename(
          "Value"
      )
    ).reset_index(
    ).set_index(
      ["Category", "Amount"]
    ).pivot_table(
      index = ["Category", "Amount"],
      columns = "Index",
      values = "Value"
    )

  def evaluate_corners_wide(self, statistic = np.mean):
    """
    Return a dataframe indexed my investment amounts in each category,
    with columns for each metric.

    Parameters
    ----------
    statistic : function
      The statistic to evaluate.
    """

    semilong = self.evaluate_corners_semilong(statistic)
    joiner = pd.DataFrame(index = semilong.index)
    joiner["KEY"] = 1
    joiner.set_index("KEY", append = True, inplace = True)
    combinations = pd.DataFrame(index = pd.Index([1], name = "KEY"))
    for category in np.unique(joiner.index.get_level_values("Category")):
        combinations = combinations.merge(
            joiner.xs(
              category
            ).reset_index(
              "Amount"
            ).rename(
              columns = {"Amount" : category}
            ),
            on = "KEY",
            how = "outer",
        )
    combinations.set_index(list(combinations.columns), inplace = True)
    result = pd.DataFrame([
      pd.DataFrame([
        semilong.loc[iname, ivalue]
        for iname, ivalue in zip(combinations.index.names, i0)
      ]).reset_index(drop = True).aggregate(np.sum)
      for i0, _ in combinations.iterrows()
    ])
    result.index = combinations.index
    return result
