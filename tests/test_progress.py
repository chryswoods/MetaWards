
from metawards.utils import Console
import pytest


def test_progress_error():
    with pytest.raises(KeyError):
        with Console.progress() as progress:
            task = progress.add_task("Something", total=10)
            for i in range(1, 11):
                progress.update(task, completed=i)
                raise KeyError()


if __name__ == "__main__":
    test_progress_error()
