"""
Epsilon-constraint optimization.
"""

import numpy  as np
import pandas as pd

from collections    import namedtuple
from scipy.optimize import fmin_slsqp


Optimum = namedtuple(
  "Optimum",
  ["exit_code", "exit_message", "amounts", "metrics"]
)
"""
Named tuple type for optimization results.
"""


class EpsilonConstraintOptimizer:
  """
  An epsilon-constration multi-objective optimizer.

  Attributes
  ----------
  evaluator : tyche.Evaluator
    The technology evaluator.
  scale : float
    The scaling factor for output.
  """

  def __init__(self, evaluator, scale = 1e6):
    """
    Parameters
    ----------
    evaluator : tyche.Evaluator
      The technology evaluator.
    scale : float
      The scaling factor for output.
    """
    
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
    """
    Maximize the objective function.

    Parameters
    ----------
    metric : str
      Name of metric to maximize.
    max_amount : DataFrame
      Maximum investment amounts by R&D category (defined in investments data)
      and maximum metric values
    total_amount : float
      Upper limit on total investments summed across all R&D categories.
    min_metric : DataFrame
      Lower limits on all metrics.
    statistic : function
      Summary statistic used on the sample evaluations; the metric measure that
      is fed to the optimizer.
    initial : array of float
      Initial value of decision variable(s) fed to the optimizer.
    tol : float
      Search tolerance fed to the optimizer.
    maxiter : int
      Maximum number of iterations the optimizer is permitted to execute.
    verbose : int
      Verbosity level returned by the optimizer and this outer function.
    """

    # get location index of metric
    i = np.where(self.evaluator.metrics == metric)[0][0]

    # if custom upper limits on investment amounts by category have not been
    # defined, get the upper limits from self.evaluator
    if max_amount is None:
      max_amount = self.evaluator.max_amount.Amount

    # scale the upper limits on investment amounts by category down such that
    # variables and constraints remain on approximately the same range
    bounds = [(0, x) for x in max_amount / self.scale]

    # define a function that will construct the investment constraint for the
    # optimizer, in the correct format
    def g(x):

      # create container for the constraints with a dummy value
      constraints = [1]

      # if the upper limit on total investments has been defined,
      if total_amount is not None:

        # scale the upper limit on investments (see line 107)
        limit = total_amount / self.scale

        # sum across all decision variable values (investment amounts) fed to
        # this function
        value = sum(x)

        # if the verbose parameter is defined as greater than three
        if verbose >= 3:

          # print the investment amounts, the RHS of the investment constraint,
          # the LHS of the investment constraint, and a Boolean indicating
          # whether the investment constraint is met
          print(x, limit, value, value <= limit)

        # update the constraint container with the LHS value of the
        # investment constraint as a <= 0 inequality constraint
        constraints = [limit - value]

      # exit the total_amount IF statement

      # if lower limits on metrics have been defined,
      if min_metric is not None:

        # loop through all available metrics
        for index, limit in min_metric.iteritems():

          # get location index of the current metric
          j = np.where(self.evaluator.metrics == index)[0][0]

          # @todo what on earth is this doing
          value = - self._f(statistic, verbose)(x)[j]

          # if the verbose parameter is defined and is greater than 3,
          if verbose >= 3:

            # print the decision variable values, the constraint RHS, the
            # constraint LHS, and a Boolean indicating whether the constraint
            # is met
            print(x, limit, value, value >= limit)

          # append the existing constraints container with the value of the
          # current metric constraint
          # as the loop executes, one constraint per metric will be added to the
          # container
          constraints += [value - limit]

      return constraints

    # if no initial decision variable values have been defined,
    if initial is None:

      # start the optimizer off at 10% of the upper limit on the decision
      # variable values
      initial = max_amount.values / 10

    # run the optimizer
    result = fmin_slsqp(
      self._fi(i, statistic, verbose), # callable function that returns the scalar objective function value
      initial / self.scale , # scaled initial guess values for decision variables (investment amounts, metrics)
      f_ieqcons   = g      , # list of functions that return inequality constraints in the form const >= 0
      bounds      = bounds , # upper and lower bounds on decision variables
      iter        = maxiter, # number of times fmin_slsqp is permitted to iterate
      acc         = tol    , # requested accuracy of optimal solution
      iprint      = verbose, # how much information fmin_slsqp returns
      full_output = True   , # return final objective function value and summary information
    )

    # calculate the scaled decision variable values that optimize the objective function
    x = pd.Series(self.scale * result[0], name = "Amount", index = self.evaluator.max_amount.index)

    # evaluate the chosen statistic for the scaled decision variable values
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
    """
    Maximum value of metrics.

    Parameters
    ----------
    max_amount : DataFrame
      The maximum amounts that can be invested in each category.
    total_amount : float
      The maximum amount that can be invested *in toto*.
    min_metric : DataFrame
      The minimum constraint for each metric.
    statistic : function
      The statistic used on the sample evaluations.
    initial : array of float
      The initial value for the search.
    tol : float
      The search tolerance.
    maxiter : int
      The maximum iterations for the search.
    verbose : int
      Verbosity level.
    """

    self._max_metrics = {
      metric : self.maximize(metric, max_amount, total_amount, None, statistic, None, tol, maxiter, verbose)
      for metric in self.evaluator.metrics
    }
    return pd.Series(
      [v.metrics[k] if v.exit_code == 0 else np.nan for k, v in self._max_metrics.items()],
      name  = "Value"                                                                     ,
      index = self._max_metrics.keys()                                                    ,
    )
