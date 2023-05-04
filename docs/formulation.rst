.. _sec-formulation:

Mathematical Formulation
========================

We separate the financial and conversion-efficiency aspects of a
production process, which are generic across all technologies, from the
physical and technical aspects, which are necessarily specific to the
particular process. The motivation for this is that the financial and
waste computations can be done uniformly for any technology (even for
disparate ones such as PV cells and biofuels) and that different experts
may be required to assess the cost, waste, and techno-physical aspects
of technological progress. :numref:`tbl-sets` defines the indices that are used
for the variables that are defined in :numref:`tbl-variables`.

.. _tbl-sets:

.. table:: Definitions for set indices used for variable subscripts.

   ========================== =================== ================================================== 
   Set                        Description         Examples                                            
   ========================== =================== ================================================== 
   :math:`c \in \mathcal{C}`  capital             equipment                                           
   :math:`f \in \mathcal{F}`  fixed cost          rent, insurance                                     
   :math:`i \in \mathcal{I}`  input               feedstock, labor                                    
   :math:`o \in \mathcal{O}`  output              product, co-product, waste                          
   :math:`m \in \mathcal{M}`  metric              cost, jobs, carbon footprint, efficiency, lifetime  
   :math:`p \in \mathcal{P}`  technical parameter temperature, pressure                               
   :math:`\nu \in N`          technology type     electrolysis, PV cell                               
   :math:`\theta \in \Theta`  design              the result of a particular investment               
   :math:`\chi \in X`         investment category investment alternatives                             
   :math:`\phi \in \Phi_\chi` investment          a particular investment                             
   :math:`\omega \in \Omega`  portfolio           a basket of investments                             
   ========================== =================== ================================================== 


.. _tbl-variables:

.. table:: Definitions for variables.

   ====================================== =============== ====================== =============
   Variable                               Type            Description            Units
   ====================================== =============== ====================== =============
   :math:`K`                              calculated      unit cost              USD/unit
   :math:`C_c`                            function        capital cost           USD
   :math:`\tau_c`                         cost            lifetime of capital    year
   :math:`S`                              cost            scale of operation     unit/year
   :math:`F_f`                            function        fixed cost             USD/year
   :math:`I_i`                            input           input quantity         input/unit
   :math:`I^*_i`                          calculated      ideal input quantity   input/unit
   :math:`\eta_i`                         waste           input efficiency       input/input
   :math:`p_i`                            cost            input price            USD/input
   :math:`O_o`                            calculated      output quantity        output/unit
   :math:`O^*_o`                          calculated      ideal output quantity  output/unit
   :math:`\eta^\prime_o`                  waste           output efficiency      output/output
   :math:`p^\prime_o`                     cost            output price (+/-)     USD/output
   :math:`\mu_m`                          calculated      metric                 metric/unit
   :math:`P_o`                            function        production function    output/unit
   :math:`M_m`                            function        metric function        metric/unit
   :math:`\alpha_p`                       parameter       technical parameter    (mixed)
   :math:`\xi_\theta`                     variable        design inputs          (mixed)
   :math:`\zeta_\theta`                   variable        design outputs         (mixed)
   :math:`\psi`                           function        design evaluation      (mixed)
   :math:`\sigma_\phi`                    function        design probability     1
   :math:`q_\phi`                         variable        investment cost        USD
   :math:`\mathbf{\zeta}_\phi`            random variable investment outcome     (mixed)
   :math:`\mathbf{Z}(\omega)`             random variable portfolio outcome      (mixed)
   :math:`Q(\omega)`                      calculated      portfolio cost         USD
   :math:`Q^\mathrm{min}`                 parameter       minimum portfolio cost USD
   :math:`Q^\mathrm{max}`                 parameter       maximum portfolio cost USD
   :math:`q^\mathrm{min}_\phi`            parameter       minimum category cost  USD
   :math:`q^\mathrm{max}_\phi`            parameter       maximum category cost  USD
   :math:`Z^\mathrm{min}`                 parameter       minimum output/metric  (mixed)
   :math:`Z^\mathrm{max}`                 parameter       maximum output/metric  (mixed)
   :math:`\mathbb{F}`, :math:`\mathbb{G}` operator        evaluate probabilities (mixed)
   ====================================== =============== ====================== =============


Cost
----

The cost characterizations (capital and fixed costs) are represented as
functions of the scale of operations and of the technical parameters in
the design:

-  Capital cost: :math:`C_c(S, \alpha_p)`.
-  Fixed cost: :math:`F_f(S, \alpha_p)`.

The per-unit cost is computed using a simple levelization formula:

:math:`K = \left( \sum_c C_c / \tau_c + \sum_f F_f \right) / S + \sum_i p_i \cdot I_i - \sum_o p^\prime_o \cdot O_o`


Waste
-----

The waste relative to the idealized production process is captured by
the :math:`\eta` parameters. Expert elicitation might estimate how the
:math:`\eta`\ s would change in response to R&D investment.

-  Waste of input: :math:`I^*_i = \eta_i I_i`.
-  Waste of output: :math:`O_o = \eta^\prime_o O^*_o`.


Production
----------

The production function idealizes production by ignoring waste, but
accounting for physical and technical processes (e.g., stoichiometry).
This requires a technical model or a tabulation/fit of the results of
technical modeling.

:math:`O^*_o = P_o(S, C_c, \tau_c, F_f, I^*_i, \alpha_p)`


Metrics
-------

Metrics such as efficiency, lifetime, or carbon footprint are also
compute based on the physical and technical characteristics of the
process. This requires a technical model or a tabulation/fit of the
results of technical modeling. We use the convention that higher values
are worse and lower values are better.

:math:`\mu_m = M_m(S, C_c, \tau_c, F_f, I_i, I^*_i, O^*_o, O_o, K, \alpha_p)`


Designs
---------

A *design* represents a state of affairs for a technology :math:`\nu`.
If we denote the design as :math:`\theta`, we have the tuple of input
variables

:math:`\xi_\theta = \left(S, C_c, \tau_c, F_f, I_i, \eta_i, \eta^\prime_o, \alpha_p, p_i, p^\prime_o\middle) \right|_\theta`

and the tuple of output variables

:math:`\zeta_\theta = \left(K, I^*_i, O^*_o, O_o, \mu_m\middle) \right|_\theta`

and their relationship

:math:`\zeta_\theta = \psi_\nu\left(\xi_\theta\middle) \right|_{\nu = \nu(\theta)}`

given the tuple of functions

:math:`\psi_\nu = \left(P_o, M_m\middle) \right|_\nu`

for the technology.


Investments
-----------

An *investment* :math:`\phi` assigns a probability distribution to
designs:

:math:`\sigma_\phi(\theta) = P\left(\theta \middle| \phi\right)`.

such that

:math:`\int d\theta \sigma_\phi(\theta) = 1` or
:math:`\sum_\theta \sigma_\phi(\theta) = 1`,

depending upon whether one is performing the computations discretely or
continuously. Expectations and other measures on probability
distributions can be computed from the :math:`\sigma_\phi(\theta)`. We
treat the outcome :math:`\mathbf{\zeta}_\phi` as a random variable for
the outcomes :math:`\zeta_\theta` according to the distribution
:math:`\sigma_\phi(\theta)`.

Because investment options may be mutually exclusive, as is the case for
investing in the same R&D at different funding levels, we say
:math:`\Phi_\chi` is the set of mutually exclusive investments (i.e.,
only one can occur simultaneously) in investment category :math:`\chi`:
investments in different categories :math:`\chi` can be combined
arbitrarily, but just one investment from each :math:`\Phi_\chi` may be
chosen.

Thus the universe of all portfolios is
:math:`\Omega = \prod_\chi \Phi_\chi`, so a particular portfolio
:math:`\omega \in \Omega` has components
:math:`\phi = \omega_\chi \in \Phi_\chi`. The overall outcome of a
portfolio is a random variable:

:math:`\mathbf{Z}(\omega) = \sum_\chi \mathbf{\zeta}_\phi \mid_{\phi = \omega_\chi}`

The cost of an investment in one of the constituents :math:`\phi` is
:math:`q_\phi`, so the cost of a porfolio is:

:math:`Q(\omega) = \sum_\chi q_\phi \mid_{\phi = \omega_\chi}`


Decision problem
----------------

The multi-objective decision problem is

:math:`\min_{\omega \in \Omega} \  \mathbb{F} \  \mathbf{Z}(\omega)`

such that

:math:`Q^\mathrm{min} \leq Q(\omega) \leq Q^\mathrm{max}` ,

:math:`q^\mathrm{min}_\phi \leq q_{\phi=\omega_\chi} \leq q^\mathrm{max}_\phi`
,

:math:`Z^\mathrm{min} \leq \mathbb{G} \  \mathbf{Z}(\omega) \leq Z^\mathrm{max}`
,

where :math:`\mathbb{F}` and :math:`\mathbb{G}` are the expectation
operator :math:`\mathbb{E}`, the value-at-risk, or another operator on
probability spaces. Recall that :math:`\mathbf{Z}` is a vector with
components for cost :math:`K` and each metric :math:`\mu_m`, so this is
a multi-objective problem.

The two-stage decision problem is a special case of the general problem
outlined here: Each design :math:`\theta` can be considers as a
composite of one or more stages.


Experts
-------

Each expert elicitation takes the form of an assessment of the
probability and range (e.g., 10th to 90th percentile) of change in the
cost or waste parameters or the production or metric functions. In
essence, the expert elicitation defines :math:`\sigma_\phi(\theta)` for
each potential design :math:`\theta` resulting from each investment :math:`\phi`.
