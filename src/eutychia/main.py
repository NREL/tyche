"""
Web server user interface for Tyche.
"""


# Import modules and functions.

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

import json as json
import numpy as np
import pandas as pd
import seaborn as sb
import tyche as ty
import uuid as uuid

from base64 import b64encode
from datetime import datetime
from io import BytesIO
from matplotlib.figure import Figure



if 'QUART_APP' in os.environ or __name__ == '__main__':

  import quart as qt

  # Create and configure application.
  technology_model = "pv-residential-simple"
  technology_path = os.path.join("ioc", technology_model + ".json")

  app = qt.Quart(__name__, static_url_path="", static_folder="static",)

  app.config.from_file(technology_path, json.load)

  print(technology_path)
  print(type(app.config))

  senseToMetric = {'min':'upper', 'max':'lower'}

  # Compute investments.

  investments = ty.Investments(app.config["INVESTMENTS"])

  designs = ty.Designs(app.config["DESIGNS"])
  designs.compile()

  tranche_results = investments.evaluate_tranches(designs, sample_count=100)

  evaluator = ty.Evaluator(tranche_results)
  
  optimizer = ty.EpsilonConstraintOptimizer(evaluator)
  optimizer.optimum_metrics(
      verbose = 0,
      sense = {
          'GHG': 'min',
          'LCOE': 'min',
          'Labor': 'max',
      }
  )

  metric_range = evaluator.min_metric.join(
      evaluator.max_metric,
      lsuffix=" Min",
      rsuffix=" Max",
  )
  print("> metric_range:\n", metric_range)


# Session-level storage.

  session_amounts = {}
  session_evaluation = {}


# Main page.


  @app.route("/")
  async def explorer():
      ident = uuid.uuid4()
      qt.session["ID"] = ident
      amounts = (
          evaluator.amounts.groupby("Category")
          .max()
          .apply(lambda x: x[0] / 2, axis=1)
          .rename("Amount")
          .to_frame()
      )
      session_amounts[ident] = amounts
      session_evaluation[ident] = evaluator.evaluate(amounts)

      technology_models=["pv-residential-simple", "simple-electrolysis"]

      plot_layout = "grid.html"

    #   plot_layout = "model.html"
    #   plot_types = ["box plot", "distribution", "violin"]

      if plot_layout == "grid.html":
          plot_types = ["box plot", "distribution", "violin"]
      elif plot_layout == "column.html":
          plot_types = ["box plot", "distribution", "violin"]
      elif plot_layout == "heatmap.html":
          plot_types = ["heatmap", "annotated"]

      print(evaluator.units["Units"])

      return await qt.render_template(
          plot_layout,
          categories=evaluator.max_amount["Amount"],
          metrics=metric_range,
          units=evaluator.units["Units"],
          plot_types=plot_types,
          technology_model=technology_model.replace('-',' '),
          technology_models=technology_models,
      )



  def setup_template(plot_layout):
      technology_models=["pv-residential-simple", "simple-electrolysis"]

      if plot_layout == "grid":
          plot_types = ["box plot", "distribution", "violin"]
      elif plot_layout == "column":
          plot_types = ["box plot", "distribution", "violin"]
      elif plot_layout == "heatmap":
          plot_types = ["heatmap", "annotated"]

      return qt.render_template(
          plot_layout + ".html",
          categories=evaluator.max_amount["Amount"],
          metrics=metric_range,
          units=evaluator.units["Units"],
          plot_types=plot_types,
          technology_model=technology_model.replace('-',' '),
          technology_models=technology_models,
      )


  @app.route("/layout/<name>")
  async def layout(name):
      plot_layout = name

      technology_models=["pv-residential-simple", "simple-electrolysis"]

      if plot_layout == "grid":
          plot_types = ["box plot", "distribution", "violin"]
      elif plot_layout == "column":
          plot_types = ["box plot", "distribution", "violin"]
      elif plot_layout == "heatmap":
          plot_types = ["heatmap", "annotated"]

      return await qt.render_template(
          plot_layout + ".html",
          categories=evaluator.max_amount["Amount"],
          metrics=metric_range,
          units=evaluator.units["Units"],
          plot_types=plot_types,
          technology_model=technology_model.replace('-',' '),
          technology_models=technology_models,
      )


# Generate plots.

@app.route("/plot", methods=["POST"])
async def plot():
    show_mean = True

    ident = qt.session["ID"]
    evaluation = session_evaluation[ident]
    form = await qt.request.form

    typ = str(form["plottype"])

    # m = evaluator.metrics[int(form["met"])]
    # c = None if form["cat"] in ["x","all"] else evaluator.categories[int(form["cat"])]
    m = evaluator.metrics[int(form["met"])]    if form["met"].isdigit() else str(form["met"])
    c = evaluator.categories[int(form["cat"])] if form["cat"].isdigit() else str(form["cat"])
    
    # print(form["height"])
    # figure = Figure(figsize=(float(form["width"]) / 100, float(form["height"]) / 100), constrained_layout=True)
    figure = Figure(figsize=(float(form["width"]) / 100, float(form["height"]) / 100))
    ax = figure.subplots()
    
    summary = evaluation.xs(m, level="Index").astype('float64')

    if c in ["x","xall"]: values = summary.groupby("Sample").sum().reset_index()
    elif c == "all":      values = summary.reset_index()
    else:                 values = summary.xs(c, level="Category").reset_index()
    
    y0 = min(0, metric_range.loc[m, "Value Min"])
    y1 = max(0, metric_range.loc[m, "Value Max"])
    dy = (y1 - y0) / 10

    # ----- GRID ---------------------------------------------------------------------------
    if typ in ["box plot", "distribution", "violin"]:
        if typ == "box plot":
            if c == "all":  sb.boxplot(ax=ax, data=values, x='Value', y='Category')
            else:           sb.boxplot(ax=ax, data=values, x='Value', linewidth=0.5)
        elif typ == "violin":
            if c == "all":  sb.violinplot(ax=ax, data=values, x='Value', y='Category')
            else:           sb.violinplot(ax=ax, data=values, x='Value')
        elif typ == "distribution":
            if c == "all":  sb.kdeplot(ax=ax, data=values, x='Value', hue='Category', multiple='stack')
            else:           sb.kdeplot(ax=ax, data=values, x='Value')

        sb.set_style({"xtick.direction": "in","ytick.direction": "in"})

        ax.set(
            xlabel="", ylabel="",
            yticks=[],
            yticklabels=[],
            xticks=[],
            xticklabels=[],
            xlim=(y0-dy, y1+dy),
        )

    # ----- HEATMAP ------------------------------------------------------------------------
    isgrid=True

    if typ in ["heatmap", "annotated"]:
        summary_norm = normalize_to_metric(evaluation)
        value_norm = summary_norm.unstack(level='Index') if isgrid else pd.DataFrame(
            aggregate_over(summary_norm, ['Category'], np.sum)).transpose()

        if typ == "heatmap":
            sb.heatmap(
                value_norm, linewidths=0.5, vmax=1.0, vmin=-1.0, cmap="coolwarm_r", ax=ax, cbar=False,
            )
            
        elif typ == "annotated":
            summary = aggregate_over(evaluation, ['Sample'])
            value = summary.unstack(level='Index') if isgrid else pd.DataFrame(
                aggregate_over(summary, ['Category'], np.sum)).transpose()

            sb.heatmap(
                value_norm, linewidths=0.5, vmax=1.0, vmin=-1.0, cmap="coolwarm_r", ax=ax, cbar=False,
                annot=value,
                fmt=".4g",
            )
        
        # ax.set(
        #     xlabel="", ylabel="",
        #     # xticks=[], yticks=[],
        #     # xticklabels=[], yticklabels=[],
        # )

    figure.set_tight_layout(True)

    # Save locally -- for prototyping.
    #   localpath = os.path.join("assets","plots",localdir,(str(m) + "_" + str(c).split()[0] + ".png").lower())
    #   figure.savefig(localpath)
    # Save for server.
    img = BytesIO()
    # figure.savefig(img, format="png", bbox_inches='tight', pad_inches = 0)
    figure.savefig(img, format="png")
    img.seek(0)
    x = b64encode(img.getvalue())
    return "data:image/png;base64,{}".format(x.decode("utf-8"))


# Compute metrics.

@app.route("/metric", methods=["POST"])
async def metric():
    ident = qt.session["ID"]
    evaluation = session_evaluation[ident]
    form = await qt.request.form
    m = evaluator.metrics[int(form["met"])]
    return str(
        np.mean(evaluation.xs(m, level="Index").groupby("Sample").aggregate(np.sum))
    )


# Update investment and recompute.


@app.route("/invest", methods=["POST"])
async def invest():
    ident = qt.session["ID"]
    form = await qt.request.form
    c = int(form["cat"])
    v = float(form["value"])
    session_amounts[ident].loc[evaluator.categories[c]] = v
    session_evaluation[ident] = evaluator.evaluate(session_amounts[ident])
    return ""


# Optimize investments.


@app.route("/optimize", methods=["POST"])
async def optimize():
    ident = qt.session["ID"]
    evaluation = session_evaluation[ident]
    form = await qt.request.form

    target_m = int(form["target"])
    target_metric = evaluator.metrics[target_m]
    constraints = json.loads(form["constraints"])
    print("> constraints\n", constraints)
    
    # print("> target\n", form["target"])

    eps_metric = {
        evaluator.metrics[m]: {
            'limit': constraints["metric"]["metlimwid_" + str(m)],
            # 'sense': 'upper'
            'sense': senseToMetric[constraints["sense"]["metsense_" + str(m)]],
        } for m in range(len(evaluator.metrics)) if m!=target_m
    }
    print("> eps_metric\n", eps_metric)

    # min_metric = pd.Series(
    #     [
    #         constraints["metric"]["metlimwid_" + str(m)]
    #         for m in range(len(evaluator.metrics))
    #     ],
    #     index=evaluator.metrics,
    # )
    # print("> min_metric\n", min_metric, "\n\n\n")

    max_amount = pd.Series(
        [
            constraints["invest"]["invlimwid_" + str(m)]
            for m in range(len(evaluator.categories))
        ],
        index=evaluator.categories,
    )

    total_amount = constraints["invest"]["invlimwid_x"]
    print("\nOptimization started.", datetime.now())
    print("> target_metric\n ", target_metric)
    print("> eps_metric\n ", eps_metric)
    print("> total_amount\n ", total_amount)
    optimum = optimizer.opt_slsqp(
        target_metric,
        sense = constraints['sense']['metsense_' + str(target_m)],
        # metric=target_metric,
        eps_metric=eps_metric,
        max_amount=max_amount,
        total_amount=total_amount
        # , tol          = 1e-4
        # , maxiter      = 10
    )
    print("> exit_message\n ", optimum.exit_message)
    print("> amounts\n ", optimum.amounts)
    print("> metrics\n ", optimum.metrics)
    print("Optimization finished.", datetime.now(), "\n")
    amounts = pd.DataFrame(optimum.amounts)
    session_amounts[ident] = amounts
    session_evaluation[ident] = evaluator.evaluate(amounts)
    result = {}
    result["message"] = optimum.exit_message
    result["amount"] = {
        "invoptwid_" + str(m): optimum.amounts[m] for m in range(len(optimum.amounts))
    }
    return json.dumps(result)


# ------------------------------------------------------------------------------------------
def aggregate_over(ser, idx, statistic=np.mean):
    ser = ser.astype("float64")
    idx_res = list(set(ser.index.names.copy()) - set(idx))
    return ser.groupby(idx_res).aggregate(statistic)


def normalize_to_metric(x):
    x_mean = aggregate_over(x, ['Sample'])
    met_diff = (metric_range['Value Max'] - metric_range['Value Min'])
    return x_mean / met_diff
