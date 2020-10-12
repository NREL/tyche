import os
import sys
sys.path.insert(0, os.path.abspath(".."))

import quart   as qt
import numpy   as np
import pandas  as pd
import seaborn as sb
import tyche   as ty

from base64            import b64encode
from io                import BytesIO
from matplotlib.figure import Figure


investments = ty.Investments("../../data/residential_pv_multiobjective")

designs = ty.Designs("../../data/residential_pv_multiobjective")
designs.compile()

tranche_results = investments.evaluate_tranches(designs, sample_count = 25)

evaluator = ty.Evaluator(investments.tranches, tranche_results.summary)


self_amounts = evaluator.amounts.groupby(
  "Category"
).max(
).apply(
  lambda x: x[0] / 2, axis = 1
).rename(
  "Amount"
)
amounts = self_amounts.to_frame()
evaluation = evaluator.evaluate(amounts)


app = qt.Quart(
  __name__                  ,
  static_url_path = ""      ,
  static_folder   = "static",
)


@app.route("/")
async def explorer():
  return await qt.render_template(
    "model.html"                     ,
    categories = evaluator.categories,
    metrics    = evaluator.metrics   ,
    units      = evaluator.units     ,
    amounts    = evaluator.max_amount,
  )


@app.route("/plot", methods = ["POST"])
async def plot():
  form = await qt.request.form
  i = evaluator.metrics[int(form["row"])]
  j = None if form["col"] == "x" else evaluator.categories[int(form["col"])]
  figure = Figure(figsize=(int(form["width"]) / 100, int(form["height"]) / 100))
  ax = figure.subplots()
  summary = evaluation.xs(i, level = "Index")
  if j is None:
    values = summary.groupby("Sample").sum()
  else:
    values = summary.xs(j, level = "Category")
  sb.boxplot(y = values, ax = ax)
  y0 = min(0, evaluator.min_metric.loc[i][0])
  y1 = max(0, evaluator.max_metric.loc[i][0])
  dy = (y1 - y0) / 20
  ax.set(
    xlabel = ""              ,
    ylabel = ""              ,
    ylim = (y0 - dy, y1 + dy),
  )
  figure.set_tight_layout(True)
  img = BytesIO()
  figure.savefig(img, format="png")
  img.seek(0)
  x = b64encode(img.getvalue())
  return "data:image/png;base64,{}".format(x.decode("utf-8"))
