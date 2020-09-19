"""
Utilities for probability distributions.
"""

import numpy       as np
import scipy.stats as st

from numpy.linalg import norm
from numpy.random import choice
from .Types       import FakeDistribution


def constant(value):
  """
  The constant distribution.

  Parameters
  ----------
  value : float
    The constant value.
  """

  return st.norm(value, 0)


def mixture(weights, distributions):
  """
  A mixture of two distributions.

  Parameters
  ----------
  weights : array of float
    The weights of the distributions to be mixed.
  distributions : array of distributions
    The distributions to be mixed.
  """

  ks = np.arange(0, len(weights))
  ps = weights / np.linalg.norm(weights, ord=1)
  return FakeDistribution(
    rvs = lambda n: np.fromiter(
      map(
        lambda i: distributions[i].rvs(),
        np.random.choice(ks, n, p=ps)
      ),
      dtype=np.float
    )
  )


def parse_distribution(text):
  """
  Make the Python object for the distribution, if any is specified.

  Parameters
  ----------
  text : str
    The Python expression for the distribution, or plain text.
  """

  try:
    return constant(np.float64(text))
  except ValueError:
    return eval(text)
