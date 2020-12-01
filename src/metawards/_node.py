
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

    #: The per-ward scale_uv (amount to scale up or down the FOI
    scale_uv: float = 1.0

    #: The per-ward cutoff (restrict movement to below this distance in km)
    cutoff: float = 99999.99

    #: Per-ward background FOI (starting value for FOI calculations)
    bg_foi: float = 0.0

    #: The per-ward custom user parameters
    _custom_params = {}

    def get_custom(self, key: str, default: float = 0.0) -> float:
        """Return the value of the custom parameter at key 'key',
           returning 'default' if this doesn't exist
        """
        return self._custom_params.get(key, default)

    def set_custom(self, key: str, value: float) -> None:
        """Set the value of the custom parameter at key 'key' to 'value'.
           Note that this *must* be a floating point value, or something
           that can be converted to a float
        """
        self._custom_params[key] = float(value)
