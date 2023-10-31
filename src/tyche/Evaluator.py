"""
Fast evaluation of technology investments.
"""

import numpy  as np
import pandas as pd

from scipy.interpolate import interp1d

from .Types import Evaluations


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
    # dictionary of statistical function options 
    # for use in the various evaluator methods
    # add entries to this dict to expand the options
    self.statistic_lookup = {
      'mean': np.mean,
      'median': np.median,
      'standard deviation': np.std,
      '10th percentile': lambda x: np.percentile(x, 0.1),
      '25th percentile': lambda x: np.percentile(x, 0.25),
      '75th percentile': lambda x: np.percentile(x, 0.75),
      '90th percentile': lambda x: np.percentile(x, 0.9)
    }  

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

  def evaluate_statistic(self, amounts, statistic = 'mean'):
    """
    Evaluate a statistic for an investment.

    Parameters
    ----------
    amounts : DataFrame
      The investment levels.
    statistic : string
      Name of the statistic to evaluate. Options are mean, median,
      10th percentile, 25th percentile, 75th percentile, 90th
      percentile, and standard deviation. If another name is
      entered, an error is thrown and the mean is used instead.
    """
    # look up the callable based on the statistic parameter
    # if the string is not found in the dict, use mean
    try:
      _stat_fcn = self.statistic_lookup[statistic]
    except KeyError as e:
      _stat_fcn = np.mean
      print(f'{e} not found in statistic function lookup; using mean')
    
    return self.evaluate(
      pd.DataFrame(amounts)
      ).groupby(
          ['Index','Sample']
      ).sum(
      ).groupby(
        ['Index']
      ).agg(
        Value = _stat_fcn
      )

  def make_statistic_evaluator(self, statistic = 'mean'):
    """
    Return a function that evaluates a statistic for an investment.

    Parameters
    ----------
    statistic : string
      Name of the statistic to evaluate. Options are mean, median,
      10th percentile, 25th percentile, 75th percentile, 90th
      percentile, and standard deviation. If another name is
      entered, an error is thrown and the mean is used instead.
    """
    # if the string is not found in the dict, use mean
    try:
      _stat_fcn = self.statistic_lookup[statistic]
    except KeyError as e:
      _stat_fcn = np.mean
      print(f'{e} not found in statistic function lookup; using mean')
    
    interpolators1 = self.raw.groupby(
      ['Category','Tranche','Index','Amount']
    ).agg(
      Value=('Value',_stat_fcn)
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

  def evaluate_corners_semilong(self, statistic = 'mean'):
    """
    Return a dataframe indexed my investment amounts in each category,
    with columns for each metric.

    Parameters
    ----------
    statistic : string
      Name of the statistic to evaluate. Options are mean, median,
      10th percentile, 25th percentile, 75th percentile, 90th
      percentile, and standard deviation. If another name is
      entered, an error is thrown and the mean is used instead.
    """
    # if the string is not found in the dict, use mean
    try:
      _stat_fcn = self.statistic_lookup[statistic]
    except KeyError as e:
      _stat_fcn = np.mean
      print(f'{e} not found in statistic function lookup; using mean')
    
    return pd.DataFrame(
      self.raw.reset_index(
      ).set_index(
          ["Category","Amount", "Index"]
      ).drop(
          columns = ["Tranche","Technology","Sample", "Units"]
      ).apply(
          _stat_fcn, axis=1
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

  def evaluate_corners_wide(self, statistic = 'mean'):
    """
    Return a dataframe indexed my investment amounts in each category,
    with columns for each metric.

    Parameters
    ----------
    statistic : string
      Name of the statistic to evaluate. Options are mean, median,
      10th percentile, 25th percentile, 75th percentile, 90th
      percentile, and standard deviation. If another name is
      entered, an error is thrown and the mean is used instead.
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
