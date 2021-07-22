Getting Started
===============

Instruction for Running the Example and the Server


Conda Environment
-----------------

Before running the example or the server, create and activate the conda
environment:

::

   conda env create --file conda\win.yml
   conda activate tyche

on Windows, or on Mac

::

   conda env create --file conda/mac.yml
   conda activate tyche

If you receive an HTTPS error, consider retrying the command with the `--insecure` flag added.
Note that the conda environment was created with the command:

::

   conda create -n tyche -c conda-forge python=3.7 numpy scipy scikit-learn seaborn=0.10 matplotlib=3.3 quart hypercorn jupyter


Running the Server
------------------

Visit the folder ``src/eutychia/`` and start the server in debug mode

::

   cd src\eutychia
   debug.cmd

on Windows, or on Mac

::

   cd src/eutychia
   ./debug.sh

or in production mode

::

   cd src\eutychia
   run.cmd

on Windows, or on Mac

::

   cd src/eutychia
   ./run.sh

and then visit http://127.0.0.1:5000/.


Running the Example
-------------------

Using Jupyter, first start the notebook server

::

   jupyter notebook

and visit http://localhost:8888/ to select ``example.ipynb`` in the folder ``src/eutychia``.

Alternatively, just open `example.py <example.py>`__ in the IDE of your
choice or run it at the command line.
