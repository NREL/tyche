% Production-Function Approach
% DRAFT
% 4 March 2020


# Concept

We separate the financial and conversion-efficiency aspects of the production process, which are generic across all technologies, from the physical and technical aspects, which are necessarily specific to the particular process. The motivation for this is that the financial and waste computations can be done uniformly for any technology (even for disparate ones such as PV cells and biofuels) and that different experts may be required to assess the cost, waste, and techno-physical aspects of technological progress.


# Formulation


## Sets

| Set                 | Description   | Examples                                           |
|---------------------|---------------|----------------------------------------------------|
| $c \in \mathcal{C}$ | capital       | equipment                                          |
| $f \in \mathcal{F}$ | fixed cost    | rent, insurance                                    |
| $i \in \mathcal{I}$ | input         | feedstock, labor                                   |
| $o \in \mathcal{O}$ | output        | product, co-product, waste                         |
| $m \in \mathcal{M}$ | metric        | cost, jobs, carbon footprint, efficiency, lifetime |
| $t \in \mathcal{T}$ | technical     | temperature, pressure                              |


## Variables

| Variable   | Type       | Description           | Units         |
|------------|------------|-----------------------|---------------|
| $K$        | calculated | unit cost             | USD/unit      |
| $C_c$      | cost       | capital cost          | USD           |
| $\tau_c$   | cost       | lifetime of capital   | year          |
| $S$        | cost       | scale of operation    | unit/year     |
| $F_f$      | cost       | fixed cost            | USD/year      |
| $I_i$      | input      | input quantity        | input/unit    |
| $I^*_i$    | calculated | ideal input quantity  | input/unit    |
| $\eta_i$   | waste      | input efficiency      | input/input   |
| $p_i$      | cost       | input price           | USD/input     |
| $O_o$      | calculated | ideal output quantity | output/unit   |
| $O^*_o$    | calculated   | output quantity     | output/unit   |
| $\eta'_o$  | waste      | output efficiency     | output/output |
| $p'_o$     | cost       | output price (+/-)    | USD/output    |
| $\mu_m$    | calculated | metric                | metric/unit   |
| $P_o$      | function   | production function   | output/unit   |
| $M_m$      | function   | metric function       | metric/unit   |
| $\alpha_t$ | parameter  | technical parameter   | -             |


## Cost

The per-unit cost is computed using a simple levelization formula:

$K = \left( \sum_c C_c / \tau_c + \sum_f F_f \right) / S + \sum_i p_i \cdot I_i - \sum_o p'_o \cdot O_o$


## Waste

The waste relative to the idealized production process is captured by the $\eta$ parameters. Expert elicitation might estimate how the $\eta$s would change in response to R&D investment.

*   Waste of input: $I^*_i = \eta_i I_i$.
*   Waste of output: $O_o = \eta'_o O^*_o$.


## Production

The production function idealizes production by ignoring waste, but accounting for physical and technical processes (e.g., stoichiometry). This requires a technical model or a tabulation/fit of the results of technical modeling.

$O^*_o = P_o(\mathcal{C}, \mathcal{F}, I^*_i, \alpha_t)$


## Metrics

Metrics such as efficiency, lifetime, or carbon footprint are also compute based on the physical and technical characteristics of the process. This requires a technical model or a tabulation/fit of the results of technical modeling.

$\mu_m = M_m(\mathcal{C}, \mathcal{F}, I_i, O_o, \alpha_t)$


# Experts

Each expert elicitation takes the form of an assessment of the probability and range (10th to 90th percentile) of change in the cost or waste parameters or the production or metric functions.


# Implementation

Database tables (one per set) hold all of the variables and the expert assessments. These tables are augmented by concise code with mathematical representations of the production and metric functions.

The Monte-Carlo computations are amenable to fast tensor-based implementation in Python.


# Examples


## Idealized electrolysis of water

Here is a very simple model for electrolysis of water. We just have water, electricity, a catalyst, and some lab space. We choose the fundamental unit of operation to be moles of H~2~:

\ \ \ \ \ H~2~O → H~2~ + ½ O~2~

Experts could assess how much R&D to increase the various efficiencies $\eta$ would cost. They could also suggest different catalysts, adding alkali, or replacing the process with PEM.


### Tracked quantities.

$\mathcal{C} = \{ \mathrm{catalyst} \}$

$\mathcal{F} = \{ \mathrm{rent} \}$

$\mathcal{I} = \{ \mathrm{water}, \mathrm{electricity} \}$

$\mathcal{O} = \{ \mathrm{oxygen}, \mathrm{hydrogen} \}$

$\mathcal{M} = \{ \mathrm{jobs} \}$


### Current design.

$I_\mathrm{water} = 19.04~\mathrm{g/mole}$

$\eta_\mathrm{water} = 0.95$ (due to mass transport loss on input)

$I_\mathrm{electricity} = 279~\mathrm{kJ/mole}$

$\eta_\mathrm{electricity} = 0.85$ (due to ohmic losses on input)

$\eta_\mathrm{oxygen} = 0.90$ (due to mass transport loss on output)

$\eta_\mathrm{hydrogen} = 0.90$ (due to mass transport loss on output)


### Current costs.

$C_\mathrm{catalyst} = 0.63~\mathrm{USD}$ (Al-Ni catalyst)

$\tau_\mathrm{catalyst} = 3~\mathrm{yr}$ (effective lifetime of Al-Ni catalyst)

$F_\mathrm{rent} = 1000~\mathrm{USD/yr}$

$S = 6650~\mathrm{mole/yr}$ (rough estimate for a 50W setup)


### Current prices.

$p_\mathrm{water} = 4.8 \cdot 10^{-3}~\mathrm{USD/mole}$

$p_\mathrm{electricity} = 3.33 \cdot 10^{-5}~\mathrm{USD/kJ}$

$p_\mathrm{oxygen} = 3.0 \cdot 10^{-3}~\mathrm{USD/g}$

$p_\mathrm{hydrogen} = 1.0 \cdot 10^{-2}~\mathrm{USD/g}$


### Production function (à la Leontief)

$P_\mathrm{oxygen} = \left( 16.00~\mathrm{g} \right) \cdot \min \left\{ \frac{I^*_\mathrm{water}}{18.08~\mathrm{g}}, \frac{I^*_\mathrm{electricity}}{237~\mathrm{kJ}} \right\}$

$P_\mathrm{hydrogen} = \left( 2.00~\mathrm{g} \right) \cdot \min \left\{ \frac{I^*_\mathrm{water}}{18.08~\mathrm{g}}, \frac{I^*_\mathrm{electricity}}{237~\mathrm{kJ}} \right\}$


### Metric function.

$M_\mathrm{jobs} = 1.5 \cdot 10^{-4}~\mathrm{job/mole}$


### Performance of current design.

$K = 0.18~\mathrm{USD/mole}$ (i.e., not profitable since it is positive)

$O_\mathrm{oxygen} = 14~\mathrm{g/mole}$

$O_\mathrm{hydrogen} = 1.8~\mathrm{g/mole}$

$\mu_\mathrm{jobs} = 1.5 \cdot 10^{-4}~\mathrm{job/mole}$


# Implementation

See \<<https://github.com/NREL/portfolio/tree/master/production-function/framework/code/tyche/>\> for the `tyche` package that computes cost, production, and metrics from a technology design.


## Database tables

Each analysis case is represented by a `Technology` and a `Scenario` within that technology.


### Metadata about indices

The `indices` table simply describes the various indices available for the variables. The `Offset` column specifies the memory location in the argument for the production and metric functions.

| Technology          | Type    | Index       | Offset   | Description | Notes |
|---------------------|---------|-------------|---------:|-------------|-------|
| Simple electrolysis | Capital | Catalyst    | 0        | Catalyst    |       |
| Simple electrolysis | Fixed   | Rent        | 0        | Rent        |       |
| Simple electrolysis | Input   | Water       | 0        | Water       |       |
| Simple electrolysis | Input   | Electricity | 1        | Electricity |       |
| Simple electrolysis | Output  | Oxygen      | 0        | Oxygen      |       |
| Simple electrolysis | Output  | Hydrogen    | 1        | Hydrogen    |       |
| Simple electrolysis | Metric  | Jobs        | 0        | Jobs        |       |


### Design variables

The `design` table specifies the values of all of the variables in the mathematical formulation of the design.

| Technology          | Scenario | Variable          | Index       | Value   | Units    | Notes                       |
|---------------------|----------|-------------------|-------------|--------:|----------|-----------------------------|
| Simple electrolysis | Base     | Input             | Water       | 19.04   | g/mole   |  $I_\mathrm{water}$         |
| Simple electrolysis | Base     | Input Efficiency  | Water       | 0.95    | 1        | $\eta_\mathrm{water}$       |
| Simple electrolysis | Base     | Input             | Electricity | 279     | kJ/mole  |  $I_\mathrm{electricity}$   |
| Simple electrolysis | Base     | Input Efficiency  | Electricity | 0.85    | 1        | $\eta_\mathrm{electricity}$ |
| Simple electrolysis | Base     | Output Efficiency | Oxygen      | 0.90    | 1        | $\eta_\mathrm{oxygen}$      |
| Simple electrolysis | Base     | Output Efficiency | Hydrogen    | 0.90    | 1        | $\eta_\mathrm{hydrogen}$    |
| Simple electrolysis | Base     | Capital cost      | Catalyst    | 0.63    | USD      | $C_\mathrm{catalyst}$       |
| Simple electrolysis | Base     | Lifetime          | Catalyst    | 3       | yr       | $\tau_\mathrm{catalyst}$    |
| Simple electrolysis | Base     | Fixed cost        | Rent        | 1000    | USD/yr   | $F_\mathrm{rent}$           |
| Simple electrolysis | Base     | Scale             |             | 6650    | mole/yr  | $S$                         |
| Simple electrolysis | Base     | Input price       | Water       | 4.8e-3  | USD/mole | $p_\mathrm{water}$          |
| Simple electrolysis | Base     | Input price       | Electricity | 3.33e-5 | USD/kJ   | $p_\mathrm{electricity}$    |
| Simple electrolysis | Base     | Output price      | Oxygen      | 3.0e-3  | USD/g    | $p_\mathrm{oxygen}$         |
| Simple electrolysis | Base     | Output price      | Hydrogen    | 1.0e-2  | USD/g    | $p_\mathrm{hydrogen}$       |


### Metadata for functions

The `functions` table simply documents which Python module and functions to use for the technology and scenario.

| Technology          | Module              | Production | Metrics | Notes |
|---------------------|---------------------|------------|---------|-------|
| Simple electrolysis | simple_electrolysis | production | metrics |       |


### Parameters for functions

The `parameters` table contains ad-hoc parameters specific to the particular production and metrics functions. The `Offset` column specifies the memory location in the argument for the production and metric functions.

| Technology          | Scenario | Parameter               | Offset   | Value  | Units    | Notes |
|---------------------|----------|-------------------------|---------:|-------:|----------|-------|
| Simple electrolysis | Base     | Oxygen production       | 0        | 16.00  | g        |       |
| Simple electrolysis | Base     | Hydrogen production     | 1        | 2.00   | g        |       |
| Simple electrolysis | Base     | Water consumption       | 2        | 18.08  | g        |       |
| Simple electrolysis | Base     | Electricity consumption | 3        | 237    | kJ       |       |
| Simple electrolysis | Base     | Jobs                    | 4        | 1.5e-4 | job/mole |       |


### Units for results

The `results` table simply specifies the units for the results.

| Technology          | Variable | Index    | Units    | Notes |
|---------------------|----------|----------|----------|-------|
| Simple electrolysis | Cost     | Cost     | USD/mole |       |
| Simple electrolysis | Output   | Oxygen   | g/mole   |       |
| Simple electrolysis | Output   | Hydrogen | g/mole   |       |
| Simple electrolysis | Metric   | Jobs     | job/mole |       |


## Python module and functions

Each technology design requires a Python module with a production and metrics function.

```python
# Simple electrolysis.


# All of the computations must be vectorized, so use `numpy`.
import numpy as np


# Production function.
def production(capital, fixed, input, parameter):

  # Moles of input.
  water       = np.divide(input[0], parameter[2])
  electricity = np.divide(input[1], parameter[3])

  # Moles of output.
  output = np.minimum(water, electricity)

  # Grams of output.
  oxygen   = np.multiply(output, parameter[0])
  hydrogen = np.multiply(output, parameter[1])

  # Package results.
  return np.vstack([oxygen, hydrogen])


# Metrics function.
def metrics(capital, fixed, input, outputs, parameter):

  # Trivial jobs calculation.
  jobs = parameter[4]

  # Package results.
  return np.vstack([jobs])
```
