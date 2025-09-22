import marimo

__generated_with = "0.15.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    import sys

    import numpy as np
    import matplotlib.pyplot as pl
    import pandas as pd
    import seaborn as sb
    import marimo as mo

    sys.path.insert(0, os.path.abspath("src"))

    import tyche as ty
    return


if __name__ == "__main__":
    app.run()
