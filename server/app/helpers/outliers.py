"""This module provides functionality to work with outliers."""

import numpy as np


def iqr(iterable, q1_bound=0.25, q2_bound=0.75):
    """Filter out outliers using iqr method based on quantiles."""
    q1_value = np.quantile(iterable, q1_bound)
    q2_value = np.quantile(iterable, q2_bound)

    return list(filter(lambda x: q1_value <= x <= q2_value, iterable))
