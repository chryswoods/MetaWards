
from metawards.utils import Profiler


def test_profiler():
    p = Profiler()
    p = p.start("main")

    assert p.name() == "main"
    assert p.total() is None
    assert p.child_total() is None

    p = p.start("child1")

    assert p.name() == "child1"
    assert p.total() is None

    p = p.stop()

    assert p.name() == "main"
    assert p.child_total() >= 0

    p = p.start("child2")

    assert p.name() == "child2"
    assert p.total() is None

    p = p.start("grandchild")

    assert p.name() == "grandchild"
    assert p.total() is None

    p = p.stop()

    assert p.name() == "child2"
    assert p.child_total() >= 0

    p = p.stop()

    assert p.name() == "main"
    assert p.child_total() >= 0
    assert p.total() is None

    p = p.stop()

    assert p.name() is None
    assert p.child_total() >= 0

    print(p)

if __name__ == "__main__":
    test_profiler()
