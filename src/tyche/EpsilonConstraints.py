"""
Epsilon-constraint optimization.
"""

import numpy  as np
import pandas as pd

from collections    import namedtuple
from scipy.optimize import fmin_slsqp, differential_evolution, shgo
from scipy.optimize import NonlinearConstraint


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

  def _f(self, evaluate, verbose = 0):
    def f(x):
      xx = pd.Series(self.scale * x, name = "Amount", index = self.evaluator.max_amount.index)
      yy = evaluate(xx)
      if verbose > 2:
        print ('scaled decision variables: ', xx.values, '\n')
        print('metric statistics: ', yy.values, '\n')
        # return the negative s.t. this function can be called as-is to maximize
        # the objective function
        # (all algorithms minimize, minimizing the negative is maximizing)
      return - yy
    return f

  def _fi(self, i, evaluate, verbose = 0):
    return lambda x: self._f(evaluate, verbose)(x)[i]

  def maximize_slsqp(
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
    Maximize the objective function using the fmin_slsqp algorithm.

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

    # create a functio to evaluate the statistic
    evaluate = self.evaluator.make_statistic_evaluator(statistic)

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
        # investment constraint as a >= 0 inequality constraint
        constraints = [limit - value]

      # exit the total_amount IF statement

      # if lower limits on metrics have been defined,
      if min_metric is not None:

        # loop through all available metrics
        for index, limit in min_metric.iteritems():

          # get location index of the current metric
          j = np.where(self.evaluator.metrics == index)[0][0]

          value = - self._f(evaluate, verbose)(x)[j]

          # if the verbose parameter is defined and is greater than 3,
          if verbose >= 3:

            # print the decision variable values, the constraint RHS, the
            # constraint LHS, and a Boolean indicating whether the constraint
            # is met
            print(x, limit, value, value >= limit)

          # append the existing constraints container with the LHS value of the
          # current metric constraint formulated as >= 0
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
      self._fi(i, evaluate, verbose), # callable function that returns the scalar objective function value
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
    y = evaluate(x)
    
    return Optimum(
      exit_code    = result[3],
      exit_message = result[4],
      amounts      = x        ,
      metrics      = y        ,
    )


  def maximize_diffev(
          self,
          metric, # objective function
          max_amount=None, # upper investment limit
          total_amount=None, # total investments
          min_metric=None, # lower metric limits
          statistic=np.mean, # how to quantify the metrics
          strategy='best1bin',
          seed=2, # random seed
          tol=0.01, #looser tolerance means greater chance of convergence
          maxiter=75, #this algorithm tends to require more iterations
          init='latinhypercube',
          verbose=0, # how much to report back during execution
  ):
    """
    Maximize the objective function using the differential_evoluation algorithm.

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
    strategy : str
      Which differential evolution strategy to use. 'best1bin' is the default.
      See algorithm docs for full list.
    seed : int
      Sets the random seed for optimization by creating a new `RandomState`
      instance. Defaults to 1. Not setting this parameter means the solutions
      will not be reproducible.
    init : str or array-like
      Type of population initialization. Default is Latin hypercube;
      alternatives are 'random' or specifying every member of the initial
      population in an array of shape (popsize, len(variables)).
    tol : float
      Relative tolerance for convergence
    maxiter : int
      Upper limit on generations of evolution (analogous to algorithm
      iterations)
    verbose : int
      Verbosity level returned by this outer function.
      differential_evolution has no verbosity parameter
    """

    # create a functio to evaluate the statistic
    evaluate = self.evaluator.make_statistic_evaluator(statistic)

    # get location index of metric
    i = np.where(self.evaluator.metrics == metric)[0][0]

    # if custom upper limits on investment amounts by category have not been
    # defined, get the upper limits from self.evaluator
    if max_amount is None:
      max_amount = self.evaluator.max_amount.Amount

    # scale the upper limits on investment amounts by category down such that
    # variables and constraints remain on approximately the same range
    var_bounds = [(0, x) for x in max_amount / self.scale]

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
        # investment constraint as a >= 0 inequality constraint
        constraints = [limit - value]

      # exit the total_amount IF statement

      # if lower limits on metrics have been defined,
      if min_metric is not None:

        # loop through all available metrics
        for index, limit in min_metric.iteritems():

          # get location index of the current metric
          j = np.where(self.evaluator.metrics == index)[0][0]

          # calculate the summary statistic on the current metric
          value = - self._f(evaluate, verbose)(x)[j]

          # if the verbose parameter is defined and is greater than 3,
          if verbose >= 3:

            # print the decision variable values, the constraint RHS, the
            # constraint LHS, and a Boolean indicating whether the constraint
            # is met
            print(x, limit, value, value >= limit)

          # append the existing constraints container with the LHS value of the
          # current metric constraint formulated as >= 0
          # as the loop executes, one constraint per metric will be added to the
          # container
          constraints += [value - limit]

      return np.array(constraints)

    # run the optimizer
    result = differential_evolution(
      self._fi(i, evaluate, verbose), # callable function that returns the scalar objective function value
      bounds=var_bounds,  # upper and lower bounds on decision variables
      strategy=strategy, # defines differential evolution strategy to use
      maxiter=maxiter, # default maximum iterations to execute
      tol=tol, # default tolerance on returned optimum
      seed=seed, # specify a random seed for reproducible optimizations
      init=init, # type of population initialization
      constraints=NonlinearConstraint(g, 0.0, np.inf)) # @note ignore this warning for now

    # calculate the scaled decision variable values that optimize the objective function
    x = pd.Series(self.scale * result.x, name="Amount",
                  index=self.evaluator.max_amount.index)

    # evaluate the chosen statistic for the scaled decision variable values
    y = evaluate(x)

    # differential_evolution doesn't return exit_code or exit_message, only
    # decision variable values, objective function value, and number of
    # iterations ("nit")
    return Optimum(
      exit_code=result.success,
      exit_message=result.message,
      amounts=x,
      metrics=y,
    )

  def maximize_shgo(
          self,
          metric,
          max_amount=None,
          total_amount=None,
          min_metric=None,
          statistic=np.mean,
          tol=1e-8,
          maxiter=50,
          sampling_method='simplicial',
          verbose=0,
  ):
    """
    Maximize the objective function using the shgo global optimization algorithm.

    Parameters
    ----------
    metric : str
      Name of metric to maximize.
    max_amount : DataFrame
      Maximum investment amounts by R&D category (defined in investments data)
      and maximum metric values
    total_amount : float
      Upper metric_limit on total investments summed across all R&D categories.
    min_metric : DataFrame
      Lower limits on all metrics.
    statistic : function
      Summary metric_statistic used on the sample evaluations; the metric measure that
      is fed to the optimizer.
    tol : float
      Objective function tolerance in stopping criterion.
    maxiter : int
      Upper metric_limit on iterations that can be performed
    sampling_method : str
      Allowable values are 'sobol and 'simplicial'. Simplicial is default, uses
      less memory, and guarantees convergence (theoretically). Sobol is faster,
      uses more memory and does not guarantee convergence. Per documentation,
      Sobol is better for "easier" problems.
    verbose : int
      Verbosity level returned by this outer function.
    """

    # create a functio to evaluate the statistic
    evaluate = self.evaluator.make_statistic_evaluator(statistic)

    # get location metric_index of metric
    i = np.where(self.evaluator.metrics == metric)[0][0]

    # if custom upper limits on investment amounts by category have not been
    # defined, get the upper limits from self.evaluator
    if max_amount is None:
      max_amount = self.evaluator.max_amount.Amount

    # scale the upper limits on investment amounts by category down such that
    # variables and constraints remain on approximately the same range
    bounds = [(0, x) for x in max_amount / self.scale]

    # define a dictionary of functions that define individual constraints and
    # their types (all inequalities)

    # initialize constraints container
    constraints = []

    # construct the investment constraint
    # if the upper metric_limit on total investments has been defined,
    if total_amount is not None:

      def g_inv(x):
        # scale the upper metric_limit on investments
        inv_limit = total_amount / self.scale

        # sum across all decision variable values (investment amounts) fed to
        # this function
        inv_value = sum(x)

        # if the verbose parameter is defined as greater than three
        if verbose >= 3:
          # print the investment amounts, the RHS of the investment constraint,
          # the LHS of the investment constraint, and a Boolean indicating
          # whether the investment constraint is met
          print('g_inv: ', x, inv_limit, inv_value, inv_value <= inv_limit, '\n')

        return inv_limit - inv_value

      # update the constraint container with the LHS value of the
      # investment constraint as a <= 0 inequality constraint
      constraints += [{'type': 'ineq', 'fun': g_inv}]

    # exit the total_amount IF statement

    def make_g_metric(evaluate, metric_index, metric_limit):

      j = np.where(self.evaluator.metrics == metric_index)[0][0]

      def g_metric_fn(x):
        met_value = - self._f(evaluate, verbose)(x)[j]

        # if the verbose parameter is defined and is greater than 3,
        if verbose >= 3:
          # print the decision variable values, the constraint RHS, the
          # constraint LHS, and a Boolean indicating whether the constraint
          # is met
          print('g_metric: ', x, metric_limit, met_value, met_value >= metric_limit, '\n')

        return met_value - metric_limit

      return g_metric_fn

    # if lower limits on metrics have been defined,
    if min_metric is not None:

      # loop through all available metrics
      for index, limit in min_metric.iteritems():
        # append the existing constraints container with the value of the
        # current metric constraint
        # as the loop executes, one constraint per metric will be added to the
        # container
        g_metric = make_g_metric(evaluate, limit)
        constraints += [{'type': 'ineq', 'fun': g_metric}]

    opt_dict = {'f_tol': tol,
                'maxiter': maxiter}

    result = shgo(
      self._fi(i, evaluate, verbose), # callable function that returns the scalar objective function value
      bounds=bounds,  # upper and lower bounds on decision variables
      constraints=constraints,
      options=opt_dict, # dictionary of options including max iters
      sampling_method=sampling_method #sampling method (sobol or simplicial)
    )

    if result.success:
      # calculate the scaled decision variable values that optimize the objective function
      x = pd.Series(self.scale * result.x, name="Amount", index=self.evaluator.max_amount.index)

      # evaluate the chosen metric_statistic for the scaled decision variable values
      y = evaluate(x)

      return Optimum(
        exit_code=result.success,
        exit_message=result.message,
        amounts=x,
        metrics=y,
      )
    else:
      return result


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
    @todo update to include additional algorithms
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
      metric : self.maximize_slsqp(metric, max_amount, total_amount, None, statistic, None, tol, maxiter, verbose)
      for metric in self.evaluator.metrics
    }
    return pd.Series(
      [v.metrics[k] if v.exit_code == 0 else np.nan for k, v in self._max_metrics.items()],
      name  = "Value"                                                                     ,
      index = self._max_metrics.keys()                                                    ,
    )
