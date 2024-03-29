"""
Designs for technologies.
"""

import os
import sys
import importlib as il
import numpy     as np
import pandas    as pd

from .DataManager   import DesignsDataset, FunctionsDataset, IndicesDataset, ParametersDataset, ResultsDataset
from .Distributions import parse_distribution
from .IO            import check_tables
from .Types         import Functions, Indices, Inputs, Results


def sampler(x, sample_count):
  """
  Sample from an array.

  Parameters
  ----------
  x : array
    The array.
  sample_count : int
    The sample size.
  """

  if sample_count == 1:
    it = np.nditer(
      [x, np.empty(x.shape + (1,), dtype=np.float64)],
      flags=["refs_ok"],
      op_flags=[["readonly"], ["writeonly", "allocate"]],
      op_axes=[list(range(x.ndim)) + [-1], None],
      itershape=x.shape+(1,)
    )
    for x, y in it:
     y[()] = x[()].rvs()
    return it.operands[1]
  else:
    it = np.nditer(
      [x, np.empty(x.shape + (sample_count,), dtype=np.float64)],
      flags=["refs_ok", "external_loop"],
      op_flags=[["readonly"], ["writeonly", "allocate"]],
      op_axes=[list(range(x.ndim)) + [-1], None],
      itershape=x.shape+(sample_count,)
    )
    for x, y in it:
      y[...] = x[0].rvs(sample_count)
    return it.operands[1]


class Designs:
  """
  Designs for a technology.

  Attributes
  ----------
  indices : DataFrame
    The *indices* table.
  functions : DataFrame
    The *functions* table.
  designs : DataFrame
    The *designs* table.
  parameters : DataFrame
    The *parameters* table.
  results : DataFrame
    The *results* table.
  """

  def __init__(
    self                         ,
    path       = None            ,
    name       = 'technology.xlsx',
    uncertain  = True           ,
  ):
    """
    Parameters
    ----------
    path : str
      Location of the data files.
    name : str
        Filename where decision context datasets are kept in separate sheets.
    uncertain : Boolean
      Flag indicating whether probability distributions are present in the *designs* or *parameters* tables.
    indices : str
      Sheet name for the *indices* table.
    functions : str
      Sheet name for the *functions* table.
    designs : str
      Sheet name for the *designs* table.
    parameters : str
      Sheet name for the *parameters* table.
    results : str
      Sheet name for the *results* table.
    """
    self.uncertain = uncertain

    if not os.path.isfile(os.path.join(path, name)):
      raise Exception(f"Designs: {os.path.join(path, name)} does not exist.")
    
    if not check_tables(path, name):
      raise Exception(f'Designs: {name} failed validation.')

    self.indices    = IndicesDataset(    os.path.join(path, name)).sort_index()
    self.functions  = FunctionsDataset(  os.path.join(path, name)).sort_index()
    self.designs    = DesignsDataset(    os.path.join(path, name)).sort_index()
    self.parameters = ParametersDataset( os.path.join(path, name)).sort_index()
    self.results    = ResultsDataset(    os.path.join(path, name)).sort_index()

      
  def vectorize_technologies(self):
    """
    Make an array of technologies.
    """

    return self.designs.reset_index(
      ["Scenario", "Variable", "Index"]
    ).sort_index(
    ).index.drop_duplicates(
    ).values
  
  def vectorize_scenarios(self, technology):
    """
    Make an array of scenarios.
    """
    return self.designs.xs(technology
    ).reset_index(
      ["Variable", "Index"]
    ).sort_index(
    ).index.drop_duplicates(
    ).values
  
  def _vectorize_indices(self, technology):
    def extract_indices(index):
      return self.indices.xs(
          (technology, index)
      ).sort_values(
          by="Offset"
      )[["Offset"]]
    return Indices(
      capital = extract_indices("Capital"),
      input   = extract_indices("Input"  ),
      output  = extract_indices("Output" ),
      metric  = extract_indices("Metric" ),
    )
  
  def vectorize_indices(self, technology):
    """
    Make an array of indices.
    """

    vectors = self._vectorize_indices(technology)
    return Indices(
      capital = vectors.capital.index.values,
      input   = vectors.input.index.values  ,
      output  = vectors.output.index.values ,
      metric  = vectors.metric.index.values ,
    )
  
  def vectorize_designs(self, technology, scenario_count, sample_count=1):
    """
    Make an array of designs.
    """

    def extract_designs(variable):
      return self.compiled_designs.xs(
        (technology, variable),
        level=["Technology", "Variable"]
      )[["Distribution"]]
    lifetimes           = extract_designs("Lifetime"         )
    scales              = extract_designs("Scale"            )
    inputs              = extract_designs("Input"            )
    input_efficiencies  = extract_designs("Input efficiency" )
    input_prices        = extract_designs("Input price"      )
    output_efficiencies = extract_designs("Output efficiency")
    output_prices       = extract_designs("Output price"     )
  
    all_indices = self._vectorize_indices(technology)
  
    def join(values, offsets):
      return values.join(
        offsets
      ).reorder_levels(
        [1, 0]
      ).reset_index(
      ).sort_values(
        by=["Offset", "Scenario"]
      )[
        "Distribution"
      ].values.reshape(
        (offsets.shape[0], scenario_count)
      )

    # If the technology model has probability distributions, sample them
    if self.uncertain:
      return Inputs(
        scale             = sampler(scales["Distribution"].values                 , sample_count),
        lifetime          = sampler(join(lifetimes          , all_indices.capital), sample_count),
        input             = sampler(join(inputs             , all_indices.input  ), sample_count),
        input_efficiency  = sampler(join(input_efficiencies , all_indices.input  ), sample_count),
        input_price       = sampler(join(input_prices       , all_indices.input  ), sample_count),
        output_efficiency = sampler(join(output_efficiencies, all_indices.output ), sample_count),
        output_price      = sampler(join(output_prices      , all_indices.output ), sample_count),
      )
    else:
      # Otherwise, just sample once to get floats and then duplicate the data for later merging
      # with the tranche samples
      return Inputs(
        scale             = np.tile(sampler(scales["Distribution"].values                 , 1), sample_count),
        lifetime          = np.tile(sampler(join(lifetimes          , all_indices.capital), 1), sample_count),
        input             = np.tile(sampler(join(inputs             , all_indices.input  ), 1), sample_count),
        input_efficiency  = np.tile(sampler(join(input_efficiencies , all_indices.input  ), 1), sample_count),
        input_price       = np.tile(sampler(join(input_prices       , all_indices.input  ), 1), sample_count),
        output_efficiency = np.tile(sampler(join(output_efficiencies, all_indices.output ), 1), sample_count),
        output_price      = np.tile(sampler(join(output_prices      , all_indices.output ), 1), sample_count),
      )

  
  def vectorize_parameters(self, technology, scenario_count, sample_count=1):
    """
    Make an array of parameters.
    """

    x = self.compiled_parameters.xs(
      technology
    ).reset_index(
    ).sort_values(
      by=["Offset", "Scenario"]
    )["Distribution"].values
    return sampler(
      x.reshape((-1, scenario_count)),
      sample_count
    )
  
  def compile(self):
    """
    Compile the production and metrics functions.
    """

    self.compiled_functions = {}
    for technology, metadata in self.functions.iterrows():
      m = il.import_module("." + metadata["Model"], package="technology")
      self.compiled_functions[technology] = Functions(
        style      =             metadata["Style"     ] ,
        capital    = eval("m." + metadata["Capital"   ]),
        fixed      = eval("m." + metadata["Fixed"     ]),
        production = eval("m." + metadata["Production"]),
        metric     = eval("m." + metadata["Metrics"   ]),
      )

    self.compiled_designs = self.designs.copy()
    self.compiled_designs["Distribution"] = self.compiled_designs["Value"].apply(parse_distribution)

    self.compiled_parameters = self.parameters.copy()
    self.compiled_parameters["Distribution"] = self.compiled_parameters["Value"].apply(parse_distribution)
          
  def evaluate(self, technology, sample_count=1):
    """
    Evaluate the performance of a technology.

    Parameters
    ----------
    technology : str
      The name of the technology.
    sample_count : int
      The number of random samples.
    """
    print(f"Evaluating {technology}")
    f_capital    = self.compiled_functions[technology].capital
    f_fixed      = self.compiled_functions[technology].fixed        
    f_production = self.compiled_functions[technology].production
    f_metrics    = self.compiled_functions[technology].metric
    
    indices = self.vectorize_indices(technology)
    
    scenarios = self.vectorize_scenarios(technology)
    n = scenarios.shape[0]
    
    design    = self.vectorize_designs(   technology, n, sample_count)
    parameter = self.vectorize_parameters(technology, n, sample_count)

    capital_cost = f_capital(design.scale, parameter)
    fixed_cost   = f_fixed  (design.scale, parameter)

    input_raw = design.input
    input = design.input_efficiency * input_raw
    
    output_raw = f_production(design.scale, capital_cost, design.lifetime, fixed_cost, input, parameter)
    output = design.output_efficiency * output_raw

    cost = np.sum(capital_cost / design.lifetime, axis=0) / design.scale + \
           np.sum(fixed_cost, axis=0) / design.scale +                     \
           np.sum(design.input_price  * input , axis=0) -                  \
           np.sum(design.output_price * output, axis=0)

    metric = f_metrics(design.scale, capital_cost, design.lifetime, fixed_cost, input_raw, input, design.input_price, output_raw, output, cost, parameter)
    
    def organize(df, ix):
      ix1 = pd.MultiIndex.from_product(
        [ix, scenarios, range(1, sample_count + 1)],
        names=["Index", "Scenario", "Sample"]
      )
      df1 = pd.DataFrame({"Value" : df.flatten()}, index=ix1)
      df1["Technology"] = technology
      return df1.set_index(
        ["Technology"],
        append=True
      ).reorder_levels(
        ["Technology", "Scenario", "Sample", "Index"]
      ).sort_index()

    return Results(
      cost   = organize(cost.reshape(cost.shape + (1,)), ["Cost"]      ),
      output = organize(output                         , indices.output),
      metric = organize(metric                         , indices.metric),
    )

      
  def evaluate_scenarios(self, sample_count=1):
    """
    Evaluate scenarios.

    Parameters
    ----------
    sample_count : int
      The number of random samples.
    """

    costs   = pd.DataFrame()
    outputs = pd.DataFrame()
    metrics = pd.DataFrame()
    for technology in self.vectorize_technologies():
      result = self.evaluate(technology, sample_count)
      costs   = pd.concat([costs, result.cost])
      outputs = pd.concat([outputs, result.output])
      metrics = pd.concat([metrics, result.metric])

    def organize(variable, values):
      return self.results.xs(
        variable,
        level="Variable",
        drop_level=False
      ).join(
        values
      ).reorder_levels(
        ["Technology", "Scenario", "Sample", "Variable", "Index"]
      )[["Value", "Units"]]

    return pd.concat([
      organize("Cost", costs),
      organize("Output", outputs),
      organize("Metric", metrics)
      ]).sort_index()
