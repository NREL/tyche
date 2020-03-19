#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p "python36.withPackages(ps: with ps; [ numpy pandas ])"



# Import modules and functions.

import concurrent.futures as ft
import numpy              as np
import pandas             as pd
import pvmodel            as pv

from copy            import deepcopy
from math            import exp, log
from multiprocessing import cpu_count


# Read inputs.

defaultInputs, scenarioInputs, regionalInputs = pv.readInputs()

defaults = pv.inputToFrame(defaultInputs, 0)


# Run single sensitivity.

experiment = deepcopy(defaults)
experiment.insert(0, ("Factor", ""), "default", True)

n = 0

for section, column in defaults.columns:
    for m in [exp(x) for x in np.arange(log(0.1), log(10) + log(100) / 20, log(100) / 20)]:
        n += 1
        row = deepcopy(defaults)
        row.insert(0, ("Factor", ""), "default", True)
        row.index = [n]
        value = row.at[n, (section, column)]
        if value == 0:
            break
        row.at[n, (section, column)] = m * value
        row.at[n, ("Factor", "")] = section + " @ " + column
        experiment = experiment.append(row)

results = pv.runModel(experiment, scenarioInputs, regionalInputs, defaultInputs)

experiment.join(results).to_csv("experiment-results.tsv", sep="\t")


# Run double sensitivity.

sensitiveFactors = pd.read_csv("sensitive-factors.tsv", sep="\t")

def make_experiment_row(n, section1, column1, section2, column2, m1, m2):
    row = deepcopy(defaults)
    row.insert(0, ("Factors", ""), "default", True)
    row.index = [n]
    value1 = row.at[n, (section1, column1)]
    row.at[n, (section1, column1)] = m1 * value1
    value2 = row.at[n, (section2, column2)]
    row.at[n, (section2, column2)] = m2 * value2
    row.at[n, ("Factors", "")] = section1 + " @ " + column1 + " & " + section2 + " @ " + column2
    return row

def make_experiment_rows():
    n = 1
    for section1, column1 in defaults.columns:
        if not any((section1 == sensitiveFactors.Section) & (column1 == sensitiveFactors.Column)):
            continue
        for section2, column2 in defaults.columns:
            if section1 >= section2 or section1 == section2 and column1 >= column2:
                continue
            if not any((section2 == sensitiveFactors.Section) & (column2 == sensitiveFactors.Column)):
                continue
            for m1 in [exp(x) for x in np.arange(log(0.1), log(10) + log(100) / 20, log(100) / 20)]:
                for m2 in [exp(x) for x in np.arange(log(0.1), log(10) + log(100) / 20, log(100) / 20)]:
                    value1 = defaults.at[0, (section1, column1)]
                    value2 = defaults.at[0, (section2, column2)]
                    if value1 != 0 and value2 != 0:
                        yield (n, section1, column1, section2, column2, m1, m2)
                        n += 1

def build_and_run(cases):
    experiment = pd.concat([make_experiment_row(n, section1, column1, section2, column2, m1, m2) for n, section1, column1, section2, column2, m1, m2 in cases])
    results = pv.runSome(experiment, scenarioInputs, regionalInputs, defaultInputs)
    results.columns = pd.MultiIndex.from_tuples([("Results", column) for column in results.columns])
    return experiment.join(results)

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

results2 = None
nbatch = cpu_count()
with ft.ProcessPoolExecutor(max_workers=nbatch) as executor:
    results2 = pd.concat(executor.map(build_and_run, map(list, chunks(list(make_experiment_rows()), nbatch))))

results2.to_csv("experiment-results2.tsv", sep="\t")
