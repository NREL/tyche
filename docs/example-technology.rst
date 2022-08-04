Electrolysis Example
====================

Here is a very simple model for electrolysis of water. We just have
water, electricity, a catalyst, and some lab space. We choose the
fundamental unit of operation to be moles of H\ :sub:`2`:

     H\ :sub:`2`\ O → H\ :sub:`2` + ½ O\ :sub:`2`

For this example, we treat the catalyst as the capital that we use to transform inputs into outputs. Our inputs are water and electricity, and our outputs are oxygen and hydrogen. Our only fixed cost is the rent on the lab space at $1000/year. Using our past experience with electrolysis technology as well as some historical data, we estimate that we'll be able to produce 6650 mol/year of hydrogen and at this scale, our catalyst has a lifetime of about 3 years. The metrics we'd like to calculate for our electrolysis technology are cost, greenhouse gas (GHG) emissions, and jobs created. Based on this information, the *designs* dataset for the base case electrolysis technology is as shown in :numref:`tbl-electrolysisdesigns`.

.. _tbl-electrolysisdesigns:
.. table:: *designs* dataset for the base case (without any R&D) of the simple electrolysis example technology.

 ===================== =================== =================== ============= ========== ========= ======================================
 Technology            Scenario            Variable            Index         Value      Units     Notes
 ===================== =================== =================== ============= ========== ========= ======================================
 Simple electrolysis   Base Electrolysis   Input               Water         19.04      g/mole    Note
 Simple electrolysis   Base Electrolysis   Input efficiency    Water         0.95       1         Due to mass transport loss on input.
 Simple electrolysis   Base Electrolysis   Input               Electricity   279        kJ/mole   Note
 Simple electrolysis   Base Electrolysis   Input efficiency    Electricity   0.85       l         Due to ohmic losses on input.
 Simple electrolysis   Base Electrolysis   Output efficiency   Oxygen        0.9        1         Due to mass transport loss on output.
 Simple electrolysis   Base Electrolysis   Output efficiency   Hydrogen      0.9        1         Due to mass transport loss on output.
 Simple electrolysis   Base Electrolysis   Lifetime            Catalyst      3          yr        Effective lifetime of Al-Ni catalyst.
 Simple electrolysis   Base Electrolysis   Scale               n/a           6650       mole/yr   Rough estimate for a 50W setup.
 Simple electrolysis   Base Electrolysis   Input price         Water         4.80E-03   USD/mole  Note
 Simple electrolysis   Base Electrolysis   Input price         Electricity   3.33E-05   USD/kJ    Note
 Simple electrolysis   Base Electrolysis   Output price        Oxygen        3.00E-03   USD/g     Note
 Simple electrolysis   Base Electrolysis   Output price        Hydrogen      1.00E-02   USD/g     Note
 ===================== =================== =================== ============= ========== ========= ======================================

Note that this is not the only way to model the electrolysis technology. We could choose to purchase lab space and equipment instead of renting, in which case we would have more types of capital, each with a particular lifetime. We could treat the oxygen output from our technology as waste instead of a coproduct and remove it from the model entirely. We could operate at a different scale and perhaps change our fixed or capital costs by doing so. Depending on where we operate this technology, our input and output prices will likely change. The Tyche framework offers great flexibility in representing technologies and technology systems; it is unlikely that there will only be a single correct way to model a decision context.

A key quantity that is not included in the *designs* dataset is our fixed cost, rent for the lab space. This quantity is included in the *parameters* dataset in :numref:`tbl-electrolysisparams`, along with the necessary data to calculate our metrics of interest (cost, GHG, jobs).

.. _tbl-electrolysisparams:
.. table:: *parameters* dataset for the base case (without any R&D) of the simple electrolysis example technology.

 ===================== =================== ===================================== =========== ========== =========== =====================================
 Technology            Scenario            Parameter                             Offset      Value      Units       Notes
 ===================== =================== ===================================== =========== ========== =========== =====================================
 Simple electrolysis   Base Electrolysis   Oxygen production                     0           16         g           Note
 Simple electrolysis   Base Electrolysis   Hydrogen production                   1           2          g           Note
 Simple electrolysis   Base Electrolysis   Water consumption                     2           18.08      g           Note
 Simple electrolysis   Base Electrolysis   Electricity consumption               3           237        kJ          Note
 Simple electrolysis   Base Electrolysis   Jobs                                  4           1.50E-04   job/mole    Note
 Simple electrolysis   Base Electrolysis   Reference scale                       5           6650       mole/yr     Note
 Simple electrolysis   Base Electrolysis   Reference capital cost for catalyst   6           0.63       USD         Note
 Simple electrolysis   Base Electrolysis   Reference fixed cost for rent         7           1000       USD/yr      Note
 Simple electrolysis   Base Electrolysis   GHG factor for water                  8           0.00108    gCO2e/g     based on 244,956 gallons = 1 Mg CO2e
 Simple electrolysis   Base Electrolysis   GHG factor for electricity            9           0.138      gCO2e/kJ    based on 1 kWh = 0.5 kg CO2e
 ===================== =================== ===================================== =========== ========== =========== =====================================

Within our R&D decision context, we're interested in increasing the input and output efficiencies of this process so we can produce hydrogen as cheaply as possible. Experts could assess how much R&D to increase the various efficiencies :math:`\eta` would cost. They could also suggest different catalysts, adding alkali, or replacing the process with PEM.

Production function (à la Leontief)
-----------------------------------

:math:`P_\mathrm{oxygen} = \left( 16.00~\mathrm{g} \right) \cdot \min \left\{ \frac{I^*_\mathrm{water}}{18.08~\mathrm{g}}, \frac{I^*_\mathrm{electricity}}{237~\mathrm{kJ}} \right\}`

:math:`P_\mathrm{hydrogen} = \left( 2.00~\mathrm{g} \right) \cdot \min \left\{ \frac{I^*_\mathrm{water}}{18.08~\mathrm{g}}, \frac{I^*_\mathrm{electricity}}{237~\mathrm{kJ}} \right\}`


Metric functions
----------------

:math:`M_\mathrm{cost} = K / O_\mathrm{hydrogen}`

:math:`M_\mathrm{GHG} = \left( \left( 0.00108~\mathrm{gCO2e/gH20} \right) I_\mathrm{water} + \left( 0.138~\mathrm{gCO2e/kJ} \right) I_\mathrm{electricity} \right) / O_\mathrm{hydrogen}`

:math:`M_\mathrm{jobs} = \left( 0.00015~\mathrm{job/mole} \right) / O_\mathrm{hydrogen}`


Performance of current design.
------------------------------

:math:`K = 0.18~\mathrm{USD/mole}` (i.e., not profitable since it is
positive)

:math:`O_\mathrm{oxygen} = 14~\mathrm{g/mole}`

:math:`O_\mathrm{hydrogen} = 1.8~\mathrm{g/mole}`

:math:`\mu_\mathrm{cost} = 0.102~\mathrm{USD/gH2}`

:math:`\mu_\mathrm{GHG} = 21.4~\mathrm{gCO2e/gH2}`

:math:`\mu_\mathrm{jobs} = 0.000083~\mathrm{job/gH2}`


Technology Model
----------------

Each technology design requires a Python file with a capital cost, a fixed cost, a production, and a metrics function. :numref:`lst-electrolysis` shows these functions for the simple electrolysis example.

.. code-block:: python
   :name: lst-electrolysis
   :caption: Example technology-defining functions.


   # Simple electrolysis.
   
   
   # All of the computations must be vectorized, so use `numpy`.
   import numpy as np
   
   
   # Capital-cost function.
   def capital_cost(
     scale,
     parameter
   ):
   
     # Scale the reference values.
     return np.stack([np.multiply(
       parameter[6], np.divide(scale, parameter[5])
     )])
   
   
   # Fixed-cost function.
   def fixed_cost(
     scale,
     parameter
   ):
   
     # Scale the reference values.
     return np.stack([np.multiply(
       parameter[7],
       np.divide(scale, parameter[5])
     )])
   
   
   # Production function.
   def production(
     capital,
     fixed,
     input,
     parameter
   ):
   
     # Moles of input.
     water       = np.divide(input[0], parameter[2])
     electricity = np.divide(input[1], parameter[3])
   
     # Moles of output.
     output = np.minimum(water, electricity)
   
     # Grams of output.
     oxygen   = np.multiply(output, parameter[0])
     hydrogen = np.multiply(output, parameter[1])
   
     # Package results.
     return np.stack([oxygen, hydrogen])
   
   
   # Metrics function.
   def metrics(
     capital,
     fixed,
     input_raw,
     input,
     img/output_raw,
     output,
     cost,
     parameter
   ):
   
     # Hydrogen output.
     hydrogen = output[1]
   
     # Cost of hydrogen.
     cost1 = np.divide(cost, hydrogen)
   
     # Jobs normalized to hydrogen.
     jobs = np.divide(parameter[4], hydrogen)
   
     # GHGs associated with water and electricity.
     water       = np.multiply(input_raw[0], parameter[8])
     electricity = np.multiply(input_raw[1], parameter[9])
     co2e = np.divide(np.add(water, electricity), hydrogen)
   
     # Package results.
     return np.stack([cost1, jobs, co2e])

