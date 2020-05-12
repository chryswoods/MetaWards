
__all__ = ["extract_small"]


def extract_small(**kwargs):
    """This extractor only extracts the 'small' default files,
       e.g. nothing that involves the incidence or prevalence
       matrices
    """

    from ._output_basic import output_basic
    from ._output_dispersal import output_dispersal

    return [output_basic, output_dispersal]
