.. _sec-optimizers:

Optimization
============

Nonlinear Programming Formulation
---------------------------------

Three methods in the ``EpsilonConstraintOptimizer`` class, ``opt_slsqp``, ``opt_shgo`` and ``opt_diffev``, are
wrappers for optimization algorithm calls. (The :ref:`sec-epsconstraint` section provides full parameter and return value information for these methods.) The optimization methods define the optimization problem according to each algorithm’s requirements, call the algorithm, and provide either optimized results in a standard format for postprocessing, or an error messages if the optimization did not complete successfully. The SLSQP algorithm, which is not a global optimizer, is provided to assess problem feasibility and provide reasonable upper and lower bounds on metrics being optimized. Because the technology models within an R&D decision context may be arbitrarily complex, two global optimization algorithms were also implemented. The global algorithms were chosen according to the following criteria.

-  Ability to perform constrained optimization with inequality constraints, for instance on metric values or investment amounts.
-  Ability to optimize without specified Jacobian or Hessian functions (derivative-less optimization).
-  Ability to specify bounds on individual decision variables, which allows constraints on single research areas.
-  Ability to work on a variety of potentially non-convex and otherwise complex problems.

Algorithm Testing
~~~~~~~~~~~~~~~~~

As a point of comparison between algorithms, the :ref:`sec-simplerespv` decision context was optimized for minimum levelized cost of electricity (LCOE) subject to an investment constraint and a metric constraint (GHG). The solutions are given in :numref:`tbl-algoperformance`. The solve times listed are in addition to the time required to set up the problem and solve for the optimum metric values; this procedure currently uses the SLSQP algorithm by default. This setup time is between 10 and 15 seconds.

.. _tbl-algoperformance:
.. table:: Minimizing LCOE subject to a total investment amount of $3 MM USD and GHG being at least 40.

 ====================== ======================== ==================== ==============
 Algorithm              Objective Function Value GHG Constraint Value Solve Time (s)
 ====================== ======================== ==================== ==============
 Differential evolution 0.037567                 41.699885            145
 Differential evolution 0.037547                 41.632867            589
 SLSQP                  0.037712                 41.969348            ~ 2
 SHGO                   None found               None found           None found
 ====================== ======================== ==================== ==============

Additional details for each solution are given below under the section for the corresponding algorithm.

Sequential Least Squares Programming (SLSQP)
--------------------------------------------

The Sequential Least Squares Programming algorithm uses a gradient search method to locate a possibly local optimum. [6] A complete list of parameters and options for the ``fmin_slsqp`` algorithm is available in the  `scipy.optimize.fmin_slsqp <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fmin_slsqp.html>`_ documentation.

Constraints for ``fmin_slsqp`` are defined either as a single function that takes as input a vector of decision variable values and returns an array containing the value of all constraints in the problem simultaneously. Both equality and inequality constraints can be defined, although they must be as separate functions and are provided to the ``fmin_slsqp`` algorithm under separate arguments.

SLSQP Solution to Simple Residential Photovoltaics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Solve time: 1.5 s

.. _tbl-slsqpvars:
.. table:: Optimal decision variables found by the SLSQP algorithm.

 ================= ===============
 Decision Variable Optimized Value
 ================= ===============
 BoS R&D           1.25 E-04
 Inverter R&D      3.64 E-08
 Module R&D        3.00 E+06
 ================= ===============

.. _tbl-slsqpmetrics:
.. table:: Optimal system metrics found by the SLSQP algorithm.

 ============= ===============
 System Metric Optimized Value
 ============= ===============
 GHG           41.97
 LCOE          0.038
 Labor         0.032
 ============= ===============

Differential Evolution
----------------------

Differential evolution is one type of evolutionary algorithm that iteratively improves on an initial population, or set of potential solutions. [5] Differential evolution is well-suited to searching large solution spaces with multiple local minima, but does not guarantee convergence to the global minimum. A complete list of parameters and options for the `differential_evolution` algorithm is available in the `scipy.optimize.differential_evolution  <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html>`_ documentation.

Constraints for `differential_evolution` are defined by passing the same multi-valued function defined in `opt_slsqp` to the `NonlinearConstraint <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.NonlinearConstraint.html>`_ method.

Differential Evolution Solutions to Simple Residential Photovoltaics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Differential evolution stochastically populates the initial set of potential solutions, and so the optimal solution and solve time may vary with the random seed used. 

Solution 1
^^^^^^^^^^

Starting with a random seed of 2, the solution time was 145 seconds.

.. _tbl-diffevvars1:
.. table:: Optimal decision variables found by the differential evolution algorithm with a seed of 2.

 ================= ===============
 Decision Variable Optimized Value
 ================= ===============
 BoS R&D           9.62 E+02
 Inverter R&D      5.33 E+02
 Module R&D        2.99 E+06
 ================= ===============

.. _tbl-diffevmetrics1:
.. table:: Optimal system metrics found by the differential evolution algorithm with a seed of 2.

 ============= ===============
 System Metric Optimized Value
 ============= ===============
 GHG           41.70
 LCOE          0.038
 Labor         -0.456
 ============= ===============

Solution 2
^^^^^^^^^^

Starting with a random seed of 1, the solution time was 589 seconds.

.. _tbl-diffevvars2:
.. table:: Optimal decision variables found by `differential_evolution` as called by `EpsilonConstraints.opt_diffev` with a seed of 1.

 ================= ===============
 Decision Variable Optimized Value
 ================= ===============
 BoS R&D           4.70 E+03
 Inverter R&D      3.71 E+02
 Module R&D        2.99 E+06
 ================= ===============

.. _tbl-diffevmetrics2:
.. table:: Optimal system metrics found by `differential_evolution` as called by `EpsilonConstraints.opt_diffev` with a seed of 1.

 ============= ===============
 System Metric Optimized Value
 ============= ===============
 GHG           41.63
 LCOE          0.037
 Labor         -2.29
 ============= ===============

Simplicial Homology Global Optimization
---------------------------------------

The Simplicial Homology Global Optimization (SHGO) algorithm applies simplicial homology to general non-linear, low-dimensional optimization problems. [4] Constraints for `shgo` must be provided as a dictionary or sequence of
dictionaries with the following format:

::

       constraints = [ {'type': 'ineq', 'fun': g1(x)},
                       {'type': 'ineq', 'fun': g2(x)},
                       ...
                       {'type': 'eq', 'fun': h1(x)},
                       {'type': 'eq', 'fun': h2(x)},
                       ... ]

Each of the constraint functions `g1(x)`, `h1(x)`, and so on are functions that take decision variable values as inputs and return the value of the constraint. Inequality constraints (`g1(x)` and `g2(x)` above) are formulated as :math:`g(x) \geq 0` and equality constraints (`h1(x)` and `h2(x)` above) are formulated as :math:`h(x) = 0`. Each constraint in the optimization problem is defined as a separate function, with a separate dictionary giving the constraint type. With `shgo` it is not possible to use one function that returns a vector of constraint values.

Piecewise Linear (MILP) Formulation
-----------------------------------

Notation
~~~~~~~~

.. _tbl-milpindex:
.. table:: Index definitions for the MILP formulation.

   ========== ================================================================
   Index      Description
   ========== ================================================================
   :math:`I`  Number of elicited data points (investment levels and metrics)
   :math:`J`  Number of investment categories
   :math:`K`  Number of metrics
   ========== ================================================================


.. _tbl-milpdat:
.. table:: Data definitions for the MILP formulation.

   ===================== =========================================================== ================================================================================================
   Data                  Notation                                                    Information 
   ===================== =========================================================== ================================================================================================
   Investment amounts    :math:`c_{ij}, i \in \{1, ..., I\}`                         :math:`c_i` is a point in :math:`J`-dimensional space
   Metric value          :math:`q_{ik}, i \in \{1, ..., I \}, k \in \{1, ..., K \}`  One metric will form the objective function, leaving up to :math:`K-1` metrics for constraints
   ===================== =========================================================== ================================================================================================


.. _tbl-milpvar:
.. table:: Variable definitions for the MILP formulation.

   ===================== ================================================= ====================================================================================================
   Variable              Notation                                          Information 
   ===================== ================================================= ====================================================================================================
   Binary variables      :math:`y_{ii'}, i, i' \in \{1, ..., I\}, i' > i`  Number of linear intervals between elicited data points.
   Combination variables :math:`\lambda_{i}, i \in \{1, ..., I\}`          Used to construct linear combinations of elicited data points. :math:`\lambda_{i} \geq 0 \forall i`
   ===================== ================================================= ====================================================================================================


Each metric and investment amount can be written as a linear combination of elicited data points and the newly introduced variables :math:`\lambda_{i}` and :math:`y_{ii'}`. Additional constraints on :math:`y_{ii'}` and :math:`\lambda_{i}` take care of the piecewise linearity by ensuring that the corners used to calculate :math:`q_k` reflect the interval that :math:`c_i` is in. There will be a total of :math:`\binom{I}{2}` binary :math:`y` variables, which reduces to :math:`\frac{I(I-1)}{2}` binary variables.


One-Investment-Category, One-Metric Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Suppose we have an elicited data set for one metric (:math:`K = 1`) and one investment category (:math:`J = 1`) with three possible investment levels (:math:`I = 3`). We can write the total investment amount as a linear combination of the three investment levels :math:`c_{i1}, i \in \{1, 2, 3\}`, using the :math:`\lambda` variables:

:math:`\lambda_{1}c_{11} + \lambda_{2}c_{21} + \lambda_{13}c_{31} = \sum_{i} \lambda_{i}c_{i1}`

We can likewise write the metric as a linear combination of :math:`q_{1i}` and the :math:`\lambda` variables:

:math:`\lambda_{1}q_{11} + \lambda_{2}q_{21} + \lambda_{3}q_{31} = \sum_{i} \lambda_{i}q_{i1}`

We have the additional constraint on the :math:`\lambda` variables that 

:math:`\sum_{i} \lambda_{i} = 1`

These equations, combined with the integer variables :math:`y_{ii'} = \{ y_{12}, y_{13}, y_{23} \}`, can be used to construct a mixed-integer linear optimization problem.

The MILP that uses this formulation to minimize a technology metric subject to a investment budget :math:`B` is as follows:

:math:`\min_{y, \lambda} \lambda_{1}q_{11} + \lambda_{2}q_{21} + \lambda_{3}q_{31}`

subject to

:math:`\lambda_{1}c_{11} + \lambda_{2}c_{21} + \lambda_{3}c_{31} \leq B` , (1) Total budget constraint

:math:`\lambda_1 + \lambda_2 + \lambda_3 = 1` , (2)

:math:`y_{12} + y_{23} + y_{13} = 1` , (3)

:math:`y_{12} \leq \lambda_1 + \lambda_2` , (4)

:math:`y_{23} \leq \lambda_2 + \lambda_3` , (5)

:math:`y_{13} \leq \lambda_1 + \lambda_3` , (6)

:math:`0 \leq \lambda_1, \lambda_2, \lambda_3 \leq 1` , (7)

:math:`y_{12}, y_{23}, y_{13} \in \{ 0, 1 \}` , (8)

(We've effectively removed the investments and the metrics as variables, replacing them with the elicited data points and the new :math:`\lambda` and :math:`y` variables.)

Extension to N x N Problem
~~~~~~~~~~~~~~~~~~~~~~~~~~

Note: :math:`k'` indicates the metric which is being constrained. :math:`k*` indicates the metric being optimized. :math:`J'` indicates the set of investment categories which have a budget limit (there may be more than one budget-constrained category in a problem).

**No metric constraint or investment category-specific budget constraint**

:math:`\min_{y, \lambda} \sum_i \lambda_{i}q_{ik*}`

subject to

:math:`\sum_i \sum_j \lambda_{i}c_{ij} \leq B` , (1) Total budget constraint

:math:`\sum_i \lambda_i = 1` , (2)

:math:`\sum_{i,i'} y_{ii'} = 1` , (3)

:math:`y_{ii'} \leq \lambda_i + \lambda_{i'} \forall i, i'` , (4)

:math:`0 \leq \lambda_i \leq 1 \forall i` , (5)

:math:`y_{ii'} \in \{ 0, 1 \} \forall i, i'` , (6)


**With investment category-specific budget constraint**

:math:`\min_{y, \lambda} \sum_i \lambda_{i}q_{ik*}`

subject to

:math:`\sum_i \sum_j \lambda_{i}c_{ij} \leq B` , (1) Total budget constraint

:math:`\sum_i \lambda_{i}c_{ij'} \leq B_{j'} \forall j' \in J'`,   (2) Investment category budget constraint(s)

:math:`\sum_i \lambda_i = 1` , (3)

:math:`\sum_{i,i'} y_{ii'} = 1` , (4)

:math:`y_{ii'} \leq \lambda_i + \lambda_{i'} \forall i, i'` , (5)

:math:`0 \leq \lambda_i \leq 1 \forall i` , (6)

:math:`y_{ii'} \in \{ 0, 1 \} \forall i, i'` , (7)


**With metric constraint and investment category-specific budget constraint**

:math:`\min_{y, \lambda} \sum_i \lambda_{i}q_{ik*}`

subject to

:math:`\sum_i \sum_j \lambda_{i}c_{ij} \leq B`, (1) Total budget constraint

:math:`\sum_i \lambda_{i}c_{ij'} \leq B_{j'} \forall j' \in J'`   (2) Investment category budget constraint(s)

:math:`\sum_i \lambda_{i}q_{ik'} \leq M_{k'}` , (3) Metric constraint

:math:`\sum_i \lambda_i = 1` , (4)

:math:`\sum_{i,i'} y_{ii'} = 1` , (5)

:math:`y_{ii'} \leq \lambda_i + \lambda_{i'} \forall i, i'` , (6)

:math:`0 \leq \lambda_i \leq 1 \forall i` , (7)

:math:`y_{ii'} \in \{ 0, 1 \} \forall i, i'` , (8)


**Problem Size**

In general, :math:`I` is the number of rows in the dataset of elicited data. In the case that all investment categories have elicited data at the same number of levels (not necessarily the same levels themselves), :math:`I` can also be calculated as :math:`l^J` where :math:`l` is the number of investment levels.

The problem will involve :math:`\frac{I(I-1)}{2}` binary variables and :math:`I` continuous (:math:`\lambda`) variables.


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
