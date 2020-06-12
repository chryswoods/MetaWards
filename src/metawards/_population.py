
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

    #: The populations in each of the multi-demographic subnetworks
    subpops = None

    @property
    def population(self) -> int:
        """The total population in all wards"""
        return self.susceptibles + self.latent + self.total + self.recovereds

    @property
    def infecteds(self) -> int:
        """The number who are infected across all wards"""
        return self.total + self.latent

    def has_equal_SEIR(self, other):
        """Return whether or not the SEIR values for this population
           equal 'other'
        """
        return self.susceptibles == other.susceptibles and \
            self.latent == other.latent and \
            self.total == other.total and \
            self.recovereds == other.recovereds

    def increment_day(self, ndays: int = 1) -> None:
        """Advance the day count by 'ndays' (default 1)"""
        self.day += ndays

        if self.subpops is not None:
            for pop in self.subpops:
                pop.day += ndays

        if self.date:
            from datetime import timedelta
            self.date += timedelta(days=1)

            if self.subpops is not None:
                for pop in self.subpops:
                    pop.date = self.date

    def specialise(self, network):
        """Specialise this population for the passed Networks"""
        subpops = []

        from copy import deepcopy

        self.subpops = None

        for i in range(0, len(network.subnets)):
            subpops.append(deepcopy(self))

        self.subpops = subpops

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

    def assert_sane(self):
        """Assert that this population is sane, i.e. the totals within
           this population and with the sub-populations all add up to
           the correct values
        """
        errors = []

        t = self.susceptibles + self.latent + self.total + self.recovereds

        if t != self.population:
            errors.append(f"Disagreement in total overall population: "
                          f"{t} versus {self.population}")

        if self.subpops is not None and len(self.subpops) > 0:
            S = 0
            E = 0
            I = 0
            R = 0
            P = 0

            for subpop in self.subpops:
                S += subpop.susceptibles
                E += subpop.latent
                I += subpop.infecteds
                R += subpop.recovereds
                P += subpop.population

            if S != self.susceptibles:
                errors.append(f"Disagreement in S: {S} "
                              f"versus {self.susceptibles}")

            if E != self.latent:
                errors.append(f"Disagreement in E: {E} "
                              f"versus {self.latent}")

            if I != self.infecteds:
                errors.append(f"Disagreement in I: {I} "
                              f"versus {self.infecteds}")

            if R != self.recovereds:
                errors.append(f"Disagreement in R: {R} "
                              f"versus {self.recovereds}")

            if P != self.population:
                errors.append(f"Disagreement in Population: {P} "
                              f"versus {self.population}")

        if len(errors) > 0:
            errors = "\nERROR: ".join(errors)
            from .utils._console import Console
            Console.error(errors)
            raise AssertionError(f"Disagreement in population sums!")

    def summary(self, demographics=None):
        """Return a short summary string that is suitable to be printed
           out during a model run

           Returns
           -------
           summary: str
             The short summary string
        """
        summary = f"S: {self.susceptibles}  E: {self.latent}  " \
                  f"I: {self.total}  R: {self.recovereds}  " \
                  f"IW: {self.n_inf_wards}  POPULATION: {self.population}"

        if self.subpops is None or len(self.subpops) == 0:
            return summary

        subs = []
        for i, subpop in enumerate(self.subpops):
            if demographics is not None:
                name = demographics.get_name(i)
                subs.append(f"{name}  {subpop.summary()}")
            else:
                subs.append(f"{i}  {subpop.summary()}")

        from .utils._align_strings import align_strings
        subs = align_strings(subs, ":")

        return f"{summary}\n  " + "\n  ".join(subs)


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

    def strip_demographics(self):
        """Remove the demographics information from this trajectory. This
           makes it much smaller and easier to transmit over a network
        """
        for value in self._trajectory:
            value._subpops = None

        return self

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
