
__all__ = ["mix_default"]


def mix_default(**kwargs):
    """This is the default mixer. By default, nothing extra is mixed
       at any stage of the model run
    """
    from ._mix_none import mix_none
    return mix_none()
