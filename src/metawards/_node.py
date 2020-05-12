
from dataclasses import dataclass

__all__ = ["Node"]


@dataclass
class Node:
    """This class represents an electoral ward (node) in the network"""

    #: The node's label (int). This is the index of the node, which must
    #: run from 1 up to len(nodes). A value of -1 implies a null node
    label: int = None

    #: The index (int) of the first link for this node in the
    #: network Links list
    begin_to: int = None

    #: The number (int) of links for this node in the Links list
    end_to: int = None

    self_w: int = None

    #: The index (int) of the first link for this node in the network
    #: play Links list (play)
    begin_p: int = None

    #: The number (int) of links for this node in the Links play list
    end_p: int = None

    self_p: int = None

    day_foi: float = 0.0        # numerator only
    night_foi: float = 0.0      # numerator only
    weekend_foi: float = 0.0    # numerator only

    #: The number of susceptible players in this ward
    play_suscept: float = 0.0
    save_play_suscept: float = 0.0

    denominator_n: float = 0.0  # Denominator only
    denominator_d: float = 0.0  # Maybe won't need

    denominator_p: float = 0.0
    denominator_pd: float = 0.0

    #: x coordinate of the ward (location)
    x: float = 0.0

    #: y coordinate of the ward (location)
    y: float = 0.0
