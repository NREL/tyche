"""""""""""""""""""""""""""""""
Tyche Quick Start Guide
"""""""""""""""""""""""""""""""

++++++++++++++++++++++++++++++++++
Introduction and Getting Started
++++++++++++++++++++++++++++++++++

The following materials walk through:

1.	what the Technology Characterization and Evaluation (Tyche ) tool does and why this is of value to the user; 
2.	setting up the Tyche package for use, including downloading and installing Anaconda (which includes Jupyter for running Tyche and Spyder for creating/editing Python files); 
3.	modifying an existing model to be used to meet your particular needs; 
4.	developing data, including conducting expert elicitations to estimate potential impacts of different R&D investments; 
5.	an overview of the code and data files used; and
6.	building and running Tyche models of your technologies to evaluate the potential impacts of alternative R&D investment strategies.

++++++++++++++++++++++++++++++++++
The Technology Characterization and Evaluation Tool
++++++++++++++++++++++++++++++++++

The **Tyche** tool provides a consistent and systematic methodology to evaluate alternative R&D investments in a technology system and determine.  This can help support decision-makers as they consider alternative R&D investment strategies to meet their overall goals.

The Tyche methodology: 

1. begins with a technoeconomic model of a particular technology; 
2. conducts expert elicitation to get quantitative estimates of how much a particular attribute of a component or subsystem within that technology might improve with R&D; 
3. represents these estimates as probability distributions—typically triangular distributions as these are straightforward to develop through expert elicitations—within this model; and then 
4. uses multi-objective stochastic optimization to determine the potential overall improvement in the technology, identify the R&D investments that have the greatest potential impact for improving technology attributes such as cost or environmental impact, and enables analysis of R&D options to meet decision-maker goals.

**To begin the quick start guide, it needs to explain what Tyche is, what it does, and why this is of value to the user. Expand this to a full explanation**

=====================
Set up Tyche package
=====================

The following installs Anaconda (from which JupyterLab is used to run Tyche models), downloads Tyche and sets up the Tyche environment within Anaconda to run Tyche models.  There are several platforms for using Tyche.  Listed below is the process for downloading the Tyche framework to your personal computer. The Tyche repository is available on github at this [link](https://github.com/NREL/tyche)...   A library of simple Tyche models is available to provide beginning templates for developing more complete models of technologies of interest at: (https://github.com/NREL/tyche/tree/dev/src/technology)

- Download and install `Anaconda <https://anaconda.org/>`_ . Most users will install the Windows version of Anaconda.  Set up an account with a password to download Anaconda to make re-installing easier if there are problems and to access tutorials and other information on Anaconda.  This can also be useful if your Jupyter link breaks.  <<For installing Anaconda for Linux or Mac systems, see below.>> 
- Download Tyche from GitHub at: https://github.com/NREL/tyche/tree/dev 
- Paste the downloaded Tyche Zip.files on your desktop and extract the files.  It is easiest to access these files using Anaconda/Jupyter when they are on your desktop.
- Navigate to the downloaded Tyche repository folder. 
- Create the Tyche environment 
    * Type the following into the Anaconda Shell (under Anaconda in the Windows Start menu). 
    * For windows machines, do the following:
    * In the Windows Start menu (left-most windows icon at the bottom of your screen) open the Anaconda folder and click on the Anaconda prompt.  A window will open showing: ```(base) C:\users\xxx>```   Navigate to where your Tyche folder is, e.g., change directories to the tyche folder:  ```(base) cd:\users\PersonName\tyche```, then install the tyche environment with:      
    * ``conda env create --file conda\win.yml``
    * ``conda activate tyche``
    * ``pip install mip``
    
- For Mac OS use system terminal. 

    * ``conda env create --file conda\mac.yml``
    * ``conda activate tyche``
    * ``pip install mip``

* These steps create a new environment in Anaconda for running Tyche files.  This can be seen by looking at Anaconda navigator (launch Anaconda navigator by clicking the Windows start button and going to the Anaconda folder and clicking on Anaconda Navigator) under “Environment” on the left-most panel.  It will show two names: “Base (root)” and “Tyche”.  The Tyche work will be done within the Tyche environment; in particular, note that the Windows Start menu showing the Anaconda file now includes a Jupyter Notebook (Tyche) icon to launch Jupyter to run Tyche. 
* Run a Tyche Model.  To test the Tyche environment, click the Windows Start menu, go to the Anaconda folder, and click on the Jupyter Notebook (Tyche) program.  This will launch Jupyter Notebook (Tyche) in your default web browser.   
* Build a Tyche Model.  This consists of **xxxxx**; Examples are provided below.  Models follow a particular format as specified in the Tyche documentation Release 0.xx.  The form of these Tyche models enables consistent approaches to evaluating technologies.
* Develop Model Data.  Much model data will be well known and should be entered directly into the respective .csv files as described below.  Other model data is developed through expert elicitations.
* Conduct Expert Elicitations to estimate potential technology cost and performance improvements for selected levels of R&D investment as well as to determine other needed data.
* Input Expert Elicitation data into the Tyche model.

=======================
Repository Organization
=======================

The directory where users should store new technology models (.py files) and the accompanying datasets (discussed below) is indicated in blue. We recommend that users create sub-directories under technology for each new technology or decision context, to avoid confusing the various input datasets.
**Add figure**

The content of the folders and files follows:

- Conda: This folder has four files: “mac.yml”, “nobuilds.yml”, “tiny.yml”, and “win.yml”.  The win.yml and mac.yml files are used to install Tyche in Windows and Mac machines, respectively, as described below.  The “nobuilds.yml” file is for xxxxx.  The “tiny.yml” file is for xxxx

- Docs: This folder has a number of RST (reStructured Text markup language) files that describe different aspects of Tyche and its programs.  These are accessed through xxxxx.

   * SRC: This has three subfolders, as discussed below:
   * Eutychia: this folder has **xxxxxxx**
   * Technology: This folder has a subfolder for each Technology that is modeled in Tyche and also has a corresponding python (.py) file for that technology model directly under SRC.
Within each Technology folder there is one Jupyter (.ipynb) file that models the technology and seven .csv files to provide data, as follow:

- designs. 
- functions.
- indices.
- investments.
- parameters.
- results.
- tranches.
- Each of these .csv files is described in detail below.

Tyche: This folder has 10 python files which form the core of the Tyche model and should not be modified.  These do the following:

- \_\_init\_\_: This is the Python initialization function.   The leading and trailing double underscores mean that this is a special method of the Python interpreter.
-	DecisionGUI:
-	Designs:
-	Distributions:
-	EpsilonConstraints:
-	Evaluator:
-	Investments:
-	IO:
-	Types:
-	Waterfall:
-	Each of these files is described in detail below

============================
Defining a Technology Model
============================


What is a “technology”?
=======================

In the R&D decision contexts represented and analyzed by Tyche, “technology” has a very broad definition. A technology converts input(s) to output(s) using capital equipment with a defined lifetime and incurs fixed and/or variable costs in doing so. A technology may be a manufacturing process, a biorefinery, an agricultural process, a renewable energy technology component such as a silicon wafer or an inverter, a renewable energy technology unit such as a wind turbine or solar panel, a renewable power plant system such as a concentrated solar power plant, and more. Within the R&D decision context, a technology is also subject to one or more research areas in which R&D investments can be made to change the technology and its economic, environmental, and other metrics of interest. Multiple technologies can be modeled and compared within the same decision context, provided the same metrics are calculable for each technology. Within Tyche, a technology is represented both physically and economically using a classic but simple and generalized techno-economic analysis (TEA). The TEA is based on a user defined technology model and accompanying datasets of technological and investment information.


=======================
Jupyter Notebook
=======================
- Describe Jupyter model and what it does
- Describe Python model and what it does, bringing up to here the discussion from below
- Then describe the supporting data sets below


+++++++++++++++
Input Datasets
+++++++++++++++
