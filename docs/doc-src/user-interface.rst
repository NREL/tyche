User Interface
==============

The Eutychia interface is a user’s portal to interact with the Tyche
decision support tool. Users can make decisions to change investments
and the metrics by which they will be assessed (as described in the
following sections). Eutychia aims to aide in formalizing funding
processes to make technically and analytically-based decisions, through
modeling possible scenarios and generating visualizations to communicate
these results. Tool output aims to aide decision-makers in

1. **Focused analysis** comparing investment scenarios to examine impact
   across metrics when exploring options during the decision-making
   process and
2. **Broader communication** of Office goals externally, such as through
   the dissemination of a funding opportunity announcement.

**Feedback is appreciated to enhance the interface to best meet user
needs.**


User Input
----------

**Investment Categories** A user can suggest research foci by selecting
**investment categories** and **investment levels** ($) in each topic
area and/or across the investment portfolio. In the current iteration of
the Eutychia prototype, users have the option to select a budget for
each of the following investment categories:

1. Balance of System R&D
2. Inverter R&D
3. Module R&D

Later-stage iterations of the prototype will include as many categories
as the user selects for which data is available.

**Metrics** A user can also select up to three metrics to impact through
R&D on these selected investment categories and specify goals that must
be met. The current options include:

1. Greenhouse gas emissions (ΔgCO2e/system)
2. Labor (Δ$/system)
3. Levelized cost of energy (Δ$/kWh)


Modes
-----

The Eutychia interface operates in two modes:

1. **Explore Mode**, checked by default,
2. **Optimize Mode**, which can be enabled by deselecting “explore.” Entering Optimize Mode allows users to update optimization parameters.

The selected mode determines which user inputs can be edited. The
following table summarizes the parameters that can be updated, the
corresponding ``optimizer`` parameter name, and the widget (currently)
used to make this change.

================================== ================ ======== ============ =============
\                                  Parameter        Widget   Explore Mode Optimize Mode
================================== ================ ======== ============ =============
Investment level (USD) by category ``max_amount``   slider   X            X
Total portfolio investment (USD)   ``total_amount`` slider                X
Metric constraint                  ``min_metric``   slider                X
Optimization metric to maximize    ``metric``       dropdown              X
================================== ================ ======== ============ =============

In either mode, changes made to investment level(s) by category will be
reflected immediately in the output visualizations. In Optimize Mode,
once satisfied with the selected metrics, the user can click “optimize”
to model the chosen scenario.


Visualizations
--------------

Users are presented with the option to interact with the data in varying
levels of detail. These options are enabled to suit the needs of users,
from those who prefer a snapshot of the bigger picture for quick
analysis to those who would like to study the distributional probability
of achieving each metric. Plots are generated using the Seaborn 0.11.0
package. [1]_ The available visualizations in order of increasing level
of detail include:

1. **Heatmaps** (``heatmap``) with metric scaled to percent of the
   maximum possible improvement,
2. **Annotated heatmaps** with metric values overlayed, and
3. **Distributions** with the probability of ahieving each metric based
   on the number of samples. At this stage of development, these results
   can be viewed in columns (by metric) or in a grid. The user can
   select from the following options:

   -  Box plots (``boxplot``)
   -  Probability distributions (``kdeplot``)
   -  Violin plots (``violinplot``)

A user can toggle between their visualization options using the links
(heatmap, column, grid) at the top left-hand corner of the screen. By
default, Eutychia opens to the grid layout.


References
----------

.. [1]
   Michael Waskom, Olga Botvinnik, Maoz Gelbart, Joel Ostblom, Paul
   Hobson, Saulius Lukauskas, David C Gemperline, et al. 2020.
   Mwaskom/Seaborn: V0.11.0 (Sepetmber 2020). Zenodo.
   https://doi.org/10.5281/zenodo.4019146.
