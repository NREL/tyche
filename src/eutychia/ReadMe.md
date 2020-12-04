Instruction for Running the Example and the Server
==================================================


Conda Environment
-----------------

Before running the example or the server, create and activate the conda environment:

	conda env create --file ../../conda-environment.yml
	conda activate tyche

Install and update a package version:

    conda activate tyche
    conda install seaborn=0.11.0
    conda env export --name tyche > ../../conda-environment.yml

Update the conda environment:

    conda env update --prefix ./env --file ../../conda-environment.yml  --prune


Running the Server
------------------

Start the server in debug mode

	./debug.sh

or in production mode

	./run.sh

and then visit http://127.0.0.1:5000/.


Running the Example
-------------------

Using Jupyter, first start the notebook server

	jupyter notebook

and visit http://localhost:8888/ to select `example.ipynb`.

Alternatively, just open [example.py](example.py) is the IDE of your choice or run it at the command line.
