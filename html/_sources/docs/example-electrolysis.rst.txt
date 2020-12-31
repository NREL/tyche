Electrolysis Example
====================

Here is a very simple model for electrolysis of water. We just have
water, electricity, a catalyst, and some lab space. We choose the
fundamental unit of operation to be moles of H\ :sub:`2`:

     H\ :sub:`2`\ O → H\ :sub:`2` + ½ O\ :sub:`2`

Experts could assess how much R&D to increase the various efficiencies
:math:`\eta` would cost. They could also suggest different catalysts,
adding alkali, or replacing the process with PEM.


Tracked quantities.
-------------------

:math:`\mathcal{C} = \{ \mathrm{catalyst} \}`

:math:`\mathcal{F} = \{ \mathrm{rent} \}`

:math:`\mathcal{I} = \{ \mathrm{water}, \mathrm{electricity} \}`

:math:`\mathcal{O} = \{ \mathrm{oxygen}, \mathrm{hydrogen} \}`

:math:`\mathcal{M} = \{ \mathrm{jobs} \}`


Current design.
---------------

:math:`I_\mathrm{water} = 19.04~\mathrm{g/mole}`

:math:`\eta_\mathrm{water} = 0.95` (due to mass transport loss on input)

:math:`I_\mathrm{electricity} = 279~\mathrm{kJ/mole}`

:math:`\eta_\mathrm{electricity} = 0.85` (due to ohmic losses on input)

:math:`\eta_\mathrm{oxygen} = 0.90` (due to mass transport loss on
output)

:math:`\eta_\mathrm{hydrogen} = 0.90` (due to mass transport loss on
output)


Current costs.
--------------

:math:`C_\mathrm{catalyst} = \left( 0.63~\mathrm{USD} \right) \cdot \frac{S}{6650~\mathrm{mole/yr}}`
(cost of Al-Ni catalyst)

:math:`\tau_\mathrm{catalyst} = 3~\mathrm{yr}` (effective lifetime of
Al-Ni catalyst)

:math:`F_\mathrm{rent} = \left( 1000~\mathrm{USD/yr} \right) \cdot \frac{S}{6650~\mathrm{mole/yr}}`

:math:`S = 6650~\mathrm{mole/yr}` (rough estimate for a 50W setup)


Current prices.
---------------

:math:`p_\mathrm{water} = 4.8 \cdot 10^{-3}~\mathrm{USD/mole}`

:math:`p_\mathrm{electricity} = 3.33 \cdot 10^{-5}~\mathrm{USD/kJ}`

:math:`p_\mathrm{oxygen} = 3.0 \cdot 10^{-3}~\mathrm{USD/g}`

:math:`p_\mathrm{hydrogen} = 1.0 \cdot 10^{-2}~\mathrm{USD/g}`


Production function (à la Leontief)
-----------------------------------

:math:`P_\mathrm{oxygen} = \left( 16.00~\mathrm{g} \right) \cdot \min \left\{ \frac{I^*_\mathrm{water}}{18.08~\mathrm{g}}, \frac{I^*_\mathrm{electricity}}{237~\mathrm{kJ}} \right\}`

:math:`P_\mathrm{hydrogen} = \left( 2.00~\mathrm{g} \right) \cdot \min \left\{ \frac{I^*_\mathrm{water}}{18.08~\mathrm{g}}, \frac{I^*_\mathrm{electricity}}{237~\mathrm{kJ}} \right\}`


Metric function.
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
