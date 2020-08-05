import os
import sys
sys.path.insert(0, os.path.abspath("../src"))

import numpy             as np
import matplotlib.pyplot as pl
import pandas            as pd
import re                as re
import scipy.stats       as st
import seaborn           as sb
import tkinter           as tk
import tyche             as ty

from copy                              import deepcopy
from matplotlib.backend_bases          import key_press_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure                 import Figure
from scipy.interpolate                 import interp1d


class Evaluator:
  def __init__(self, tranches, summary):
    self.amounts    = tranches.groupby(["Category", "Tranche"]).sum() / 1000
    self.categories = summary.reset_index()["Category"].unique()
    self.metrics    = summary.reset_index()["Index"   ].unique()
    self.units      = summary[["Units"]].groupby("Index").max()
    self.interpolators = summary.join(
      self.amounts
    ).groupby(
      ["Category", "Index", "Sample"]
    ).apply(
      lambda df: interp1d(
        np.append(df.Amount, 0),
        np.append(df.Value , 0),
        kind = "linear"        ,
        fill_value = "extrapolate",
        assume_sorted = False  ,
      )
    ).rename(
      "Interpolator"
    )
    self.max_amount = self.amounts.groupby("Category").max()
    self.min_metric = summary.groupby(["Category", "Index"]).min(numeric_only = True).groupby("Index").sum()
    self.max_metric = summary.groupby(["Category", "Index"]).max(numeric_only = True).groupby("Index").sum()
  def evaluate(self, amounts):
    return amounts.join(
      self.interpolators
    ).apply(
      lambda row: row["Interpolator"](row["Amount"]), axis = 1
    ).rename(
      "Value"
    )

class Window:
  def __init__(self, evaluator):
    self.root = tk.Tk()
    self.root.winfo_toplevel().title("R&D Portfolio Evaluation")
    self.evaluator = evaluator
    self.amounts = self.evaluator.amounts.groupby(
      "Category"
    ).max(
    ).apply(
      lambda x: tk.DoubleVar(self.root, value = x[0] / 2), axis = 1
    ).rename(
      "Amount"
    )
    tk.Label(text = "R&D Category"   ).grid(row = 1, column = 0, columnspan = 3)
    tk.Label(text = "Portfolio Total").grid(row = 1, column = 5, rowspan    = 2)
    self.sliders = {}
    self.fixeds = {}
    for j in range(len(self.evaluator.categories)):
      tk.Label(
        self.root                               ,
        text      = self.evaluator.categories[j],
      ).grid(
        row    = 2,
        column = j,
      )
      tk.Scale(
        self.root                                                                ,
        variable   = self.amounts[self.evaluator.categories[j]]                   ,
        label      = "Investment [k$]"                                            ,
        from_      = 0                                                            ,
        to         = self.evaluator.max_amount.xs(self.evaluator.categories[j])[0],
        resolution = 50                                                           ,
        orient     = tk.HORIZONTAL                                                ,
      ).grid(
        row    = 6          ,
        column = j          ,
        sticky = tk.W + tk.E,
      )
      self.fixeds[self.evaluator.categories[j]] = tk.BooleanVar(self.root)
      tk.Checkbutton(
        self.root                                            ,
        variable  = self.fixeds[self.evaluator.categories[j]],
        text      = "Fixed?"                                 ,
      ).grid(
        row    = 7,
        column = j,
      )
    self.sliders["Aggregate"] = tk.DoubleVar(self.root)
    tk.Scale(
      self.root                           ,
      variable = self.sliders["Aggregate"],
      label    = "Investment [k$]"        ,
      from_    = 0                        ,
      to       = self.evaluator.max_amount.sum()[0] ,
      orient = tk.HORIZONTAL              ,
    ).grid(row = 6, column = 5, sticky = tk.W + tk.E)
    for i in range(len(self.evaluator.metrics)):
      tk.Label(self.root, text = self.evaluator.metrics[i] + "\n[" + self.evaluator.units.iloc[i].values[0] + "]").grid(row = 3 + i, column = 3)
    self.priority = tk.StringVar(self.root)
    self.priority.set(self.evaluator.metrics[0])
    tk.Label(self.root, text = "Priority Metric:").grid(row = 7, column = 3, sticky = tk.E)
    tk.OptionMenu(self.root, self.priority, *self.evaluator.metrics).grid(row = 7, column = 5, sticky = tk.W + tk.E)
    self.percentile = tk.DoubleVar(self.root)
    self.percentile.set(50)
    tk.Label(self.root, text = "Minimum Percentile:").grid(row = 8, column = 3, sticky = tk.E + tk.S)
    tk.Scale(self.root, variable = self.percentile, from_ = 0, to = 100, orient = tk.HORIZONTAL).grid(row = 8, column = 5, sticky = tk.W + tk.E + tk.N)
    self.job = None
    self.reevaluate_immediate()
    self.canvases = {}
    for i in range(len(self.evaluator.metrics)):
      for j in range(len(self.evaluator.categories)):
        init_figure = self.create_figure(
          self.evaluator.metrics[i]   ,
          self.evaluator.categories[j],
        )
        canvas = self.canvases[(i, j)] = FigureCanvasTkAgg(init_figure, master = self.root)
        canvas.get_tk_widget().grid(row = 3 + i, column = j)
        canvas.draw()
      init_figure = self.create_figure(
        self.evaluator.metrics[i],
        "Aggregate"              ,
      )
      canvas = self.canvases[(i, "Aggregate")] = FigureCanvasTkAgg(init_figure, master = self.root)
      canvas.get_tk_widget().grid(row = 3 + i, column = 5)
      canvas.draw()
    self.root.grid_columnconfigure(5, minsize = 50)
    self.amounts.apply(lambda v: v.trace_add("write", lambda arg0, arg1, arg2: self.refresh()))
  def reevaluate(self, next = lambda: None, delay = 200):
    if self.job:
      self.root.after_cancel(self.job)
    self.job = self.root.after(delay, lambda: self.reevaluate_immediate(next = next))
  def reevaluate_immediate(self, next = lambda: None):
    self.job = None
    amounts = self.amounts.apply(lambda v: float(v.get())).to_frame()
    self.evaluation = self.evaluator.evaluate(amounts)
    next()
  def refresh(self):
    self.reevaluate(next = lambda: self.refresh_immediate())
  def refresh_immediate(self):
    for i in range(len(self.evaluator.metrics)):
      for j in range(len(self.evaluator.categories)):
        canvas = self.canvases[(i, j)]
        canvas.figure = self.create_figure(
          self.evaluator.metrics[i]   ,
          self.evaluator.categories[j],
        )
      canvas = self.canvases[(i, "Aggregate")]
      canvas.figure = self.create_figure(
        self.evaluator.metrics[i],
        "Aggregate"              ,
      )
    for i in range(len(self.evaluator.metrics)):
      for j in range(len(self.evaluator.categories)):
        self.canvases[(i, j)].draw()
      self.canvases[(i, "Aggregate")].draw()
  def create_figure(self, i, j) -> Figure:
      figure = Figure(figsize=(2, 2))
      ax = figure.subplots()
      summary = self.evaluation.xs(i, level = "Index")
      if j == "Aggregate":
        values = summary.groupby("Sample").sum()
      else:
        values = summary.xs(j, level = "Category")
      sb.boxplot(y = values, ax = ax)
      y0 = min(0, self.evaluator.min_metric.loc[i][0])
      y1 = max(0, self.evaluator.max_metric.loc[i][0])
      dy = (y1 - y0) / 20
      ax.set(
        xlabel = ""              ,
        ylabel = ""              ,
        ylim = (y0 - dy, y1 + dy),
      )
      figure.set_tight_layout(True)
      return figure
  def mainloop(self):
    tk.mainloop()


designs     = ty.Designs("../data/residential_pv_multiobjective")
investments = ty.Investments("../data/residential_pv_multiobjective")

designs.compile()

tranche_results = investments.evaluate_tranches(designs, sample_count = 500)


e = Evaluator(investments.tranches, tranche_results.summary)

w = Window(e)

w.mainloop()
