
from libc.stdint cimport uintptr_t

cdef extern from "../ran_binomial/distributions.h":
    ctypedef struct binomial_rng

    binomial_rng* binomial_rng_alloc() nogil
    void binomial_rng_free (binomial_rng * r) nogil

    void seed_ran_binomial ( binomial_rng * rng, int seed) nogil
    unsigned int ran_binomial(binomial_rng * rng, double p, unsigned int n) nogil
    double binomial_rng_uniform(binomial_rng * rng) nogil


cdef inline uintptr_t _construct_binomial_rng() nogil:
    """Construct and return a pointer to a new gsl random number
       generator. This will return a uintptr_t that can be handled
       in Python. You must destroy this random number generator
       when you don't want it anymore, using the _delete_gsl_rng
       function
    """
    cdef binomial_rng* r
    r = binomial_rng_alloc()

    cdef uintptr_t p = <uintptr_t>r

    return p


cdef inline void _delete_binomial_rng(uintptr_t rng) nogil:
    """Delete the passed gsl random number generator.
       WARNING: It is not safe to use this pointer to
       generate any more random numbers!
    """
    cdef binomial_rng* r = _get_binomial_ptr(rng)
    binomial_rng_free(r)


cdef inline binomial_rng* _get_binomial_ptr(uintptr_t rng) nogil:
    """Get the underlying binomial_rng pointer from the uintptr_t"""
    cdef binomial_rng* r = <binomial_rng*>rng

    return r


cdef inline uintptr_t _seed_ran_binomial(uintptr_t rng,
                                         unsigned long seed) nogil:
    """Seed the passed random number generator"""
    cdef binomial_rng* r = _get_binomial_ptr(rng)
    seed_ran_binomial(r, seed)


cdef inline int _ran_binomial(binomial_rng *rng, double p, int n) nogil:
    """Generate a random number from the binomial distribution
       described by p and n
    """
    return ran_binomial(rng, p, n)

cdef inline double _ran_uniform(binomial_rng *rng) nogil:
    """Generate the next random-distributed uniform [0,1] random number"""
    return binomial_rng_uniform(rng)
