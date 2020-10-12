import os
import sys
sys.path.insert(0, os.path.abspath(".."))

import json    as json
import quart   as qt
import seaborn as sb
import tyche   as ty
import uuid    as uuid

from base64            import b64encode
from io                import BytesIO
from matplotlib.figure import Figure


app = qt.Quart(
  __name__                  ,
  static_url_path = ""      ,
  static_folder   = "static",
)

app.config.from_file("demo.json", json.load)


investments = ty.Investments(app.config["INVESTMENTS"])

designs = ty.Designs(app.config["DESIGNS"])
designs.compile()

tranche_results = investments.evaluate_tranches(designs, sample_count = 25)

evaluator = ty.Evaluator(investments.tranches, tranche_results.summary)


session_amounts = {}
session_evaluation = {}


@app.route("/")
async def explorer():
  ident = uuid.uuid4()
  qt.session["ID"] = ident
  amounts = evaluator.amounts.groupby(
    "Category"
  ).max(
  ).apply(
    lambda x: x[0] / 2, axis = 1
  ).rename(
    "Amount"
  ).to_frame(
  )
  session_amounts[ident] = amounts
  session_evaluation[ident] = evaluator.evaluate(amounts)
  return await qt.render_template(
    "model.html"                     ,
    categories = evaluator.categories,
    metrics    = evaluator.metrics   ,
    units      = evaluator.units     ,
    amounts    = evaluator.max_amount,
  )


@app.route("/plot", methods = ["POST"])
async def plot():
  ident = qt.session["ID"]
  evaluation = session_evaluation[ident]
  form = await qt.request.form
  i = evaluator.metrics[int(form["row"])]
  j = None if form["col"] == "x" else evaluator.categories[int(form["col"])]
  figure = Figure(figsize=(float(form["width"]) / 100, float(form["height"]) / 100))
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


@app.route("/invest", methods = ["POST"])
async def invest():
  ident = qt.session["ID"]
  form = await qt.request.form
  j = int(form["col"])
  v = float(form["value"])
  session_amounts[ident].loc[evaluator.categories[j]] = v
  session_evaluation[ident] = evaluator.evaluate(session_amounts[ident])
  return ""
