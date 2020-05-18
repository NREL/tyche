import numpy       as np
import scipy.stats as st

from numpy.linalg import norm
from numpy.random import choice
from .Types       import FakeDistribution


def constant(value):
    return st.norm(value, 0)


def mixture(weights, distributions):
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
    try:
        return constant(np.float64(text))
    except ValueError:
        return eval(text)
