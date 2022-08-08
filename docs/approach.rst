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

The framework is scalable, supporting rapid computation on laptops
computer and large-ensemble studies on high-performance computers (HPC).
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
to simulator or subsequent to it.

Four example technologies have been implemented as examples illustrating
framework’s use: biorefineries, electrolysis, residential photovoltaics
(PV), and utility-scale PV. A desktop user interface allows exploration
of the cost-benefit trade-offs in portfolio decision problems.


Mock FOA Definition
-------------------

Background
^^^^^^^^^^

Understanding the FOA process is essential to designing an effective
tool to make to make technically and analytically-based decisions. The
“Mock FOA” process takes a service design approach to understanding the
FOA-writing process as it stands. The Mock FOA began with interviews
with five previous DOE detailees and seven senior DOE staff who have led
multiple FOA development efforts. A major theme emerged: effective
communication of analysis logic and results poses one of the largest
challenges during the FOA process.

A decision-support tool could assist in the communication necessary to
percolate this technical information up the chain. Interview findings
were formalized in collaboration with the NREL service design team to
understand where such a tool could make the greatest impact. The team
considered the steps taken to issue a FOA, resources referenced, and
decision-makers involved.

Phases
~~~~~~

Interviews revealed that, while all FOA processes are unique and highly
non-linear, specific actions must occur. These characterize phases of
the FOA journey:

1. **Launch**. Decide to issue a FOA.
2. **Frame**. Formulate a plan to collect the information necessary to write the FOA
3. **Scope**. Investigate topic options.
4. **Draft**. Compile information into draft FOA.
5. **Refine**. Prepare FOA for distribution.

The specific needs of each phase inform the tool **content**.

Roles
~~~~~

The team considered that different staff members will interact with this
information differently and prefer different methods of data
communication. These roles were characterized by “personae” defined by
level of involvement in the FOA-writing process.

* Technical analyst
* Technical lead
* FOA lead
* Approver

Decision makers in each of these roles will interact with tool output.
The tool users determine how the tool will be used and how its content
will be displayed, informing **interactions and data visualization**.
For example, a user who will view the tool output in a presentation will
need a static representation of the tool output.

Potential topics
^^^^^^^^^^^^^^^^

Prototyping a tool requires content. The team referenced two previous
FOAs to understand the break-down of topic areas. We then extracted FOA
topic/subtopic areas and metrics from 2016 budget request, combining
hard/soft cost-focused FOAs to examine how to compete the two and avoid
directly analyzing a specific past FOA. Following this process further
informed the team’s understanding of how decision-makers might decide
what to input into the tool.

Topics under consideration might be assessed by the following metrics:

* $/W\ :sub:`DC`
* $/kWh
* Strategic metal content (lifetime)
* Hazardous waste content (lifetime)
* Lifetime
* Reliability
* Emissions
* Labor

The following text details topic areas considered for Tyche tool
development.

1. Crystaline silicon wafer design
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Wafer area
-  Wafer thickness
-  Wafer density
-  Silicon utilization
-  Production yield

2. Tandem thin-films
~~~~~~~~~~~~~~~~~~~~

-  Design parameters
-  Architectures

3. Polysilicon module
~~~~~~~~~~~~~~~~~~~~~

-  (many parameters)

4. Module design
~~~~~~~~~~~~~~~~

-  Module Capital
-  Module Lifetime
-  Module Efficiency
-  Module Aperture
-  Module O&M Fixed
-  Module Degradation
-  Module Soiling Loss

5. Inverter design
~~~~~~~~~~~~~~~~~~

-  Inverter Capital
-  Inverter Lifetime
-  Inverter Replacement
-  Inverter Efficiency

6. Balance-of-system design
~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Hardware Capital
-  Direct Labor
-  Permitting
-  Customer Acquisition
-  Installer Overhead & Profit
