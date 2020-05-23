

from ._ran_binomial cimport _construct_binomial_rng, _ran_binomial, \
                            _seed_ran_binomial, _delete_binomial_rng, \
                            _get_binomial_ptr, _ran_uniform


__all__ = ["ran_binomial", "ran_uniform", "ran_int",
           "seed_ran_binomial", "delete_ran_binomial"]


# The plan with this file is to move to an inline cdef that just
# calls the gsl_ran_binomial function directly. Moving away from
# pygsl (and indeed probably gsl) as this is too heavyweight an
# import just to use a random binomial generator. The signature
# of this function in the code will remain though...


def seed_ran_binomial(seed: int = None):
    """Seed and return the random binomial generator. This returns
       the object that you should pass to ran_binomial to generate
       random numbers drawn from a binomial distribution
    """
    if seed is None:
        import random
        seed = random.randint(10000, 99999999)

    from ._console import Console
    Console.print(f"Using random number seed: **{seed}**", markdown=True)
    rng = _construct_binomial_rng()
    _seed_ran_binomial(rng, seed)

    cdef binomial_rng* r = _get_binomial_ptr(rng)

    return rng


def ran_binomial(rng, p: float, n: int):
    """Return a random number drawn from the binomial distribution
       [p,n] (see gsl_ran_binomial for documentation)
    """
    cdef binomial_rng *r = _get_binomial_ptr(rng)
    return _ran_binomial(r, p, n)


def ran_uniform(rng):
    """Return a random double drawn from a uniform distribution between
       zero and one
    """
    cdef binomial_rng *r = _get_binomial_ptr(rng)
    return _ran_uniform(r)


def ran_int(rng, lower=0, upper=(2**32)-1):
    """Draw a random integer from [0,upper] inclusive"""
    return lower + int(ran_uniform(rng) * (upper-lower))


def delete_ran_binomial(rng):
    """Delete the passed random number generator.

       WARNING: It will not be safe to use this generator after
                you have deleted it!
    """
    _delete_binomial_rng(rng)
