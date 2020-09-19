"""
Interactive exploration of a technology.
"""

import seaborn as sb
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure                 import Figure


class DecisionWindow:
  """
  Class for displaying an interactive interface to explore cost-benefit tradeoffs for a technology.
  """

  def __init__(self, evaluator):
    """
      Parameters
      ----------
      evaluator : tyche.Evaluator
        The evaluation object for the technology.
    """

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
    n_categories = len(self.evaluator.categories)
    n_metrics    = len(self.evaluator.metrics   )
    tk.Label(text = "R&D Category"   ).grid(row = 1, column = 0, columnspan = 3)
    tk.Label(text = "Portfolio Total").grid(row = 1, column = 5, rowspan    = 2)
    self.sliders = {}
    self.fixeds = {}
    for j in range(n_categories):
      tk.Label(
        self.root                               ,
        text      = self.evaluator.categories[j],
      ).grid(
        row    = 2,
        column = j,
      )
      tk.Scale(
        self.root                                                                 ,
        variable   = self.amounts[self.evaluator.categories[j]]                   ,
        label      = "Investment [$]"                                             ,
        from_      = 0                                                            ,
        to         = self.evaluator.max_amount.xs(self.evaluator.categories[j])[0],
        resolution = 50                                                           ,
        orient     = tk.HORIZONTAL                                                ,
      ).grid(
        row    = n_metrics + 3,
        column = j            ,
        sticky = tk.W + tk.E  ,
      )
#     self.fixeds[self.evaluator.categories[j]] = tk.BooleanVar(self.root)
#     tk.Checkbutton(
#       self.root                                            ,
#       variable  = self.fixeds[self.evaluator.categories[j]],
#       text      = "Fixed?"                                 ,
#     ).grid(
#       row    = n_metrics + 4,
#       column = j            ,
#     )
    self.sliders["Aggregate"] = tk.DoubleVar(self.root)
    aggregate = tk.Scale(
      self.root                                    ,
      variable = self.sliders["Aggregate"]         ,
      label    = "Investment [$]"                  ,
      from_    = 0                                 ,
      to       = self.evaluator.max_amount.sum()[0],
      orient = tk.HORIZONTAL                       ,
    )
    aggregate.grid(
      row    = n_metrics + 3   ,
      column = n_categories + 2,
      sticky = tk.W + tk.E     ,
    )
    aggregate.configure(state='disabled')
    for i in range(n_metrics):
      tk.Label(
        self.root                                                                                   ,
        text      = self.evaluator.metrics[i] + "\n[" + self.evaluator.units.iloc[i].values[0] + "]",
      ).grid(
        row    = 3 + i       ,
        column = n_categories,
      )
#   self.priority = tk.StringVar(self.root)
#   self.priority.set(self.evaluator.metrics[0])
#   tk.Label(self.root, text = "Priority Metric:").grid(row = 7, column = 3, sticky = tk.E)
#   tk.OptionMenu(
#     self.root              ,
#     self.priority          ,
#     *self.evaluator.metrics,
#   ).grid(
#     row    = n_metrics + 4   ,
#     column = n_categories + 2,
#     sticky = tk.W + tk.E     ,
#   )
#   self.percentile = tk.DoubleVar(self.root)
#   self.percentile.set(50)
#   tk.Label(
#     self.root                        ,
#     text      = "Minimum Percentile:",
#   ).grid(
#     row    = n_metrics + 5,
#     column = n_categories ,
#     sticky = tk.E + tk.S  ,
#   )
#   tk.Scale(
#     self.root                  ,
#     variable  = self.percentile,
#     from_     = 0              ,
#     to        = 100            ,
#     orient    = tk.HORIZONTAL  ,
#   ).grid(
#     row    = n_metrics + 5     ,
#     column = n_categories + 2  ,
#     sticky = tk.W + tk.E + tk.N,
#   )
    self.job = None
    self.reevaluate_immediate()
    self.canvases = {}
    for i in range(n_metrics):
      for j in range(n_categories):
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
      canvas.get_tk_widget().grid(row = 3 + i, column = n_categories + 2)
      canvas.draw()
    self.root.grid_columnconfigure(5, minsize = 50)
    self.amounts.apply(lambda v: v.trace_add("write", lambda arg0, arg1, arg2: self.refresh()))

  def reevaluate(self, next = lambda: None, delay = 200):
    """
    Recalculate the results after a delay.

    Parameters
    ----------
    next : function
      The operation to perform after completing the recalculation.
    delay : int
      The number of milliseconds to delay before the recalculation.
    """
    
    if self.job:
      self.root.after_cancel(self.job)
    self.job = self.root.after(delay, lambda: self.reevaluate_immediate(next = next))

  def reevaluate_immediate(self, next = lambda: None):
    """
    Recalculate the results immediately.

    Parameters
    ----------
    next : function
      The operation to perform after completing the recalculation.
    """

    self.job = None
    amounts = self.amounts.apply(lambda v: float(v.get())).to_frame()
    self.sliders["Aggregate"].set(amounts.values.sum())
    self.evaluation = self.evaluator.evaluate(amounts)
    next()

  def refresh(self):
    """
    Refresh the graphics after a delay.
    """

    self.reevaluate(next = lambda: self.refresh_immediate())

  def refresh_immediate(self):
    """
    Refresh the graphics immediately.
    """

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
    """
    Run the interactive interface.
    """

    tk.mainloop()
