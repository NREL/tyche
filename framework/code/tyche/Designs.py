import importlib as il
import numpy     as np
import os        as os
import pandas    as pd

from .Types import Functions, Indices, Inputs, Investments, Results


class Designs:
    
    indices     = None
    functions   = None
    designs     = None
    parameters  = None
    results     = None
    tranches    = None
    investments = None
    
    compilation = None
    
    _indices_dtypes = {
        "Technology"  : np.str_ ,
        "Type"        : np.str_ ,
        "Index"       : np.str_ ,
        "Offset"      : np.int16,
        "Description" : np.str_ ,
        "Notes"       : np.str_ ,
    }
    _functions_dtypes = {
        "Technology" : np.str_,
        "Style"      : np.str_,
        "Module"     : np.str_,
        "Capital"    : np.str_,
        "Fixed"      : np.str_,
        "Production" : np.str_,
        "Metrics"    : np.str_,
        "Notes"      : np.str_,
    }
    _designs_dtypes = {
        "Technology" : np.str_   ,
        "Scenario"   : np.str_   ,
        "Variable"   : np.str_   ,
        "Index"      : np.str_   ,
        "Value"      : np.float64,
        "Units"      : np.str_   ,
        "Notes"      : np.str_   ,
    }
    _parameters_dtypes = {
        "Technology" : np.str_   ,
        "Scenario"   : np.str_   ,
        "Parameter"  : np.str_   ,
        "Offset"     : np.int16  ,
        "Value"      : np.float64,
        "Units"      : np.str_   ,
        "Notes"      : np.str_   ,
    }
    _results_dtypes = {
        "Technology" : np.str_   ,
        "Variable"   : np.str_   ,
        "Index"      : np.str_   ,
        "Units"      : np.str_   ,
        "Notes"      : np.str_   ,
    }
    _tranches_dtypes = {
        "Category"   : np.str_   ,
        "Tranche"    : np.str_   ,
        "Scenario"   : np.str_   ,
        "Notes"      : np.str_   ,
    }
    _investments_dtypes = {
        "Investment" : np.str_   ,
        "Category"   : np.str_   ,
        "Tranche"    : np.str_   ,
        "Amount"     : np.float64,
        "Notes"      : np.str_   ,
    }
    
    _indices_index     = ["Technology", "Type"    , "Index"             ]
    _functions_index   = ["Technology",                                 ]
    _designs_index     = ["Technology", "Scenario", "Variable" , "Index"]
    _parameters_index  = ["Technology", "Scenario", "Parameter"         ]
    _results_index     = ["Technology", "Variable", "Index"             ]
    _tranches_index    = ["Category"  , "Tranche" , "Scenario" ,        ]
    _investments_index = ["Investment", "Category", "Tranche"  ,        ]
    
    def __init__(self, path=None):
        if path == None:
            self._make()
        else:
            self._read(path)
            
    def _make(self):
        make = lambda dtypes, index: pd.DataFrame({k: [v()] for k, v in dtypes.items()}, index=index).iloc[0:0]
        self.indices     = make(self._indices_dtypes    , self._indices_index    )
        self.functions   = make(self._functions_dtypes  , self._functions_index  )
        self.designs     = make(self._designs_dtypes    , self._designs_index    )
        self.parameters  = make(self._parameters_dtypes , self._parameters_index )
        self.results     = make(self._results_dtypes    , self._results_index    )
        self.tranches    = make(self._tranches_dtypes   , self._tranches_index   )
        self.investments = make(self._investments_dtypes, self._investments_index)
        
    def _read(self, path):
        read = lambda name, dtypes, index: pd.read_csv(
            os.path.join(path, name),
            sep="\t",
            index_col=index, converters=dtypes
        ).sort_index()
        self.indices     = read("indices.tsv"    , self._indices_dtypes    , self._indices_index    )
        self.functions   = read("functions.tsv"  , self._functions_dtypes  , self._functions_index  )
        self.designs     = read("designs.tsv"    , self._designs_dtypes    , self._designs_index    )
        self.parameters  = read("parameters.tsv" , self._parameters_dtypes , self._parameters_index )
        self.results     = read("results.tsv"    , self._results_dtypes    , self._results_index    )
        self.tranches    = read("tranches.tsv"   , self._tranches_dtypes   , self._tranches_index   )
        self.investments = read("investments.tsv", self._investments_dtypes, self._investments_index)
        
    def vectorize_technologies(self):
        return self.designs.reset_index(
            ["Scenario", "Variable", "Index"]
        ).sort_index(
        ).index.drop_duplicates(
        ).values
    
    def vectorize_scenarios(self, technology):
        return self.designs.xs(technology
        ).reset_index(
            ["Variable", "Index"]
        ).sort_index(
        ).index.drop_duplicates(
        ).values
    
    def _vectorize_indices(self, technology):
        extract_indices = lambda index: self.indices.xs(
                                            (technology, index)
                                        ).sort_values(
                                            by="Offset"
                                        )[["Offset"]]
        return Indices(
            capital = extract_indices("Capital"),
            fixed   = extract_indices("Fixed"  ),
            input   = extract_indices("Input"  ),
            output  = extract_indices("Output" ),
            metric  = extract_indices("Metric" ),
        )
    
    def vectorize_indices(self, technology):
        vectors = self._vectorize_indices(technology)
        return Indices(
            capital = vectors.capital.index.values,
            fixed   = vectors.fixed.index.values  ,
            input   = vectors.input.index.values  ,
            output  = vectors.output.index.values ,
            metric  = vectors.metric.index.values ,
        )
    
    def vectorize_designs(self, technology, n):

        extract_designs = lambda variable: self.designs.xs(
                                               (technology, variable),
                                               level=["Technology", "Variable"]
                                           )[["Value"]]
        lifetimes           = extract_designs("Lifetime"         )
        scales              = extract_designs("Scale"            )
        inputs              = extract_designs("Input"            )
        input_efficiencies  = extract_designs("Input efficiency" )
        input_prices        = extract_designs("Input price"      )
        output_efficiencies = extract_designs("Output efficiency")
        output_prices       = extract_designs("Output price"     )
    
        all_indices = self._vectorize_indices(technology)
    
        join = lambda values, offsets: values.join(
                                           offsets
                                       ).reorder_levels(
                                           [1, 0]
                                       ).reset_index(
                                       ).sort_values(
                                           by=["Offset", "Scenario"]
                                       )["Value"].values.reshape((
                                           offsets.shape[0], n)
                                       )
        return Inputs(
            lifetime          = join(lifetimes          , all_indices.capital),
            scale             = scales["Value"].values                        ,
            input             = join(inputs             , all_indices.input  ),
            input_efficiency  = join(input_efficiencies , all_indices.input  ),
            input_price       = join(input_prices       , all_indices.input  ),
            output_efficiency = join(output_efficiencies, all_indices.output ),
            output_price      = join(output_prices      , all_indices.output ),
        )
    
    def vectorize_parameters(self, technology, n):
        x = self.parameters.xs(
            technology
        ).reset_index(
        ).sort_values(
            by=["Offset", "Scenario"]
        )["Value"].values
        return x.reshape((int(x.shape[0] / n), n)) 
    
    def compile(self):
        self.compilation = {}
        for technology, metadata in self.functions.iterrows():
            m = il.import_module("." + metadata["Module"], package="technology")
            self.compilation[technology] = Functions(
                style      =             metadata["Style"     ] ,
                capital    = eval("m." + metadata["Capital"   ]),
                fixed      = eval("m." + metadata["Fixed"     ]),
                production = eval("m." + metadata["Production"]),
                metric     = eval("m." + metadata["Metrics"   ]),
            )
            
    def evaluate(self, technology):

        f_capital    = self.compilation[technology].capital
        f_fixed      = self.compilation[technology].fixed        
        f_production = self.compilation[technology].production
        f_metrics    = self.compilation[technology].metric
        
        indices = self.vectorize_indices(technology)
        
        scenarios = self.vectorize_scenarios(technology)
        n = scenarios.shape[0]
        
        design    = self.vectorize_designs(   technology, n)
        parameter = self.vectorize_parameters(technology, n)
        
        capital_cost = f_capital(design.scale, parameter)
        fixed_cost   = f_fixed  (design.scale, parameter)

        input = design.input_efficiency * design.input
        
        output = design.output_efficiency * f_production(capital_cost, fixed_cost, input, parameter)
        
        metric = f_metrics(capital_cost, fixed_cost, input, output, parameter)

        cost = np.sum(capital_cost / design.lifetime, axis=0) / design.scale + \
               np.sum(fixed_cost, axis=0) / design.scale + \
            np.sum(design.input_price  * input , axis=0) - \
            np.sum(design.output_price * output, axis=0)
        
        def organize(df):
            df1 = pd.melt(
                df.rename_axis(["Scenario"]).reset_index(),
                id_vars=["Scenario"],
                value_vars=df.columns,
                var_name="Index",
                value_name="Value"
            )
            df1["Technology"] = technology
            return df1.set_index(["Technology", "Scenario", "Index"])

        return Results(
            cost   = organize(pd.DataFrame(cost.reshape((cost.shape[0], 1)), index=scenarios, columns=["Cost"]      )),
            output = organize(pd.DataFrame(np.transpose(output)            , index=scenarios, columns=indices.output)),
            metric = organize(pd.DataFrame(np.transpose(metric)            , index=scenarios, columns=indices.metric)),
        )
        
    def evaluate_scenarios(self):
        costs   = pd.DataFrame()
        outputs = pd.DataFrame()
        metrics = pd.DataFrame()
        for technology in self.vectorize_technologies():
            result = self.evaluate(technology)
            costs   = costs.append(  result.cost  )
            outputs = outputs.append(result.output)
            metrics = metrics.append(result.metric)
        organize = lambda variable, values: self.results.xs(
                                                variable,
                                                level="Variable",
                                                drop_level=False
                                            ).join(
                                                values
                                            ).reorder_levels(
                                                ["Technology", "Scenario", "Variable", "Index"]
                                            )[["Value", "Units"]]
        return organize("Cost", costs).append(
            organize("Output", outputs)
        ).append(
            organize("Metric", metrics)
        ).sort_index()

    def evaluate_investments(self):
        amounts = self.investments.sum(
            level=["Investment"]
        )
        metrics = self.investments.drop(
            columns=["Amount", "Notes"]
        ).join(
            self.tranches.drop(columns=["Notes"])
        ).join(
            self.evaluate_scenarios().xs("Metric", level="Variable")
        ).reorder_levels(
            ["Investment", "Category", "Tranche", "Scenario", "Technology", "Index"]
        )
        return Investments(
            amounts = amounts,
            metrics = metrics,
            summary = metrics.set_index(
                "Units",
                append=True
            ).sum(
                level=["Investment", "Index", "Units"]
            ).reset_index(
                "Units"
            )[["Value", "Units"]],
        )
