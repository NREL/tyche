
import numpy as np

from scipy.interpolate import interp1d


class Evaluator:

  def __init__(self, tranches, summary):
    self.amounts    = tranches.groupby(["Category", "Tranche"]).sum() / 1000
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
    return amounts.join(
      self.interpolators
    ).apply(
      lambda row: row["Interpolator"](row["Amount"]), axis = 1
    ).rename(
      "Value"
    )
