
import numpy  as np
import pandas as pd

from scipy.optimize import minimize


class EpsilonConstraintOptimizer:

  def __init__(self, evaluator, scale = 1e6):
    self.evaluator = evaluator
    self.scale = scale
    self._max_metrics = {}

  def _f(self, statistic, verbose = 0):
    def f(x):
      xx = pd.Series(self.scale * x, name = "Amount", index = self.evaluator.max_amount.index)
      yy = self.evaluator.evaluate_statistic(xx, statistic)
      if verbose > 2:
        print (xx.values, yy.values)
      return - yy
    return f

  def _fi(self, i, statistic, verbose = 0):
    return lambda x: self._f(statistic, verbose)(x)[i]

  def maximize(
    self                  ,
    metric                ,
    max_amount   = None   ,
    total_amount = None   ,
    min_metric   = None   ,
    statistic    = np.mean,
    initial      = None   ,
    tol          = 1e-10  ,
    maxiter      = 25     ,
    verbose      = 0      ,
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
        {"type" : "ineq", "fun" : lambda x: x[np.where(self.evaluator.metrics == index)[0][0]] - value}
        for index, value in min_metric.iteritems()
      ]    
    if initial is None:
      initial = max_amount.values / 2
    result = minimize(
      self._fi(i, statistic, verbose)    ,
      initial / self.scale               ,
      method      = "SLSQP"              ,
      bounds      = bounds               ,
      constraints = constraints          ,
      tol         = tol                  ,
      options = {
        "maxiter" : maxiter                ,
        "disp"    : verbose >= 1           ,
        "iprint"  : 0 if verbose < 2 else 3,
      }
    )
    x = pd.Series(self.scale * result.x, name = "Amount", index = self.evaluator.max_amount.index)
    y = self.evaluator.evaluate_statistic(x, statistic)
    return result.message, x, y

  def max_metrics(
    self                  ,
    max_amount   = None   ,
    total_amount = None   ,
    statistic    = np.mean,
    tol          = 1e-10  ,
    maxiter      = 25     ,
    verbose      = 0      ,
  ):
    self._max_metrics = {
      metric : self.maximize(metric, max_amount, total_amount, None, statistic, None, tol, maxiter, verbose)
      for metric in self.evaluator.metrics
    }
    return pd.Series(
      [v[2][k] for k, v in self._max_metrics.items()],
      name  = "Value"                                ,
      index = self._max_metrics.keys()               ,
    )
