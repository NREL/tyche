% Guiding Lessons from Workshop and Toy Models
% DRAFT
% 2019-10-21


# Preface

This document is not meant to re-summarize the project's other summaries of lessons from the toy models and the workshop. See the [fact sheets](https://github.com/NREL/portfolio/tree/master/workshop/fact%20sheets), [slide presentations](https://github.com/NREL/portfolio/tree/master/workshop/presentations), and [workshop report](https://github.com/NREL/portfolio/tree/master/workshop/report) for these. Rather, it states high-level conclusions that are actionable for continued development of the analytic framework.


# Conclusions

1.  There is enough commonality between ***stochastic optimization*** methods (cf. the *Monte Carlo*, *Real Options*, and *TRL-TPL* models) and ***stochastic programming*** methods (cf. the *Biorefinery Model* and Gabriel's work) that the analytic framework should be abstract and general enough to encompass both ensemble simulations, linear/non-linear programming, and dynamic programming, although it may be too much effort to formulate individual models so that they can be run in all three modes.

2.  Models (*Polysilicon*, *Biorefinery*, and *Real Options*) are mildly ***non-linear***, so it likely is preferable to use non-linear solvers instead of forcing a linearization or an analytic solution.

3.  Decision-theoretic approaches rely on similar themes of finding ***non-dominated solutions*** or ***robust decisions***, regardless of whether a probabilistic or (scenario-generative) non-probabilistic framework is used, though the probabilistic methods result in information such as confidence intervals.

4.   ***Multi-objective*** optimization is a necessity.

5.  ***Model complexity*** should be kept to a manageable (one or two dozen) set of system components, subcomponents, or decidable parameters. The *Polysilicon Model* probably represents the upper limit of complexity. Klemun's work on overall system costs provides an important example of combining ***hard and soft costs*** for several systems and for the balance of the system. Highly leveragable investments needs to be represented via physics-based modeling.

6.  ***Real options*** can be subsumed under the more general ***multi-stage stochastic optimization***, but two-stage optimization is advisable for R&D investment decisions, because of the uncertainty involved. Studying the performance of a two-stage decisions-support process might involve nesting within a higher level optimization. Discrete methods such as *Petri Nets* are not needed for two-stage decision models.

7.  ***Expert opinion*** might be best represented as assessments of future trends in ***experience curves*** that are based on historical experience, perhaps as confidence intervals or odds ratios instead of detailed specificaitions of probability distributions.

8.  Portfolio-level decisions will inevitably involve a ***hierarchy*** of programs, systems, subsystems, and components within and between portfolios.

9.  ***Bayesian updating*** of expert opinions requires too much training history---especially where rare events might be an issue---and is not sufficiently informative to warrant the complexity it adds. Schemes not involving temporal updates are best for near-term development of the analytic framework.

10.  The concepts of ***Technology Readiness Level*** and ***Technology Performance Level*** may be too high level for modeling, though they may be useful in communication.

11. In the long term, ***SEDS*** may play an important role in contextualizing and evaluating portfolios, so compatibility, both in method and software, needs consideration.
