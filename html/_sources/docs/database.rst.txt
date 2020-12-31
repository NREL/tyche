Database Schema
===============

Database tables (one per set) hold all of the variables and the expert
assessments. These tables are augmented by concise code with
mathematical representations of the production and metric functions.

The Monte-Carlo computations are amenable to fast tensor-based
implementation in Python.

See
<https://github.com/NREL/portfolio/tree/master/production-function/framework/code/tyche/>
for the ``tyche`` package that computes cost, production, and metrics
from a technology design.

Each analysis case is represented by a ``Technology`` and a ``Scenario``
within that technology. In the specifications for the individual tables,
we use the simple electrolysis example to populate the table.


Metadata about indices
----------------------

The ``indices`` table (see :numref:`tbl-indices`) simply describes the various
indices available for the variables. The ``Offset`` column specifies the
memory location in the argument for the production and metric functions.

.. _tbl-indices:

.. table:: Example of the ``indices`` table.

   =================== ======== ============ ====== =========== ===== 
   Technology           Type     Index       Offset Description Notes
   =================== ======== ============ ====== =========== ===== 
   Simple electrolysis  Capital  Catalyst     0     Catalyst         
   Simple electrolysis  Fixed    Rent         0     Rent             
   Simple electrolysis  Input    Water        0     Water            
   Simple electrolysis  Input    Electricity  1     Electricity      
   Simple electrolysis  Output   Oxygen       0     Oxygen           
   Simple electrolysis  Output   Hydrogen     1     Hydrogen         
   Simple electrolysis  Metric   Cost         0     Cost             
   Simple electrolysis  Metric   Jobs         1     Jobs             
   Simple electrolysis  Metric   GHG          2     GHGs             
   =================== ======== ============ ====== =========== ===== 


Design variables
----------------

The ``design`` table (see :numref:`tbl-designs`) specifies the values of all of
the variables in the mathematical formulation of the design. Note that
the ``Value`` column can either contain numeric literals or Python
expressions specifying probability distribution functions. For example,
a normal distribution with mean of five and standard deviation of two
would be written ``st.norm(5, 2)``. All of the `Scipy probability
distribution
functions <https://docs.scipy.org/doc/scipy-1.4.1/reference/tutorial/stats/continuous.html#continuous-distributions-in-scipy-stats>`__
are available for use, as are two special functions, ``constant`` and
``mixture``. The ``constant`` distribution is just a single constant
value; the ``mixture`` distribution is the mixture of a list of
distributions, with specified relative weights. The ``mixture`` function
is particularly important because it allows one to specify a first
distribution in the case of an R&D breakthrough, but a second
distribution if no breakthrough occurs.

.. _tbl-designs:

.. table:: Example of the ``designs`` table. 

   =================== ========= ================= =========== ======= ======== ================================
   Technology           Scenario Variable          Index       Value   Units    Notes                        
   =================== ========= ================= =========== ======= ======== ================================
   Simple electrolysis  Base     Input             Water       19.04   g/mole   :math:`I_\mathrm{water}`
   Simple electrolysis  Base     Input Efficiency  Water       0.95    1        :math:`\eta_\mathrm{water}`
   Simple electrolysis  Base     Input             Electricity 279     kJ/mole  :math:`I_\mathrm{electricity}`
   Simple electrolysis  Base     Input Efficiency  Electricity 0.85    1        :math:`\eta_\mathrm{electricity}`
   Simple electrolysis  Base     Output Efficiency Oxygen      0.90    1        :math:`\eta_\mathrm{oxygen}`
   Simple electrolysis  Base     Output Efficiency Hydrogen    0.90    1        :math:`\eta_\mathrm{hydrogen}`
   Simple electrolysis  Base     Lifetime          Catalyst    3       yr       :math:`\tau_\mathrm{catalyst}`
   Simple electrolysis  Base     Scale                         6650    mole/yr  :math:`S`
   Simple electrolysis  Base     Input price       Water       4.8e-3  USD/mole :math:`p_\mathrm{water}`
   Simple electrolysis  Base     Input price       Electricity 3.33e-5 USD/kJ   :math:`p_\mathrm{electricity}`
   Simple electrolysis  Base     Output price      Oxygen      3.0e-3  USD/g    :math:`p_\mathrm{oxygen}`
   Simple electrolysis  Base     Output price      Hydrogen    1.0e-2  USD/g    :math:`p_\mathrm{hydrogen}`
   =================== ========= ================= =========== ======= ======== ================================


Metadata for functions
----------------------

The ``functions`` table (see :numref:`tbl-functions`) simply documents which
Python module and functions to use for the technology and scenario.
Currently only the ``numpy`` style of function is supported, but later
``plain`` Python functions and ``tensorflow`` functions will be allowed.

.. _tbl-functions:

.. table:: Example of the ``functions`` table.

   =================== ===== =================== ============ ========== ========== ======= ===== 
   Technology          Style Module              Capital      Fixed      Production Metrics Notes 
   =================== ===== =================== ============ ========== ========== ======= ===== 
   Simple electrolysis numpy simple_electrolysis capital_cost fixed_cost production metrics       
   =================== ===== =================== ============ ========== ========== ======= ===== 


Parameters for functions
------------------------

The ``parameters`` table (see :numref:`tbl-parameters`) contains ad-hoc
parameters specific to the particular production and metrics functions.
The ``Offset`` column specifies the memory location in the argument for
the production and metric functions.

.. _tbl-parameters:

.. table:: Example of the ``parameters`` table.

   =================== ======== =================================== ====== ======= ======== ==================================== 
   Technology          Scenario Parameter                           Offset Value   Units    Notes                                
   =================== ======== =================================== ====== ======= ======== ==================================== 
   Simple electrolysis Base     Oxygen production                   0      16.00   g                                             
   Simple electrolysis Base     Hydrogen production                 1      2.00    g                                             
   Simple electrolysis Base     Water consumption                   2      18.08   g                                             
   Simple electrolysis Base     Electricity consumption             3      237     kJ                                            
   Simple electrolysis Base     Jobs                                4      1.5e-4  job/mole                                      
   Simple electrolysis Base     Reference scale                     5      6650    mole/yr                                       
   Simple electrolysis Base     Reference capital cost for catalyst 6      0.63    USD                                           
   Simple electrolysis Base     Reference fixed cost for rent       7      1000    USD/yr                                        
   Simple electrolysis Base     GHG factor for water                8      0.00108 gCO2e/g  based on 244,956 gallons = 1 Mg CO2e 
   Simple electrolysis Base     GHG factor for electricity          9      0.138   gCO2e/kJ based on 1 kWh = 0.5 kg CO2e         
   =================== ======== =================================== ====== ======= ======== ==================================== 


Units for results
-----------------

The ``results`` table (see :numref:`tbl-results`) simply specifies the units for
the results.

.. _tbl-results:

.. table:: Example of the ``results`` table.

   =================== ======== ======== ========= =====
   Technology          Variable Index    Units     Notes
   =================== ======== ======== ========= =====
   Simple electrolysis Cost     Cost     USD/mole 
   Simple electrolysis Output   Oxygen   g/mole   
   Simple electrolysis Output   Hydrogen g/mole   
   Simple electrolysis Metric   Cost     job/gH2  
   Simple electrolysis Metric   Jobs     job/gH2  
   Simple electrolysis Metric   GHG      gCO2e/gH2
   =================== ======== ======== ========= =====


Tranches of investments.
------------------------

In the ``tranches`` table (see :numref:`tbl-tranches`), each *category* of
investment contains a set of mutually exclusive *tranches* that may be
associated with one or more *scenarios* defined in the ``designs``
table. Typically, a category is associated with a technology area and
each tranche corresponds to an investment strategy within that category.

.. _tbl-tranches:

.. table:: Example of the ``tranches`` table.

   ================ ======================= ================================= ======= ===== 
   Category         Tranche                 Scenario                          Amount  Notes 
   ================ ======================= ================================= ======= ===== 
   Electrolysis R&D No Electrolysis R&D     Base Electrolysis                 0             
   Electrolysis R&D Low Electrolysis R&D    Slow Progress on Electrolysis     1000000       
   Electrolysis R&D Medium Electrolysis R&D Moderate Progress on Electrolysis 2500000       
   Electrolysis R&D High Electrolysis R&D   Fast Progress on Electrolysis     5000000       
   ================ ======================= ================================= ======= ===== 


Investments
-----------

In the ``investments`` table (see :numref:`tbl-investments`), each *investment*
is associated with a single *tranche* in one or more *categories*. An
investment typically combines tranches from several different investment
categories.

.. _tbl-investments:

.. table:: Example of the ``investments`` table.

   =================== ================ ======================= =====
   Investment          Category         Tranche                 Notes
   =================== ================ ======================= =====
   No R&D Spending     Electrolysis R&D No Electrolysis R&D    
   Low R&D Spending    Electrolysis R&D Low Electrolysis R&D   
   Medium R&D Spending Electrolysis R&D Medium Electrolysis R&D
   High R&D Spending   Electrolysis R&D High Electrolysis R&D  
   =================== ================ ======================= =====
