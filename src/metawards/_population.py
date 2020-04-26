
from dataclasses import dataclass as _dataclass
from typing import List as _List
from copy import deepcopy as _deepcopy
from datetime import date as _date

__all__ = ["Population", "Populations"]


@_dataclass
class Population:
    """This class holds information about the progress of the
       disease through the population
    """
    #: The initial population loaded into the model
    initial: int = 0
    #: The number of members who could be infected
    susceptibles: int = 0
    #: The number of latent infections
    latent: int = 0
    #: The total number of infections
    total: int = 0
    #: The total number who are removed from the outbreak,
    #: either because they have recovered, or are otherwise
    #: no longer able to be infected
    recovereds: int = 0
    #: The number infected in all wards
    n_inf_wards: int = 0
    #: The scale_uv parameter that can be used to affect the
    #: foi calculation. A value of 1.0 means do nothing
    scale_uv: float = 1.0
    #: The day in the outbreak of this record (e.g. day 0, day 10 etc.)
    day: int = 0
    #: The date in the outbreak of this record
    date: _date = None

    @property
    def population(self) -> int:
        """The total population in all wards"""
        return self.susceptibles + self.latent + self.total + self.recovereds

    @property
    def infecteds(self) -> int:
        """The number who are infected across all wards"""
        return self.total + self.latent

    def __str__(self):
        s = f"DAY: {self.day} " \
            f"S: {self.susceptibles}    " \
            f"E: {self.latent}    " \
            f"I: {self.total}    " \
            f"R: {self.recovereds}    " \
            f"IW: {self.n_inf_wards}   " \
            f"UV: {self.scale_uv}   " \
            f"TOTAL POPULATION {self.population}"

        if self.date:
            return f"{self.date.isoformat()}: {s}"
        else:
            return s


@_dataclass
class Populations:
    """This class holds the trajectory of Population objects recorded
       for every step (day) of a model outbreak
    """
    #: The trajectory of Population objects
    _trajectory: _List[Population] = None

    def __str__(self):
        if len(self) == 0:
            return "Populations:empty"
        else:
            return f"Latest: {self._trajectory[-1]}"

    def __getitem__(self, i: int):
        """Return the ith Population in the trajectory"""
        if self._trajectory is None:
            raise IndexError("No trajectory data collected")
        else:
            return self._trajectory[i]

    def __len__(self):
        if self._trajectory is None:
            return 0
        else:
            return len(self._trajectory)

    def append(self, population: Population):
        """Append the next step in the trajectory.

           Parameters
           ----------
           population: Population
             The population to append to this list
        """
        if not isinstance(population, Population):
            raise TypeError("Only Population objects should be recorded!")

        if self._trajectory is None:
            self._trajectory = []

        self._trajectory.append(_deepcopy(population))
