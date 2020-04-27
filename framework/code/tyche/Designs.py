import importlib as il
import numpy     as np
import pandas    as pd

from .Distributions import parse_distribution
from .IO            import make_table, read_table
from .Types         import Functions, Indices, Inputs, Results


class Designs:
    
    indices     = None
    functions   = None
    designs     = None
    parameters  = None
    results     = None
    
    compiled_functions  = None
    compiled_designs    = None
    compiled_parameters = None
    
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
        "Technology" : np.str_,
        "Scenario"   : np.str_,
        "Variable"   : np.str_,
        "Index"      : np.str_,
        "Value"      : np.str_,
        "Units"      : np.str_,
        "Notes"      : np.str_,
    }
    _parameters_dtypes = {
        "Technology" : np.str_ ,
        "Scenario"   : np.str_ ,
        "Parameter"  : np.str_ ,
        "Offset"     : np.int16,
        "Value"      : np.str_ ,
        "Units"      : np.str_ ,
        "Notes"      : np.str_ ,
    }
    _results_dtypes = {
        "Technology" : np.str_   ,
        "Variable"   : np.str_   ,
        "Index"      : np.str_   ,
        "Units"      : np.str_   ,
        "Notes"      : np.str_   ,
    }
    
    _indices_index     = ["Technology", "Type"    , "Index"             ]
    _functions_index   = ["Technology",                                 ]
    _designs_index     = ["Technology", "Scenario", "Variable" , "Index"]
    _parameters_index  = ["Technology", "Scenario", "Parameter"         ]
    _results_index     = ["Technology", "Variable", "Index"             ]
    
    def __init__(
        self                         ,
        path       = None            ,
        indices    = "indices.tsv"   ,
        functions  = "functions.tsv" ,
        designs    = "designs.tsv"   ,
        parameters = "parameters.tsv",
        results    = "results.tsv"   ,
    ):
        if path == None:
            self._make()
        else:
            self._read(path, indices, functions, designs, parameters, results)
            
    def _make(self):
        self.indices     = make_table(self._indices_dtypes   , self._indices_index    )
        self.functions   = make_table(self._functions_dtypes , self._functions_index  )
        self.designs     = make_table(self._designs_dtypes   , self._designs_index    )
        self.parameters  = make_table(self._parameters_dtypes, self._parameters_index )
        self.results     = make_table(self._results_dtypes   , self._results_index    )
        
    def _read(self, path, indices, functions, designs, parameters, results):
        self.indices     = read_table(path, indices   , self._indices_dtypes    , self._indices_index    )
        self.functions   = read_table(path, functions , self._functions_dtypes  , self._functions_index  )
        self.designs     = read_table(path, designs   , self._designs_dtypes    , self._designs_index    )
        self.parameters  = read_table(path, parameters, self._parameters_dtypes , self._parameters_index )
        self.results     = read_table(path, results   , self._results_dtypes    , self._results_index    )
        
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
    
    def sampler(self, x, samples):
        it = np.nditer(
            [x, None],
            flags=["refs_ok", "external_loop"],
            op_flags=[["readonly"], ["writeonly", "allocate"]],
            op_axes=[list(range(x.ndim)) + [-1], None],
            itershape=x.shape+(samples,)
        )
        for x, y in it:
            y[...] = x[0].rvs(samples)
        return it.operands[1]

    def vectorize_designs(self, technology, n, samples=1):

        extract_designs = lambda variable: self.compiled_designs.xs(
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
                (offsets.shape[0], n)
            )

        return Inputs(
            scale             = self.sampler(scales["Distribution"].values                 , samples),
            lifetime          = self.sampler(join(lifetimes          , all_indices.capital), samples),
            input             = self.sampler(join(inputs             , all_indices.input  ), samples),
            input_efficiency  = self.sampler(join(input_efficiencies , all_indices.input  ), samples),
            input_price       = self.sampler(join(input_prices       , all_indices.input  ), samples),
            output_efficiency = self.sampler(join(output_efficiencies, all_indices.output ), samples),
            output_price      = self.sampler(join(output_prices      , all_indices.output ), samples),
        )
    
    def vectorize_parameters(self, technology, n, samples=1):
        x = self.compiled_parameters.xs(
            technology
        ).reset_index(
        ).sort_values(
            by=["Offset", "Scenario"]
        )["Distribution"].values
        return self.sampler(
            x.reshape((int(x.shape[0] / n), n)),
            samples
        )
    
    def compile(self):

        self.compiled_functions = {}
        for technology, metadata in self.functions.iterrows():
            m = il.import_module("." + metadata["Module"], package="technology")
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
            
    def evaluate(self, technology, samples=1):

        f_capital    = self.compiled_functions[technology].capital
        f_fixed      = self.compiled_functions[technology].fixed        
        f_production = self.compiled_functions[technology].production
        f_metrics    = self.compiled_functions[technology].metric
        
        indices = self.vectorize_indices(technology)
        
        scenarios = self.vectorize_scenarios(technology)
        n = scenarios.shape[0]
        
        design    = self.vectorize_designs(   technology, n, samples)
        parameter = self.vectorize_parameters(technology, n, samples)
        
        capital_cost = f_capital(design.scale, parameter)
        fixed_cost   = f_fixed  (design.scale, parameter)

        input = design.input_efficiency * design.input
        
        output = design.output_efficiency * f_production(capital_cost, fixed_cost, input, parameter)
        
        metric = f_metrics(capital_cost, fixed_cost, input, output, parameter)

        cost = np.sum(capital_cost / design.lifetime, axis=0) / design.scale + \
               np.sum(fixed_cost, axis=0) / design.scale +                     \
               np.sum(design.input_price  * input , axis=0) -                  \
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
        
    def evaluate_scenarios(self, samples=1):
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
