
import numpy  as np
import pandas as pd

from collections    import namedtuple
from scipy.optimize import fmin_slsqp


Optimum = namedtuple(
  "Optimum",
  ["exit_code", "exit_message", "amounts", "metrics"]
)


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
    tol          = 1e-8   ,
    maxiter      = 50     ,
    verbose      = 0      ,
  ):
    i = np.where(self.evaluator.metrics == metric)[0][0]
    if max_amount is None:
      max_amount = self.evaluator.max_amount.Amount
    bounds = [(0, x) for x in max_amount / self.scale]
    def g(x):
      constraints = [1]
      if total_amount is not None:
        limit = total_amount / self.scale
        value = sum(x)
        if verbose >= 3:
          print(x, limit, value, value <= limit)
        constraints = [limit - value]
      if min_metric is not None:
        for index, limit in min_metric.iteritems():
          j = np.where(self.evaluator.metrics == index)[0][0]
          value = - self._f(statistic, verbose)(x)[j]
          if verbose >= 3:
            print(x, limit, value, value >= limit)
          constraints += [value - limit]
      return constraints
    if initial is None:
      initial = max_amount.values / 10
    result = fmin_slsqp(
      self._fi(i, statistic, verbose),
      initial / self.scale ,
      f_ieqcons   = g      ,
      bounds      = bounds ,
      iter        = maxiter,
      acc         = tol    ,
      iprint      = verbose,
      full_output = True   ,
    )
    x = pd.Series(self.scale * result[0], name = "Amount", index = self.evaluator.max_amount.index)
    y = self.evaluator.evaluate_statistic(x, statistic)
    return Optimum(
      exit_code    = result[3],
      exit_message = result[4],
      amounts      = x        ,
      metrics      = y        ,
    )

  def max_metrics(
    self                  ,
    max_amount   = None   ,
    total_amount = None   ,
    statistic    = np.mean,
    tol          = 1e-8   ,
    maxiter      = 50     ,
    verbose      = 0      ,
  ):
    self._max_metrics = {
      metric : self.maximize(metric, max_amount, total_amount, None, statistic, None, tol, maxiter, verbose)
      for metric in self.evaluator.metrics
    }
    return pd.Series(
      [v.metrics[k] if v.exit_code == 0 else np.nan for k, v in self._max_metrics.items()],
      name  = "Value"                                                                     ,
      index = self._max_metrics.keys()                                                    ,
    )
