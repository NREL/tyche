from collections import namedtuple


Indices = namedtuple("Indices", [
    "capital",
    "fixed"  ,
    "input"  ,
    "output" ,
    "metric" ,
])


Inputs = namedtuple("Inputs", [
    "lifetime"         ,
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
