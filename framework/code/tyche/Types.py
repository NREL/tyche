from collections import namedtuple


Scenarios = namedtuple("Scenarios", [
    "technology",
    "scenario"  ,
])


Indices = namedtuple("Indices", [
    "capital",
    "fixed"  ,
    "input"  ,
    "output" ,
    "metric" ,
])


Inputs = namedtuple("Inputs", [
    "capital_cost"     ,
    "lifetime"         ,
    "fixed_cost"       ,
    "scale"            ,
    "input"            ,
    "input_efficiency" ,
    "input_price"      ,
    "output_efficiency",
    "output_price"     ,
])


Results = namedtuple("Results", [
    "cost"  ,
    "output",
    "metric",
])


Functions = namedtuple("Functions", [
    "style"     ,
    "capital"   ,
    "fixed"     ,
    "production",
    "metric"    ,
])
