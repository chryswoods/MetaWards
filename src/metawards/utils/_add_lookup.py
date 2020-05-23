
from .._network import Network

__all__ = ["add_lookup"]


def add_lookup(network: Network, nthreads: int = 1):
    """Add in metadata about the network that can be used
       to look up wards by name of location or region etc.

       This will add the data to the network.ward_info object,
       as a list ensuring that network.nodes[i] has its
       info in network.ward_info[i]
    """
    lookup_file = network.params.input_files.lookup

    if lookup_file is None:
        from ._console import Console
        Console.print("No ward lookup information available.")
        return

    lines = open(lookup_file, "r").readlines()

    if lines[0].find(",") != -1:
        sep = ","
    else:
        sep = " "

    columns = network.params.input_files.lookup_columns

    WDCD = columns.get("code", None)
    WDNM = columns.get("name", None)
    CMWDCD = columns.get("alternate_code", None)
    CMWDNM = columns.get("alternate_name", None)
    LADCD = columns.get("authority_code", None)
    LADNM = columns.get("authority_name", None)
    REGCD = columns.get("region_code", None)
    REGNM = columns.get("region_name", None)

    from .._wardinfo import WardInfo, WardInfos

    ward_infos = []
    ward_infos.append(None)   # 1-indexed

    import csv

    for parts in csv.reader(lines[1:], quotechar='"', delimiter=',',
                            quoting=csv.QUOTE_ALL, skipinitialspace=True):

        info = WardInfo()

        if WDCD is not None:
            info.code = parts[WDCD].strip()

        if WDNM is not None:
            info.name = parts[WDNM].strip()

        if CMWDCD is not None:
            info.alternate_codes.append(parts[CMWDCD].strip())

        if CMWDNM is not None:
            info.alternate_names.append(parts[CMWDNM].strip())

        if LADCD is not None:
            info.authority_code = parts[LADCD].strip()

        if LADNM is not None:
            info.authority = parts[LADNM].strip()

        if REGCD is not None:
            info.region_code = parts[REGCD].strip()

        if REGNM is not None:
            info.region = parts[REGNM].strip()

        ward_infos.append(info)

    if len(ward_infos) != network.nnodes + 1:
        from ._console import Console
        Console.warning(
            f"Number of wards from {lookup_file} "
            f"({len(ward_infos)}) disagrees with the number "
            f"of wards in the network ({network.nnodes})")

        if len(ward_infos) > network.nnodes+1:
            ward_infos = ward_infos[0:network.nnodes+1]
        else:
            while len(ward_infos) <= network.nnodes:
                ward_infos.append(None)

    network.info = WardInfos(wards=ward_infos)
