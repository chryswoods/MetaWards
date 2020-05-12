
from dataclasses import dataclass

__all__ = ["Link"]


@dataclass
class Link:
    """This is a link between nodes in the network"""

    #: Index of the origin node (ward)
    ifrom: int = None

    #: Index of the destination node (ward)
    ito: int = None

    #: Weight of the link, used to save the original number
    #: of susceptibles in the work matrix
    weight: float = None

    #: Number of susceptibles in the case of the work matrix. Used
    #: to save the weight of the play matrix
    suscept: float = None

    #: The distance between the two wards connected by this link
    distance: float = None
