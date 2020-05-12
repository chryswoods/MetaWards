
__all__ = ["mix_none"]


def mix_none(**kwargs):
    """This mixer will perform no mixing. The result is that
       the demographics won't interact with one another and
       each disease outbreak will be completely separate.
    """
    return []
