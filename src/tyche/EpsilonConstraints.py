
import numpy  as np
import pandas as pd

from scipy.optimize import minimize


class EpsilonConstraintMinimizer:

  def __init__(self, evaluator, scale = 1e6):
    self.evaluator = evaluator
    self.scale = scale
    self._max_metrics = None

  def _f(self, statistic):
    return lambda x: - self.evaluator.evaluate_statistic(
      pd.Series(self.scale * x, name = "Amount", index = self.evaluator.max_amount.index),
      statistic,
    )

  def _fi(self, i, statistic):
    return lambda x: self._f(statistic)(x)[i]

  def maximize(
    self                  ,
    metric                ,
    max_amount   = None   ,
    total_amount = None   ,
    min_metric   = None   ,
    statistic    = np.mean,
    tol          = 1e-10  ,
    maxiter      = 25     ,
  ):
    i = np.where(self.evaluator.metrics == metric)[0][0]
    if max_amount is None:
      max_amount = self.evaluator.max_amount.Amount
    bounds = [(0, x) for x in max_amount / self.scale]
    constraints = []
    if total_amount is not None:
      constraints += [
        {"type" : "ineq", "fun" : lambda x: total_amount / self.scale - sum(x)}
      ]
    if min_metric is not None:
      constraints += [
        {"type" : "ineq", "fun" : lambda x: x[np.where(self.evaluator.metrics == index)] - value / self.scale}
        for index, value in min_metric.iteritems()
      ]    
    result = minimize(
      self._fi(i, statistic)             ,
      max_amount.values / self.scale / 20,
      method      = "SLSQP"              ,
      bounds      = bounds               ,
      constraints = constraints          ,
      tol         = tol                  ,
      options = {
        "maxiter" : maxiter,
      # "disp"    : 3      ,
      # "iprint"  : 3      ,
      }
    )
    x = pd.Series(self.scale * result.x, name = "Amount", index = self.evaluator.max_amount.index)
    y = self.evaluator.evaluate_statistic(x, statistic)
    return x, y

  def max_metrics(self, max_amount = None, total_amount = None, statistic = np.mean):
    return {
      metric : self.maximize(metric, max_amount, total_amount, None, statistic)
      for metric in self.evaluator.metrics
    }
