"""
Data types for Tyche.
"""

from collections import namedtuple


Indices = namedtuple("Indices", [
  "capital",
  "input"  ,
  "output" ,
  "metric" ,
])
"""
Name tuple type for rows in the *indices* table.
"""


Inputs = namedtuple("Inputs", [
  "lifetime"         ,
  "scale"            ,
  "input"            ,
  "input_efficiency" ,
  "input_price"      ,
  "output_efficiency",
  "output_price"     ,
])
"""
Named tuple type for rows in the *inputs* table.
"""


Results = namedtuple("Results", [
  "cost"  ,
  "output",
  "metric",
])
"""
Named tuple type for rows in the *results* table.
"""


Functions = namedtuple("Functions", [
  "style"     ,
  "capital"   ,
  "fixed"     ,
  "production",
  "metric"    ,
])
"""
Name tuple type for rows in the *functions* table.
"""


Evaluations = namedtuple("Evaluations", [
  "amounts",
  "metrics",
  "summary",
  "uncertain",
])
"""
Named tuple type for rows in the *evaluations* table.
"""


FakeDistribution = namedtuple("FakeDistribution", [
  "rvs",
])
"""
Named tuple type for a fake distribution.
"""
