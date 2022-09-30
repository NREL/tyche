.. _sec-approach:

Approach
========

Our production-function approach to R&D portfolio evaluation is
mathematically formulated as a stochastic multi-objective
decision-optimization problem and is implemented in the Python
programming language. The framework abstracts the technology-independent
aspects of the problem into a generic computational schema and enables
the modeler to specify the technology-dependent aspects in a set of data
tables and Python functions. This approach not only minimizes the labor
needed to add new technologies, but it also enforces uniformity of
financial, mass-balance, and other assumptions in the analysis.

The framework is scalable, supporting rapid computation on laptop
computers and large-ensemble studies on high-performance computers (HPC).
The use of vectorized operations for the stochastic calculations and of
response-surface fits for the portfolio evaluations minimizes the
computational resources needed for complex multi-objective
optimizations. The software handles parameterized studies such as
tornado plots, Monte-Carlo sensitivity analyses, and a generalization of
epsilon-constraint optimization.

All values in the data tables may be probability distributions,
specified by Python expressions using a large library of standard
distributions, or the values may be simple numbers. Expert opinion is
encoded through these distributions. The opinions may be combined prior
to simulation or subsequent to it.

Four example technologies have been implemented as examples illustrating the
framework’s use: biorefineries, electrolysis, residential photovoltaics
(PV), and utility-scale PV. A desktop user interface allows exploration
of the cost-benefit trade-offs in portfolio decision problems.

Below we detail the mathematical formulation and its implementation as a
Python module with user-specified data tables and technology functions.

We also provide a sample analysis that exercises the framework’s main
features.
