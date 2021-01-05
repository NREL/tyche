Optimization
============

Summary
-------

Technology models and data are defined before the optimizer is called.
Three methods in the ``EpsilonConstraintOptimizer`` class,
``maximize_slsqp``, ``maximize_shgo`` and ``maximize_diffev``, are
wrappers for the algorithm calls. The optimization methods define the
optimization problem according to each algorithm’s requirements, call
the algorithm, and provide either optimized results in a standard format
for postprocessing, or an error messages if the optimization did not
complete successfully. The SLSQP algorithm, which is not a global
optimizer, is provided to assess problem feasibility and provide
reasonable upper and lower bounds on metrics being optimized. Global
optimization algorithms to implement were chosen according to the
following criteria.

-  Ability to perform constrained optimization with inequality
   constraints
-  Ability to optimize without specified Jacobian or Hessian functions
-  Ability to specify bounds on individual decision variables
-  Ability to work on a variety of potentially non-convex and otherwise
   complex problems

Solutions to ``residential_pv_multiobjective``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The solve times listed are in addition to the time required to set up
the problem and solve for the maximum allowable metric values, which
currently uses the SLSQP algorithm. This setup time is between 10 and 15
seconds.

Minimizing LCOE subject to a total investment amount of $3 MM USD and
GHG being at least 40.

====================== ======================== ==================== ==============
Algorithm              Objective Function Value GHG Constraint Value Solve Time (s)
====================== ======================== ==================== ==============
Differential evolution 0.037567                 41.699885            145
Differential evolution 0.037547                 41.632867            589
SLSQP                  0.037712                 41.969348            ~ 2
SHGO                   None found               None found           -
====================== ======================== ==================== ==============

Additional details for each solution are given below under the section
for the corresponding algorithm.

Sequential Least Squares Programming
------------------------------------

The Sequential Least Squares Programming algorithm uses a gradient
search method to locate a possibly local optimum. [6]

``EpsilonConstraintOptimizer.maximize_slsqp(self, metric, max_amount=None, total_amount=None, min_metric=None, statistic=np.mean, initial=None, tol=1e-8, maxiter=50, verbose=0)``

Maximize the objective function using the ``fmin_slsqp`` algorithm.

**Parameters**

``metric`` : str
   Name of metric to maximize. No default.
``max_amount`` : DataFrame
   Maximum investment amounts by R&D category (defined in investments
   data) and maximum metric values. Defaults to ``None``.
``total_amount`` : float
   Upper limit on total investments summed across all R&D categories.
   Defaults to ``None``.
``min_metric`` : DataFrame
   Lower limits on all metrics. Defaults to ``None``.
``statistic`` : function
   Summary statistic used on the sample evaluations; the metric measure
   that is fed to the optimizer. Defaults to ``np.mean`` such that the
   optimization is performed on the means of relevant metrics.
``initial`` : array of float
   Initial value of decision variable(s) fed to the optimizer. Defaults
   to ``None``.
``tol`` : float
   Requested accuracy of the optimized solution. Defaults to 1E-08.
``maxiter`` : int
   Maximum number of iterations the optimizer is permitted to execute.
   Defaults to 50.
``verbose`` : int
   Amount of information provided by the wrapper as the optimization is
   performed. Defaults to 0.

**Return**

``results`` : ``Optimum`` instance
   Container for an ``exit_code`` and ``exit_message`` received from the
   ``differential_evolution`` call, a list of optimized ``amounts`` and
   a list of optimized ``metrics``.

A complete list of parameters and options for the ``fmin_slsqp``
algorithm is available in the documentation. [3]

Defining Constraints
~~~~~~~~~~~~~~~~~~~~

Constraints for ``fmin_slsqp`` are defined either as a single function
that takes as input a vector of decision variable values and returns an
array containing the value of all constraints in the problem
simultaneously. Both equality and inequality constraints can be defined,
although they must be as separate functions and are provided to the
``fmin_slsqp`` algorithm under separate arguments.

SLSQP Solution to ``residential_pv_multiobjective``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Solve time: 1.5 s

================= ===============
Decision Variable Optimized Value
================= ===============
BoS R&D           1.25 E-04
Inverter R&D      3.64 E-08
Module R&D        3.00 E+06
================= ===============

============= ===============
System Metric Optimized Value
============= ===============
GHG           41.97
LCOE          0.038
Labor         0.032
============= ===============

Differential Evolution
----------------------

Differential evolution is one type of evolutionary algorithm that
iteratively improves on an initial population, or set of potential
solutions. [5] Differential evolution is well-suited to searching large
solution spaces with multiple local minima, but does not guarantee
convergence to the global minimum.

``EpsilonConstraintOptimizer.maximize_diffev(self, metric, max_amount=None, total_amount=None, min_metric=None, statistic=np.mean, strategy='best1bin', tol=1e-8, maxiter=50, init='latinhypercube', verbose=0)``

**Parameters**

``metric`` : str
   Name of metric to maximize. No default value.
``max_amount`` : DataFrame
   Maximum investment amounts by R&D category (defined in investments
   data) and maximum metric values. Defaults to ``None``.
``total_amount`` : float
   Upper limit on total investments summed across all R&D categories.
   Defaults to ``None``.
``min_metric`` : DataFrame
   Lower limits on all metrics. Defaults to ``None``.
``statistic`` : function
   Summary statistic used on the sample evaluations; the metric measure
   that is fed to the optimizer. Defaults to ``np.mean`` such that the
   optimization is performed on the means of relevant metrics.
``strategy`` : str
   Which differential evolution strategy to use. Defaults to ‘best1bin’.
   See [2] for full list.
``seed`` : int
   Sets the random seed for optimization by creating a new
   ``RandomState`` instance. Defaults to 2 for reproducible solutions.
   If a value is not provided, then ``differential_evolution`` will
   return slightly different solutions for the same optimization problem
   every time it is called.
``init`` : str or array-like
   Type of population initialization. Defaults to ‘latinhypercube’.
   Alternative initializations are ‘random’ (which does not guarantee
   good coverage of the solution space) or specifying every member of
   the initial population in an array of shape (``popsize``,
   ``len(variables)``). The latter option is useful when the global
   minimum is known to be in a small portion of the solution space, and
   the initialization can seed the population in this area. However,
   this parameter is not analogous to specifying initial values for
   decision variables, as each candidate solution in the population must
   be unique for the algorithm to optimize correctly.
``tol`` : float
   Relative tolerance for convergence, which provides an upper limit on
   the standard deviation of candidate solutions. When this upper limit
   is met, the optimization has converged. Defaults to 0.01. The
   convergence tolerance for this algorithm was loosened compared to the
   other algorithms to lessen the execution time and increase the
   changes of the algorithm converging. Tighter tolerances (lower values
   of ``tol``) tended to prevent the algorithm converging.
``maxiter`` : int
   Upper limit on generations of candidate solution evolution, which
   corresponds to the number of algorithm iterations. Each iteration
   involves many function evaluations as each solution in the population
   evolves. Defaults to 75.
``verbose`` : int
    Verbosity level returned by this outer function and the differential_evolution algorithm. Defaults to 0.
    * verbose = 0 : No messages.
    * verbose = 1 : Objective function value at every algorithm iteration.
    * verbose = 2 : Investment constraint status, metric constraint status, and objective function value.
    * verbose = 3 : Decision variable values, investment constraint status, metric constraint status, and objective function value.
    * verbose > 3 : All metric values, decision variable values, investment constraint status, metric constraint status, and objective function value.

**Returns**

``out`` : ``Optimum`` instance
   Container for an ``exit_code`` and ``exit_message`` received from the
   ``differential_evolution`` call, a list of optimized ``amounts`` and
   a list of optimized ``metrics``.

A complete list of parameters and options for the
``differential_evolution`` algorithm is available in the documentation.
[2]

.. _defining-constraints-1:

Defining Constraints
~~~~~~~~~~~~~~~~~~~~

Constraints for ``differential_evolution`` are defined by passing the
same multi-valued function defined in ``maximize_slsqp`` to the
``NonLinearConstraint`` method. [7]

Differential Evolution Solutions to ``residential_pv_multiobjective``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Solution 1**

-  Seed = 2
-  Solve time = 145 s

================= ===============
Decision Variable Optimized Value
================= ===============
BoS R&D           9.62 E+02
Inverter R&D      5.33 E+02
Module R&D        2.99 E+06
================= ===============

============= ===============
System Metric Optimized Value
============= ===============
GHG           41.70
LCOE          0.038
Labor         -0.456
============= ===============

**Solution 2**

-  Seed = 1
-  Solve time = 589

================= ===============
Decision Variable Optimized Value
================= ===============
BoS R&D           4.70 E+03
Inverter R&D      3.71 E+02
Module R&D        2.99 E+06
================= ===============

============= ===============
System Metric Optimized Value
============= ===============
GHG           41.63
LCOE          0.037
Labor         -2.29
============= ===============

Simplicial Homology Global Optimization
---------------------------------------

The Simplicial Homology Global Optimization (SHGO) algorithm applies
simplicial homology to general non-linear, low-dimensional optimization
problems. [4]

``EpsilonConstraintOptimizer.maximize_shgo(self, metric, max_amount=None, total_amount=None, min_metric=None, statistic=np.mean, tol=1e-8, maxiter=50, sampling_method='simplicial', verbose=0)``

Maximize the objective function using the shgo global optimization
algorithm.

**Parameters**

``metric`` : str
   Name of metric to maximize. No default value.
``max_amount`` : DataFrame
   Maximum investment amounts by R&D category (defined in investments
   data) and maximum metric values. Defaults to ``None``.
``total_amount`` : float
   Upper metric_limit on total investments summed across all R&D
   categories. Defaults to ``None``.
``min_metric`` : DataFrame
   Lower limits on all metrics. Defaults to ``None``.
``statistic`` : function
   Summary statistic used on the sample evaluations; the metric measure
   that is fed to the optimizer. Defaults to ``np.mean`` such that the
   optimization is performed on the means of relevant metrics.
``tol`` : float
   Objective function tolerance in stopping criterion. Defaults to
   1E-08.
``maxiter`` : int
   Upper limit on algorithm iterations that can be performed. One
   iteration involves many function evaluations. Defaults to 50.
``sampling_method`` : str
   Allowable values are ‘sobol and ’simplicial’. Simplicial is default,
   uses less memory, and guarantees convergence (theoretically). Sobol
   is faster, uses more memory and does not guarantee convergence. Per
   documentation, Sobol is better for “easier” problems. Defaults to
   ‘simplicial’.
``verbose`` : int
    Verbosity level returned by this outer function and the SHGO algorithm. Defaults to 0.
    *  verbose = 0 : No messages.
    *  verbose = 1 : Convergence messages from SHGO algorithm.
    *  verbose = 2 : Investment constraint status, metric constraint status, and convergence messages.
    *  verbose = 3 : Decision variable values, investment constraint status, metric constraint status, and convergence messages.
    *  verbose > 3 : All metric values, decision variable values, investment constraint status, metric constraint status, and convergence messages .

**Returns**

``out`` : ``Optimum`` instance
   : Container for an ``exit_code`` and ``exit_message`` received from
   the ``shgo`` call, a list of optimized ``amounts`` and a list of
   optimized ``metrics``.

``shgo`` does not have a parameter that sets the initial decision
variable values. A complete list of parameters available for the
``shgo`` algorithm is available in the documentation. [1]

.. _defining-constraints-2:

Defining Constraints
~~~~~~~~~~~~~~~~~~~~

Constraints for ``shgo`` must be provided as a dictionary or sequence of
dictionaries with the following format:

::

       constraints = [ {'type': 'ineq', 'fun': g1(x)},
                       {'type': 'ineq', 'fun': g2(x)},
                       ...
                       {'type': 'eq', 'fun': h1(x)},
                       {'type': 'eq', 'fun': h2(x)},
                       ... ]

Each of the constraint functions ``g1(x)``, ``h1(x)``, and so on are
functions that take decision variable values as inputs and return the
value of the constraint. Inequality constraints (``g1(x)`` and ``g2(x)``
above) are formulated as :math:`g(x) \geq 0` and equality constraints
(``h1(x)`` and ``h2(x)`` above) are formulated as :math:`h(x) = 0`. Each
constraint in the optimization problem is defined as a separate
function, with a separate dictionary giving the constraint type. With
``shgo`` it is not possible to use one function that returns a vector of
constraint values.

References
----------

1. ``scipy.optimize.shgo`` SciPy v1.5.4 Reference Guide: Optimization
   and root finding (``scipy.optimize``) URL:
   https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.shgo.html#rb2e152d227b3-1
   Last accessed 12/28/2020.

2. ``scipy.optimize.differential_evolution`` SciPy v1.5.4 Reference
   Guide: Optimization and root finding (``scipy.optimize``) URL:
   https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html
   Last accessed 12/28/2020.

3. ``scipy.optimize.fmin_slsqp`` SciPy v1.5.4 Reference Guide:
   Optimization and root finding (``scipy.optimize``) URL:
   https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fmin_slsqp.html
   Last accessed 12/28/2020.

4. Endres, SC, Sandrock, C, Focke, WW. (2018) “A simplicial homology
   algorithm for Lipschitz optimisation”, Journal of Global Optimization
   (72): 181-217. URL:
   https://link.springer.com/article/10.1007/s10898-018-0645-y

5. Storn, R and Price, K. (1997) “Differential Evolution - a Simple and
   Efficient Heuristic for Global Optimization over Continuous Spaces”,
   Journal of Global Optimization (11): 341 - 359. URL:
   https://link.springer.com/article/10.1023/A:1008202821328

6. Kraft D (1988) A software package for sequential quadratic
   programming. Tech. Rep. DFVLR-FB 88-28, DLR German Aerospace Center —
   Institute for Flight Mechanics, Koln, Germany.

7. ``scipy.optimize.NonlinearConstraint`` SciPy v1.5.4 Reference Guide:
   Optimization and root finding (``scipy.optimize``) URL:
   https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.NonlinearConstraint.html
   Last accessed 12/29/2020.
