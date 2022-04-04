"""
Epsilon-constraint optimization.
"""

import numpy  as np
import pandas as pd
import time

from collections    import namedtuple
from scipy.optimize import fmin_slsqp, differential_evolution, shgo
from scipy.optimize import NonlinearConstraint

from mip import Model, MAXIMIZE, MINIMIZE, BINARY, xsum

Optimum = namedtuple(
  "Optimum",
  ["exit_code", "exit_message", "amounts", "metrics", "solve_time", "opt_sense"]
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

    # Create and store the set of valid optimization sense parameters for use
    # in optimization methods
    self.valid_sense = {'min', 'max'}

  def _f(self, evaluate, sense, verbose = 0):
    def f(x):
      xx = pd.Series(self.scale * x, name = "Amount", index = self.evaluator.max_amount.index)
      yy = evaluate(xx)
      if verbose > 2:
        print ('scaled decision variables: ', xx.values, '\n')
        print('metric statistics: ', yy.values, '\n')
      # fmin_slsqp always minimizes the objective function
      # if this method is maximizing, multiply the objective function by -1.0 to
      # maximize by minimizing the negative
      # if this method is minimizing, keep the objective function as is to
      # minimize
      if sense == 'max':
        _obj_mult = -1.0
      else:
        _obj_mult = 1.0
      return _obj_mult * yy
    return f

  def _fi(self, i, evaluate, sense, verbose = 0):
    return lambda x: self._f(evaluate, sense, verbose)(x)[i]

  def opt_slsqp(
    self                  ,
    metric                ,
    sense        = None   ,
    max_amount   = None   ,
    total_amount = None   ,
    eps_metric   = None   ,
    statistic    = np.mean,
    initial      = None   ,
    tol          = 1e-8   ,
    maxiter      = 50     ,
    verbose      = 0      ,
  ):
    """
    Optimize the objective function using the fmin_slsqp algorithm.

    Parameters
    ----------
    metric : str
      Name of metric to maximize.
    sense : str
      Optimization sense ('min' or 'max'). If no value is provided to
      this method, the sense value used to create the
      EpsilonConstraintOptimizer object is used instead.
    max_amount : DataFrame
      Maximum investment amounts by R&D category (defined in investments data)
      and maximum metric values
    total_amount : float
      Upper limit on total investments summed across all R&D categories.
    eps_metric : Dict
      RHS of the epsilon constraint(s) on one or more metrics. Keys are metric
      names, and the values are dictionaries of the form
      {'limit': float, 'sense': str}. The sense defines whether the epsilon
      constraint is a lower or an upper bound, and the value must be either
      'upper' or 'lower'.
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

    # If no optimization sense is provided, use the default value from self.
    # If an optimization sense IS provided, overwrite the default value with
    # the provided value.
    # _sense is the parameter used only in this method
    if sense is None:
      print('opt_slsqp: No optimization sense specified; maximizing objective function')
      sense = 'max'
    else:
      if sense not in self.valid_sense:
        raise ValueError(f'opt_slsqp: sense must be one of {self.valid_sense}')

    # create a function to evaluate the statistic
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
      if eps_metric is not None:

        # loop through all available metrics
        for index, info in eps_metric.items():

          # get location index of the current metric
          j = np.where(self.evaluator.metrics == index)[0][0]
          if info['sense'] == 'lower':
            value = self._f(evaluate=evaluate,
                            sense='min',
                            verbose=verbose)(x)[j]
          elif info['sense'] == 'upper':
            value = self._f(evaluate=evaluate,
                            sense='max',
                            verbose=verbose)(x)[j]
          else:
            raise ValueError('opt_slsqp: Epsilon constraint must be upper or lower')

          if verbose == 3:
            print('Metric limit:     ', np.round(info['limit'], 3),
                  '  Metric value:     ', np.round(value, 3),
                  ' Constraint met: ', value >= info['limit'])
          elif verbose > 3:
            print('Decision variable values: ', np.round(x, 3),
                  ' Metric limit:     ', np.round(info['limit'], 3),
                  '  Metric value:      ', np.round(value, 3),
                  ' Constraint met: ', value >= info['limit'])

          # append the existing constraints container with the LHS value of the
          # current metric constraint formulated as >= 0
          # as the loop executes, one constraint per metric will be added to
          # the container
          constraints += [value - info['limit']]

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
      self._fi(i, evaluate, sense, verbose), # callable function that returns the scalar objective function value
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
      solve_time   = elapsed  ,
      opt_sense    = sense   ,
    )


  def opt_diffev(
          self                            ,
          metric                          ,
          sense         = None            ,
          max_amount    = None            ,
          total_amount  = None            ,
          eps_metric    = None            ,
          statistic     = np.mean         ,
          strategy      = 'best1bin'      ,
          seed          = 2               ,
          tol           = 0.01            ,
          maxiter       = 75              ,
          init          = 'latinhypercube',
          verbose       = 0               ,
  ):
    """
    Maximize the objective function using the differential_evoluaion algorithm.

    Parameters
    ----------
    metric : str
      Name of metric to maximize. The objective function.
    sense : str
      Optimization sense ('min' or 'max'). If no value is provided to
       this method, the sense value used to create the
       EpsilonConstraintOptimizer object is used instead.
    max_amount : DataFrame
      Maximum investment amounts by R&D category (defined in investments data)
      and maximum metric values
    total_amount : float
      Upper limit on total investments summed across all R&D categories.
    eps_metric : Dict
      RHS of the epsilon constraint(s) on one or more metrics. Keys are metric
      names, and the values are dictionaries of the form {'limit': float, 'sense': str}.
      The sense defines whether the epsilon constraint is a lower or an upper bound,
      and the value must be either 'upper' or 'lower'.
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
    # If no optimization sense is provided, use the default value from self.
    # If an optimization sense IS provided, overwrite the default value with
    # the provided value.
    # _sense is the parameter used only in this method
    if sense is None:
      print('opt_diffev: No optimization sense provided; Maximizing objective function')
      sense = 'max'
    else:
      if sense not in self.valid_sense:
        raise ValueError(f'opt_diffev: sense must be one of {self.valid_sense}')

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

      # create empty container for the constraints
      constraints = []

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
        constraints += [limit - value]

      # exit the total_amount IF statement

      # if lower limits on metrics have been defined,
      if eps_metric is not None:

        # loop through all available metrics
        for index, info in eps_metric.items():

          # get location index of the current metric
          j = np.where(self.evaluator.metrics == index)[0][0]

          # calculate the summary statistic on the current metric
          if info['sense'] == 'lower':
            value = self._f(evaluate=evaluate,
                            sense='min',
                            verbose=verbose)(x)[j]
          elif info['sense'] == 'upper':
            value = self._f(evaluate=evaluate,
                            sense='max',
                            verbose=verbose)(x)[j]
          else:
            raise ValueError('opt_diffev: Epsilon constraint must be upper or lower')

          if verbose == 3:
            print('Metric limit:     ', np.round(info['limit'], 3),
                  '  Metric value:     ', np.round(value, 3),
                  ' Constraint met: ', value <= info['limit'])
          elif verbose > 3:
            print('Decision variable values: ', np.round(x, 3),
                  ' Metric limit:     ', np.round(info['limit'], 3),
                  '  Metric value:      ', np.round(value, 3),
                  ' Constraint met: ', value <= info['limit'])

          # append the existing constraints container with the LHS value of the
          # current metric constraint formulated as >= 0
          # as the loop executes, one constraint per metric will be added to
          # the container
          constraints += [value - info['limit']]

      return np.array(constraints)

    # note time when algorithm started
    start = time.time()

    # run the optimizer
    result = differential_evolution(
      self._fi(i, evaluate, sense, verbose), # callable function that returns the scalar objective function value
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
        solve_time=elapsed,
        opt_sense=sense
      )
    else:
      return result, elapsed


  def opt_shgo(
          self                           ,
          metric                         ,
          sense            = None        ,
          max_amount       = None        ,
          total_amount     = None        ,
          eps_metric       = None        ,
          statistic        = np.mean     ,
          tol              = 0.01        ,
          maxiter          = 50          ,
          sampling_method  = 'simplicial',
          verbose          = 0           ,
  ):
    """
    Maximize the objective function using the shgo global optimization
    algorithm.

    Parameters
    ----------
    metric : str
      Name of metric to maximize.
    sense : str
      Optimization sense ('min' or 'max'). If no value is provided to
      this method, the sense value used to create the
      EpsilonConstraintOptimizer object is used instead.
    max_amount : DataFrame
      Maximum investment amounts by R&D category (defined in investments data)
      and maximum metric values
    total_amount : float
      Upper metric_limit on total investments summed across all R&D categories.
    eps_metric : Dict
      RHS of the epsilon constraint(s) on one or more metrics. Keys are metric
      names, and the values are dictionaries of the form
      {'limit': float, 'sense': str}. The sense defines whether the epsilon
      constraint is a lower or an upper bound, and the value must be either
      'upper' or 'lower'.
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
    # If no optimization sense is provided, use the default value from self.
    # If an optimization sense IS provided, overwrite the default value with
    # the provided value.
    # _sense is the parameter used only in this method
    if sense is None:
      print('opt_shgo: No optimization sense provided; Maximizing objective function')
      sense = 'max'
    else:
      if sense not in self.valid_sense:
        raise ValueError(f'opt_shgo: sense must be one of {self.valid_sense}')

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

    def make_g_metric(mkg_evaluate, mkg_sense, metric_index, metric_limit):

      j = np.where(self.evaluator.metrics == metric_index)[0][0]

      def g_metric_fn(x):
        if mkg_sense == 'upper':
          met_value = self._f(evaluate=mkg_evaluate,
                              sense='max',
                              verbose=verbose)(x)[j]
        elif mkg_sense == 'lower':
          met_value = self._f(evaluate=mkg_evaluate,
                              sense='min',
                              verbose=verbose)(x)[j]
        else:
          raise ValueError('opt_shgo: Epsilon constraint must be upper or lower')

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
    if eps_metric is not None:

      # loop through all available metrics
      for index, info in eps_metric.items():
        # append the existing constraints container with the value of the
        # current metric constraint
        # as the loop executes, one constraint per metric will be added to the
        # container
        g_metric = make_g_metric(
          mkg_evaluate = evaluate,
          mkg_sense = info['sense'],
          metric_index = index,
          metric_limit = info['limit']
        )

        constraints += [{'type': 'ineq', 'fun': g_metric}]

    opt_dict = {'f_tol': tol,
                'maxiter': maxiter,
                'disp': verbose >= 1}

    # note time when algorithm started
    start = time.time()

    result = shgo(
      self._fi(i, evaluate, sense, verbose), # callable function that returns the scalar objective function value
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
        solve_time=elapsed,
        opt_sense=sense
      )
    else:
      return result, elapsed


  def optimum_metrics(
    self                  ,
    max_amount   = None   ,
    total_amount = None   ,
    sense        = None   ,
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
    sense : Dict or str
      Optimization sense for each metric. Must be 'min' or 'max'. If None, then
      the sense provided to the EpsilonConstraintOptimizer class is used for
      all metrics. If string, the sense is used for all metrics.
    statistic : function
      The statistic used on the sample evaluations.
    tol : float
      The search tolerance.
    maxiter : int
      The maximum iterations for the search.
    verbose : int
      Verbosity level.
    """
    # if no metric_sense is provided, default to maximizing metrics
    if sense is None:
      print('optimum_metrics: No optimization sense provided; Maximizing metrics')
      self._max_metrics = {
        mtr : self.opt_slsqp(
          metric = mtr,
          sense = 'max',
          max_amount=max_amount,
          total_amount=total_amount,
          eps_metric=None,
          statistic=statistic,
          tol=tol,
          maxiter=maxiter,
          verbose=verbose
        )
        for mtr in self.evaluator.metrics
      }
    else:
      # if metric_sense is a dictionary, use the sense value provided per metric
      if type(sense) == dict:
        self._max_metrics = {
          mtr: self.opt_slsqp(
            metric = mtr,
            sense = sense[mtr],
            max_amount = max_amount,
            total_amount = total_amount,
            eps_metric = None,
            statistic = statistic,
            tol = tol,
            maxiter = maxiter,
            verbose = verbose
          )
          for mtr in self.evaluator.metrics
        }
      # if metric_sense is a string, apply that sense to all metrics
      elif type(sense) == str:
        self._max_metrics = {
          mtr: self.opt_slsqp(
            metric = mtr,
            sense = sense,
            max_amount = max_amount,
            total_amount = total_amount,
            eps_metric = None,
            statistic = statistic,
            tol = tol,
            maxiter = maxiter,
            verbose = verbose
          )
          for mtr in self.evaluator.metrics
        }
      else:
        raise TypeError(f'optimum_metrics: sense must be dict or str')

    # Provide info on any failed metric optimizations
    for k,v in self._max_metrics.items():
      if v.exit_code != 0:
        print(f'Metric {k} optimization failed: Code {v.exit_code}, {v.exit_message}')
        v.metrics[k] = -1.0

    return pd.Series(
      [v.metrics[k]
       for k, v in self._max_metrics.items()],
      name  = "Value",
      index = self._max_metrics.keys(),
    )


  def opt_milp(
          self,
          metric,
          sense        = None   ,
          max_amount   = None   ,
          total_amount = None   ,
          eps_metric   = None   ,
          statistic    = np.mean,
          sizelimit    = 1e6    ,
          verbose      = 0      ,
  ):
    """
    Maximize the objective function using a piecewise linear
    representation to create a mixed integer linear program.

    Parameters
    ----------
    metric : str
      Name of metric to maximize
    sense : str
      Optimization sense ('min' or 'max'). If no value is provided to this
      method, the sense value used to create the EpsilonConstraintOptimizer
      object is used instead.
    max_amount : DataFrame
      Maximum investment amounts by R&D category (defined in investments data)
      and maximum metric values
    total_amount : float
      Upper limit on total investments summed across all R&D categories.
    eps_metric : Dict
      RHS of the epsilon constraint(s) on one or more metrics. Keys are metric
      names, and the values are dictionaries of the form
      {'limit': float, 'sense': str}. The sense defines whether the epsilon
      constraint is a lower or an upper bound, and the value must be either
      'upper' or 'lower'.
    statistic : function
      Summary statistic (metric measure) fed to evaluator_corners_wide method
      in Evaluator
    total_amount : float
      Upper limit on total investments summed across all R&D categories
    sizelimit : int
      Maximum allowed number of binary variables. If the problem size exceeds
      this limit, pwlinear_milp will exit before building or solving the model.
    verbose : int
      A value greater than zero will save the optimization model as a .lp file
      A value greater than 1 will print out status messages

    Returns
    -------
    Optimum : NamedTuple
      exit_code
      exit_message
      amounts (None, if no solution found)
      metrics (None, if no solution found)
      solve_time
      opt_sense

    """
    import time
    time0 = time.time()
    # If no optimization sense is provided, use the default value from self.
    # If an optimization sense IS provided, overwrite the default value with
    # the provided value.
    # _sense is the parameter used only in this method
    if sense is None:
      print('opt_milp: No optimization sense provided; Maximizing objective')
      sense = 'max'
    else:
      if sense not in self.valid_sense:
        raise ValueError(f'opt_milp: sense must be one of {self.valid_sense}')

    _start = time.time()

    # investment categories
    _categories = self.evaluator.categories

    # metric to optimize
    _obj_metric = metric

    # if custom upper limits on investment amounts by category have not been
    # defined, get the upper limits from self.evaluator
    if max_amount is None:
      max_amount = self.evaluator.max_amount.Amount

    if verbose > 1: print(f'Getting and processing wide data at %s s' %
                          str(round(time.time() - _start, 1)))

    # get data frame of elicited metric values by investment level combinations
    _wide = self.evaluator.evaluate_corners_wide(statistic).reset_index()

    _nbinary = len(_wide) * (len(_wide)-1) / 2

    if _nbinary >= sizelimit:
      print(f'MILP contains {_nbinary} binary variables and will exit without solving')
      return None

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

    if verbose > 1: print('Data processed at %s s' %
                          str(round(time.time() - _start, 1)))

    if verbose > 1: print('Building MIP model at %s s' %
                          str(round(time.time() - _start, 1)))

    # instantiate MILP model
    if sense == 'max':
      _model = Model(sense=MAXIMIZE)
    else:
      _model = Model(sense=MINIMIZE)

    bin_vars = []
    lmbd_vars = []
    #%%
    time0 = time.time()
    if verbose > 1: print('Creating %i lambda variables at %s s' %
                          (I, str(round(time.time() - _start, 1))))

    # create continuous lambda variables
    for i in range(I):
      #lmbd_vars += [_model.add_var(name='lmbd_' + str(i), lb=0.0, ub=1.0)]
      lmbd_vars.append(_model.add_var(name='lmbd_' + str(i), lb=0.0, ub=1.0))

    if verbose > 1: print('Creating %i binary variables and constraints at %s s' %
                          (_nbinary, str(round(time.time() - _start, 1))))

    # create binary variables and binary/lambda variable constraints
    bin_count = 0
    for i in range(I):
      for j in range(i, I):
        if j != i:
          # add binary variable
          bin_vars.append(_model.add_var(name='y_' + str(i) + '_' + str(j),
                                      var_type=BINARY))
          # add binary/lambda variable constraint
          _model += bin_vars[bin_count] <= lmbd_vars[i] + lmbd_vars[j],\
                    'Interval_Constraint_' + str(i) + '_' + str(j)
          bin_count += 1
    
    if verbose > 1: print('Creating total budget constraint at %s s' %
                          str(round(time.time() - _start, 1)))

    # total budget constraint - only if total_amount is an input
    if total_amount is not None:
      _model += xsum(lmbd_vars[i] * inv_levels[i][j]
                      for i in range(I)
                      for j in range(len(inv_levels[i]))) <= total_amount,\
                 'Total_Budget'

    if verbose > 1: print('Creating category budget constraints at %s s' %
                          str(round(time.time() - _start, 1)))

    # constraint on budget for each investment category
    # this is either fed in as an argument or pulled from evaluator
    for j in range(len(_categories)):
      _model += xsum(lmbd_vars[i] * [el[j] for el in inv_levels][i]
                      for i in range(I)) <= max_amount[j],\
                 'Budget_for_' + _categories[j].replace(' ', '')

    if verbose > 1: print('Defining metric constraints at %s s' %
                          str(round(time.time() - _start, 1)))

    # define metric constraints if lower limits on metrics have been defined
    if eps_metric is not None:

      # loop through list of metric minima
      for index, info in eps_metric.items():
        if info['sense'] == 'upper':
          _eps_mult = -1.0
        elif info['sense'] == 'lower':
          _eps_mult = 1.0
        else:
          raise ValueError('opt_milp: Epsilon constraint must be upper or lower')

        # add metric constraint on the lambda variables
        _model += _eps_mult * xsum(lmbd_vars[i] * _wide.loc[:,index].values.tolist()[i]
                       for i in range(I)) >= info['limit'],\
                  'Eps_Const_' + index

    if verbose > 1: print('Defining lambda convexity constraints at %s s' %
                          str(round(time.time() - _start, 1)))

    time0 = time.time()
    lmbd_vars = np.asarray(lmbd_vars)
    # convexity constraint for continuous variables
    _model += np.sum(lmbd_vars) == 1, 'Lambda_Sum'

    if verbose > 1: print('Defining binary convexity constraints at %s s' %
                          str(round(time.time() - _start, 1)))

    # constrain binary variables such that only one interval can be active
    # at a time
    
    bin_var = np.asarray(bin_vars)
    _model += bin_var.sum() == 1, 'Binary_Sum'

    if verbose > 1: print('Defining objective function at %s s' %
                          str(round(time.time() - _start, 1)))

    # objective function
    _model.objective = xsum(m[i] * lmbd_vars[i] for i in range(I))

    # save a copy of the model in LP format
    if verbose > 0:
      print('Saving model at %s s' %
            str(round(time.time() - _start, 1)))
      _model.write('model.lp')
    else:
      # if the verbose parameter is 0, the MIP solver does not print output
      _model.verbose = 0

    if verbose > 1: print('Optimizing at %s s' %
                          str(round(time.time() - _start, 1)))
    
    _opt_start = time.time()
    
    # find optimal solution
    _solution = _model.optimize()

    elapsed = time.time() - _opt_start

    # if a feasible solution was found, calculate the optimal investment values
    # and return a populated Optimum tuple
    if _model.status.value == 0:
      # get the optimal variable values as two lists
      if verbose > 1: print('Optimized at %s s' %
                            str(round(time.time() - _start, 1)))
      lmbd_opt = []
      y_opt = []
      for v in _model.vars:
        if 'lmbd' in v.name:
          lmbd_opt += [v.x]
        elif 'y' in v.name:
          y_opt += [v.x]
      
      inv_levels_opt = []

      if verbose > 1: print('Calculating optimal investment values at %s s' %
                            str(round(time.time() - _start, 1)))

      # calculate the optimal investment values
      for i in range(len(_categories)):
        inv_levels_opt += [sum([lmbd_opt[j] * [el[i] for el in inv_levels][j]
                                for j in range(len(lmbd_opt))])]

      # construct a Series of optimal investment levels
      x = pd.Series(inv_levels_opt, name="Amount",
                    index=self.evaluator.max_amount.index)

      y = pd.Series(None, name="Value",
                    index=_all_metrics)

      if verbose > 1: print('Calculating optimal metric values at %s s' %
                            str(round(time.time() - _start, 1)))

      # calculate optimal values of all metrics
      for j in range(len(_all_metrics)):
        y[j] = sum(
          [lmbd_opt[i] * _metric_data[i][j]
           for i in range(len(_metric_data))]
        )

      if verbose > 1: print('Optimal metric values calculated at %s s' %
                            str(round(time.time() - _start, 1)))

      return Optimum(
        exit_code=_model.status.value,
        exit_message=_model.status,
        amounts=x,
        metrics=y,
        solve_time=elapsed,
        opt_sense = sense
      )
    # if no feasible solution was found, return a partially empty Optimum tuple
    else:
      return Optimum(
        exit_code=_model.status.value,
        exit_message=_model.status,
        amounts=None,
        metrics=None,
        solve_time=elapsed,
        opt_sense=sense
      )