
import pytest
import metawards


@pytest.mark.slow
def test_ran_binomial():
    # I've packaged the numpy random binomial generator
    # (mt19937 generator) into metawards so that we now
    # don't have any major dependencies

    # the random number sequence should be identical
    # for both

    seed = 15324

    import numpy as np

    rng = metawards.utils.seed_ran_binomial(seed)
    np.random.seed(seed)

    for i in range(0, 1000):
        r = metawards.utils.ran_binomial(rng, 0.5, 100)
        s = np.random.binomial(100, 0.5)

        if r != s:
            print(f"{i} {r} {s}")

        assert r == s

    metawards.utils.delete_ran_binomial(rng)

    # if they agree, then I have the numpy ran_binomial, which
    # I think we can trust is correct


if __name__ == "__main__":
    test_ran_binomial()
