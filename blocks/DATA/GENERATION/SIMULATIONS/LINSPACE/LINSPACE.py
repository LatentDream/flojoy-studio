import numpy as np
from flojoy import flojoy, Vector, DataContainer
from typing import Optional


@flojoy
def LINSPACE(
    start: float = 10,
    end: float = 0,
    step: int = 1000,
    default: Optional[DataContainer] = None,
) -> Vector:
    """Generate a Vector of evenly spaced data between two points.

    This block uses the 'linspace' numpy function. It is useful for generating an x-axis for the OrderedPair data type.

    Parameters
    ----------
    start : float
        The start point of the data.
    end : float
        The end point of the data.
    step : float
        The number of points in the vector.

    Returns
    -------
    Vector
        v: the vector between 'start' and 'end' with a 'step' number of points.
    """

    v = np.linspace(start, end, step)
    return Vector(v=v)
