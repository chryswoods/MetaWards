
__all__ = ["mix_evenly"]


def mix_evenly(stage: str, **kwargs):
    """This mixer will evenly mix all demographics. This should be
       equivalent to a null model, and produce similar results
       as if the population was all in a single demographic
    """
    if stage == "foi":
        from ._merge_evenly import merge_evenly
        return [merge_evenly]
    else:
        from ._mix_default import mix_default
        return mix_default(stage=stage, **kwargs)
