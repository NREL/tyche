*Tyche:* *T*echnolog*y* *Ch*aracterization and *E*valuation
===========================================================

See our complete documentation on [GitHub Pages](https://nrel.github.io/tyche-docs/) or in downloadable PDF format [here](https://github.com/NREL/tyche-docs/blob/main/Tyche.pdf).

If you would like to download the Tyche software, please visit our [releases page](https://github.com/NREL/tyche/releases) to access the most recent release.

The directory structure of this repository is as follows:

* conda: Conda environment specification files for use when installing or updating Tyche.
* docs: Documentation source files and related metadata.
* src: Tyche's code base
	* eutychia: Code for the browser-based graphical user interface
	* technology: Datasets, models, and analysis Jupyter notebooks for Tyche case studies. Subdirectories contain the datasets and notebooks for each case study.
		* pv-residential-large
		* pv-residential-simple
		* simple-electrolysis
		* transport-model
		* tutorial-basic
		* tutorial-biorefinery
		* utility-pv
	* tyche: Code for ensemble evaluation and stochastic optimization.
	
The branch structure of this repository is as follows:

* `main` contains the current stable and released version of Tyche and can only be altered via approved pull request
* `dev` contains the latest working version of Tyche and may contain unresolved bugs. Commits directly to `dev` should be avoided except for urgent bug fixes and last minute pre-release commits.
* All other branches are feature branches under active development and should not be used for applications.


