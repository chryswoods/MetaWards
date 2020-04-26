
from libc.math cimport exp

cdef inline double rate_to_prob(double rate) nogil:
    """Convert the return the probability associated with the passed
       infection rate
    """
    return rate - (0.5*rate*rate) if rate < 1e-6 else 1.0 - exp(-rate)
