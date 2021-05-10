"""
Epsilon-constraint optimization.
"""

import numpy  as np
import pandas as pd
import time

from pymoo.model.problem import FunctionalProblem
from pymoo.algorithms.nsga2 import NSGA2
from pymoo.algorithms.so_de import DE
from pymoo.factory import get_sampling, get_crossover, get_mutation
from pymoo.util.termination.f_tol import MultiObjectiveSpaceToleranceTermination
from pymoo.optimize import minimize

from collections    import namedtuple
from scipy.optimize import fmin_slsqp, differential_evolution, shgo
from scipy.optimize import NonlinearConstraint

from mip import Model, MINIMIZE, BINARY, xsum

Optimum = namedtuple(
  "Optimum",
  ["exit_code", "exit_message", "amounts", "metrics", "solve_time"]
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
      Defaults to 0.
      verbose = 0     No messages
      verbose = 1     Summary message when fmin_slsqp completes
      verbose = 2     Status of each algorithm iteration and summary message
      verbose = 3     Investment constraint status, metric constraint status,
                      status of each algorithm iteration, and summary message
      verbose > 3     All metric values, decision variable values, investment
                      constraint status, metric constraint status, status of
                      each algorithm iteration, and summary message
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

        if verbose == 3:
          print('Investment limit: ', np.round(limit, 3),
                ' Investment value: ', np.round(value, 3),
                ' Constraint met: ', value <= limit)
        elif verbose > 3:
          print('Decision variable values: ', np.round(x, 3),
                ' Investment limit: ', np.round(limit, 3),
                ' Investment value:  ', np.round(value, 3),
                '  Constraint met: ', value <= limit)

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

          if verbose == 3:
            print('Metric limit:     ', np.round(limit, 3),
                  '  Metric value:     ', np.round(value, 3),
                  ' Constraint met: ', value >= limit)
          elif verbose > 3:
            print('Decision variable values: ', np.round(x, 3),
                  ' Metric limit:     ', np.round(limit, 3),
                  '  Metric value:      ', np.round(value, 3),
                  ' Constraint met: ', value >= limit)

          # append the existing constraints container with the LHS value of the
          # current metric constraint formulated as >= 0
          # as the loop executes, one constraint per metric will be added to
          # the container
          constraints += [value - limit]

      return constraints

    # if no initial decision variable values have been defined,
    if initial is None:

      # start the optimizer off at 10% of the upper limit on the decision
      # variable values
      initial = max_amount.values / 10

    # note time when algorithm started
    start = time.time()

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

    elapsed = time.time() - start

    # calculate the scaled decision variable values that optimize the
    # objective function
    x = pd.Series(self.scale * result[0], name = "Amount",
                  index = self.evaluator.max_amount.index)

    # evaluate the chosen statistic for the scaled decision variable values
    y = evaluate(x)
    
    return Optimum(
      exit_code    = result[3],
      exit_message = result[4],
      amounts      = x        ,
      metrics      = y        ,
      solve_time   = elapsed
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
    Maximize the objective function using the differential_evoluation
     algorithm.

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
      Verbosity level returned by this outer function and the
       differential_evolution algorithm.
      verbose = 0     No messages
      verbose = 1     Objective function value at every algorithm iteration
      verbose = 2     Investment constraint status, metric constraint status,
                      and objective function value
      verbose = 3     Decision variable values, investment constraint status,
                      metric constraint status, and objective function value
      verbose > 3     All metric values, decision variable values, investment
                      constraint status, metric constraint status, and
                      objective function value
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

        if verbose == 2:
          print('Investment limit: ', np.round(limit, 3),
                ' Investment value: ', np.round(value, 3),
                ' Constraint met: ', value <= limit)
        elif verbose > 2:
          print('Decision variable values: ', np.round(x, 3),
                ' Investment limit: ', np.round(limit, 3),
                ' Investment value: ', np.round(value, 3),
                ' Constraint met: ', value <= limit)

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

          if verbose == 2:
            print('Metric limit:     ', np.round(limit, 3),
                  '  Metric value:     ', np.round(value, 3),
                  ' Constraint met: ', value <= limit)
          elif verbose > 2:
            print('Decision variable values: ', np.round(x, 3),
                  ' Metric limit:     ', np.round(limit, 3),
                  '  Metric value:      ', np.round(value, 3),
                  ' Constraint met: ', value <= limit)

          # append the existing constraints container with the LHS value of the
          # current metric constraint formulated as >= 0
          # as the loop executes, one constraint per metric will be added to
          # the container
          constraints += [value - limit]

      return np.array(constraints)

    # note time when algorithm started
    start = time.time()

    # run the optimizer
    result = differential_evolution(
      self._fi(i, evaluate, verbose), # callable function that returns the scalar objective function value
      bounds=var_bounds,  # upper and lower bounds on decision variables
      strategy=strategy, # defines differential evolution strategy to use
      maxiter=maxiter, # default maximum iterations to execute
      tol=tol, # default tolerance on returned optimum
      seed=seed, # specify a random seed for reproducible optimizations
      disp=verbose>=1, # print objective function at every iteration
      init=init, # type of population initialization
      # @note ignore this warning for now
      constraints=NonlinearConstraint(g, 0.0, np.inf))

    elapsed = time.time() - start

    if result.success:
      # calculate the scaled decision variable values that optimize the
      # objective function
      x = pd.Series(self.scale * result.x, name="Amount",
                    index=self.evaluator.max_amount.index)

      # evaluate the chosen statistic for the scaled decision variable values
      y = self.evaluator.evaluate_statistic(x, statistic)

      return Optimum(
        exit_code=result.success,
        exit_message=result.message,
        amounts=x,
        metrics=y,
        solve_time=elapsed
      )
    else:
      return result, elapsed


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
    Maximize the objective function using the shgo global optimization
    algorithm.

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
      Summary metric_statistic used on the sample evaluations; the metric
      measure that is fed to the optimizer.
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
      Verbosity level returned by this outer function and the SHGO algorithm.
      verbose = 0     No messages
      verbose = 1     Convergence messages from SHGO algorithm
      verbose = 2     Investment constraint status, metric constraint status,
                      and convergence messages
      verbose = 3     Decision variable values, investment constraint status,
                      metric constraint status, and convergence messages
      verbose > 3     All metric values, decision variable values, investment
                      constraint status, metric constraint status, and
                      convergence messages
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

        if verbose == 2:
          # print the investment limit (RHS of constraint), the investment
          # amount (LHS of constraint), and a Boolean indicating whether the
          # investment constraint is met
          print('Investment limit: ', np.round(inv_limit, 3),
                ' Investment value: ', np.round(inv_value, 3),
                ' Constraint met: ', inv_value <= inv_limit)
        # if verbose is greater than or equal to three
        elif verbose > 2:
          # also print the decision variable values
          print('Decision variable values: ', np.round(x, 3),
                ' Investment limit: ', np.round(inv_limit, 3),
                ' Investment value:  ', np.round(inv_value, 3),
                '  Constraint met: ', inv_value <= inv_limit)

        return inv_limit - inv_value

      # update the constraint container with the LHS value of the
      # investment constraint as a <= 0 inequality constraint
      constraints += [{'type': 'ineq', 'fun': g_inv}]

    # exit the total_amount IF statement

    def make_g_metric(evaluate, metric_index, metric_limit):

      j = np.where(self.evaluator.metrics == metric_index)[0][0]

      def g_metric_fn(x):
        met_value = - self._f(evaluate, verbose)(x)[j]

        if verbose == 2:
          print('Metric limit:     ', np.round(metric_limit, 3),
                '  Metric value:     ', np.round(met_value, 3),
                ' Constraint met: ', met_value >= metric_limit)
        elif verbose > 2:
          print('Decision variable values: ', np.round(x, 3),
                ' Metric limit:     ', np.round(metric_limit, 3),
                '  Metric value:      ', np.round(met_value, 3),
                ' Constraint met: ', met_value >= metric_limit)

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
                'maxiter': maxiter,
                'disp': verbose >= 1}

    # note time when algorithm started
    start = time.time()

    result = shgo(
      self._fi(i, evaluate, verbose), # callable function that returns the scalar objective function value
      bounds=bounds,  # upper and lower bounds on decision variables
      constraints=constraints,
      options=opt_dict, # dictionary of options including max iters
      sampling_method=sampling_method #sampling method (sobol or simplicial)
    )

    elapsed = time.time() - start

    if result.success:
      # calculate the scaled decision variable values that optimize the
      # objective function
      x = pd.Series(self.scale * result.x, name="Amount",
                    index=self.evaluator.max_amount.index)

      # evaluate the chosen metric_statistic for the scaled decision variable values
      y = evaluate(x)
      return Optimum(
        exit_code=result.success,
        exit_message=result.message,
        amounts=x,
        metrics=y,
        solve_time=elapsed
      )
    else:
      return result, elapsed


  def maximize_pymoo(
          self,
          metric,
          max_amount=None,
          total_amount=None,
          min_metric=None,
          statistic=np.mean,
          seed=1,
          algo='NSGA2',
          pop_size=40,
          n_offsprings=None,
          tol=1e-2,
          maxiter=50,
          verbose=0,
  ):
    """
    Maximize the objective function using an algorithm from the pymoo library.

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
    seed : int
      Sets the random seed for optimization. Defaults to 1. Not setting this
      parameter means the solutions will not be reproducible.
    algo : str
      Name of optimization algorithm to use. Defaults to NSGA-II. Current
      options are: NSGA-II ('NSGA2'), differential evolution ('DE').
    pop_size : int
      Number of solutions to evolve. Defaults to 40.
    n_offsprings : int
      Number of offspring created in a generation. Defaults to None, which sets
      n_offsprings equal to pop_size (internal to the algorithm).
    tol : float
      Search tolerance fed to the algorithm. The algorithm terminates once tol
      is satisfied OR when the maximum generations (maxiter) is reached,
      whichever comes first.
    maxiter : int
      Maximum number of iterations the optimizer is permitted to execute. The
      algorithm terminates once maxiter is reached OR when tol is satisified,
      whichever comes first.
    verbose : int
      Verbosity level returned by the optimizer and this outer function.
      Defaults to 0.
      verbose = 0     No messages
      verbose = 1     Output from algorithm
      verbose = 2     Investment constraint status, metric constraint status,
                      and output from algorithm
      verbose = 3     Decision variable values, investment constraint status,
                      metric constraint status, and output from algorithm
      verbose > 3     All metric values, decision variable values, investment
                      constraint status, metric constraint status, and output
                      from algorithm
    """

    # get location index of metric
    i = np.where(self.evaluator.metrics == metric)[0][0]

    # if custom upper limits on investment amounts by category have not been
    # defined, get the upper limits from self.evaluator
    if max_amount is None:
      max_amount = self.evaluator.max_amount.Amount

    # scale the upper limits on investment amounts by category down such that
    # variables and constraints remain on approximately the same range
    bounds_lower = np.repeat(0, len(max_amount))
    # @todo check that xu is dtype np.array
    bounds_upper = max_amount / self.scale

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

        if verbose == 2:
          # print the investment limit (RHS of constraint), the investment
          # amount (LHS of constraint), and a Boolean indicating whether the
          # investment constraint is met
          print('Investment limit: ', np.round(inv_limit, 3),
                ' Investment value: ', np.round(inv_value, 3),
                ' Constraint met: ', inv_value <= inv_limit)
        # if verbose is greater than or equal to three
        elif verbose > 2:
          # also print the decision variable values
          print('Decision variable values: ', np.round(x, 3),
                ' Investment limit: ', np.round(inv_limit, 3),
                ' Investment value:  ', np.round(inv_value, 3),
                '  Constraint met: ', inv_value <= inv_limit)

        return inv_limit - inv_value

      # update the constraint container with the LHS value of the
      # investment constraint as a <= 0 inequality constraint
      constraints += [g_inv]

    # exit the total_amount IF statement

    def make_g_metric(metric_statistic, metric_index, metric_limit):

      j = np.where(self.evaluator.metrics == metric_index)[0][0]

      def g_metric_fn(x):
        met_value = - self._f(metric_statistic, verbose)(x)[j]

        if verbose == 2:
          print('Metric limit:     ', np.round(metric_limit, 3),
                '  Metric value:     ', np.round(met_value, 3),
                ' Constraint met: ', met_value >= metric_limit)
        elif verbose > 2:
          print('Decision variable values: ', np.round(x, 3),
                ' Metric limit:     ', np.round(metric_limit, 3),
                '  Metric value:      ', np.round(met_value, 3),
                ' Constraint met: ', met_value >= metric_limit)

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
        g_metric = make_g_metric(statistic, index, limit)
        constraints += [g_metric]

    _problem = FunctionalProblem(
      len(max_amount),
      objs=self._fi(i, statistic, verbose),
      constr_ieq=constraints,
      xl=bounds_lower,
      xu=bounds_upper
    )

    # initialize algorithm
    if algo == 'NSGA2':
      _algorithm = NSGA2(
        pop_size=pop_size,
        n_offsprings=n_offsprings,
        sampling=get_sampling("real_random"),
        crossover=get_crossover("real_sbx", prob=0.9, eta=15),
        mutation=get_mutation("real_pm", eta=20),
        eliminate_duplicates=True
      )
    elif algo == 'DE': #@todo swap DE for a reproducible algorithm
      _algorithm = DE(
        pop_size=pop_size
      )
    else:
      raise NotImplementedError

    # specify termination criteria
    _termination = MultiObjectiveSpaceToleranceTermination(
      tol=tol,
      n_max_gen=maxiter
    )

    # run the optimizer
    _pymoo_result = minimize(
      _problem,
      _algorithm,
      _termination,
      seed=seed,
      save_history=True,
      verbose=verbose>0
    )

    # extract optimal decision variable values
    result = [_pymoo_result.X]

    # calculate the scaled decision variable values that optimize the
    # objective function
    # @todo check that this evaluates correctly
    x = pd.Series(self.scale * result[0], name="Amount",
                  index=self.evaluator.max_amount.index)

    # evaluate the chosen statistic for the scaled decision variable values
    y = self.evaluator.evaluate_statistic(x, statistic)

    return Optimum(
      exit_code=_pymoo_result.success,
      exit_message=_pymoo_result.message,
      amounts=x,
      metrics=y,
      solve_time=_pymoo_result.exec_time
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
    @todo update max_metrics to include additional algorithms
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
      metric : self.maximize_slsqp(metric, max_amount, total_amount,
                                   None, statistic, None,
                                   tol, maxiter, verbose)
      for metric in self.evaluator.metrics
    }
    return pd.Series(
      [v.metrics[k] if v.exit_code == 0
       else np.nan for k, v in self._max_metrics.items()],
      name  = "Value",
      index = self._max_metrics.keys(),
    )


  def pwlinear_milp(
          self,
          metric,
          max_amount   = None   ,
          total_amount = None   ,
          min_metric   = None   ,
          statistic    = np.mean,
          verbose      = 0      ,
  ):
    """
    Maximize the objective function using a piecewise linear
    representation to create a mixed integer linear program.

    Parameters
    ----------
    metric : str
      Name of metric to maximize
    max_amount : DataFrame
      Maximum investment amounts by R&D category (defined in investments data)
      and maximum metric values
    total_amount : float
      Upper limit on total investments summed across all R&D categories.
    min_metric : DataFrame
      Lower limits on all metrics
    statistic : function
      Summary statistic (metric measure) fed to evaluator_corners_wide method
      in Evaluator
    total_amount : float
      Upper limit on total investments summed across all R&D categories
    verbose : int
      A value greater than zero will save the optimization model as a .lp file

    Returns
    -------
    Optimum : NamedTuple
      exit_code
      exit_message
      amounts (None, if no solution found)
      metrics (None, if no solution found)
      solve_time
    """

    # investment categories
    _categories = self.evaluator.categories

    # metric to optimize
    _obj_metric = metric

    # if custom upper limits on investment amounts by category have not been
    # defined, get the upper limits from self.evaluator
    if max_amount is None:
      max_amount = self.evaluator.max_amount.Amount

    # get data frame of elicited metric values by investment level combinations
    _wide = self.evaluator.evaluate_corners_wide(statistic).reset_index()

    # (combinations of) Investment levels
    inv_levels = _wide.loc[:, _categories].values.tolist()

    # Elicited metric values - for objective function
    m = _wide.loc[:, _obj_metric].values.tolist()

    # all metric values - for calculating optimal metrics
    _metric_data = _wide.copy().drop(columns=_categories).values.tolist()

    # list of metrics
    _all_metrics = _wide.copy().drop(columns=_categories).columns.values

    # Number of investment level combinations/metric values
    I = len(inv_levels)

    # instantiate MILP model
    _model = Model(sense=MINIMIZE)

    bin_vars = []
    lmbd_vars = []

    # create binary variables
    for i in range(I - 1):
      _name = 'y' + '_' + str(i)
      bin_vars += [_model.add_var(name=_name, var_type=BINARY)]
      del _name

    # create continuous variables
    for i in range(I):
      _name = 'lmbd' + '_' + str(i)
      lmbd_vars += [_model.add_var(name=_name, lb=0.0, ub=1.0)]
      del _name

    # create budget constraints

    # total budget constraint - only if total_amount is an input
    if total_amount is not None:
      _model += xsum(lmbd_vars[i] * inv_levels[i][j]
                      for i in range(I)
                      for j in range(len(inv_levels[i]))) <= total_amount,\
                 'Total_Budget'

    # constraint on budget for each investment category
    # this is either fed in as an argument or pulled from evaluator
    for j in range(len(_categories)):
      _model += xsum(lmbd_vars[i] * [el[j] for el in inv_levels][i]
                      for i in range(I)) <= max_amount[j],\
                 'Budget_for_' + _categories[j].replace(' ', '')

    # define metric constraints if lower limits on metrics have been defined
    if min_metric is not None:

      # loop through list of metric minima
      for index, limit in min_metric.iteritems():

        # add minimum-metric constraint on the lambda variables
        _model += xsum(lmbd_vars[i] * _wide.loc[:,index].values.tolist()[i]
                       for i in range(I)) >= limit,\
                  'Minimum_' + index

    # convexity constraint for continuous variables
    _model += sum(lmbd_vars) == 1, 'Lambda_Sum'

    # constrain binary variables such that only one interval can be active
    # at a time
    _model += sum(bin_vars) == 1, 'Binary_Sum'

    # constraint on lambda and binary variables
    for i in range(I - 1):
      _model += bin_vars[i] <= lmbd_vars[i] + lmbd_vars[i + 1],\
                 'Interval_Constraint_' + str(i)

    # objective function
    _model.objective = xsum(m[i] * lmbd_vars[i] for i in range(I))

    # save a copy of the model in LP format
    if verbose > 0:
      _model.write('model.lp')
    else:
      # if the verbose parameter is 0, the MIP solver does not print output
      _model.verbose = 0

    # note time when algorithm started
    _start = time.time()

    # find optimal solution
    _solution = _model.optimize()

    elapsed = time.time() - _start

    # if a feasible solution was found, calculate the optimal investment values
    # and return a populated Optimum tuple
    if _model.status.value == 0:
      # get the optimal variable values as two lists
      lmbd_opt = []
      y_opt = []

      for v in _model.vars:
        if 'lmbd' in v.name:
          lmbd_opt += [v.x]
        elif 'y' in v.name:
          y_opt += [v.x]

      inv_levels_opt = []

      # calculate the optimal investment values
      for i in range(len(_categories)):
        inv_levels_opt += [sum([lmbd_opt[j] * [el[i] for el in inv_levels][j]
                                for j in range(len(lmbd_opt))])]

      # construct a Series of optimal investment levels
      x = pd.Series(inv_levels_opt, name="Amount",
                    index=self.evaluator.max_amount.index)

      metrics_opt = []

      # calculate optimal values of all metrics
      for i in range(len(_all_metrics)):
        metrics_opt += [sum([lmbd_opt[i] * [el[i] for el in _metric_data][j]
                             for j in range(len(lmbd_opt))])]

      y = pd.Series(metrics_opt, name="Value",
                    index=_all_metrics)

      return Optimum(
        exit_code=_model.status.value,
        exit_message=_model.status,
        amounts=x,
        metrics=y,
        solve_time=elapsed
      )
    # if no feasible solution was found, return a partially empty Optimum tuple
    else:
      return Optimum(
        exit_code=_model.status.value,
        exit_message=_model.status,
        amounts=None,
        metrics=None,
        solve_time=elapsed
      )