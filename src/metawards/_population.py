
from dataclasses import dataclass as _dataclass
from typing import List as _List
from typing import Dict as _Dict
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

    #: The totao number of infections in other states
    totals: _Dict[str, int] = None

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
        pop: int = 0

        for val in [self.susceptibles, self.latent,
                    self.total, self.recovereds]:
            if val is not None:
                pop += val

        if self.totals is not None:
            for val in self.totals.values():
                pop += val

        return pop

    @property
    def infecteds(self) -> int:
        """The number who are infected across all wards"""
        return self.population - \
            int(self.susceptibles or 0) - \
            int(self.recovereds or 0)

    def has_equal_SEIR(self, other):
        """Return whether or not the SEIR values for this population
           equal 'other'
        """
        return self.susceptibles == other.susceptibles and \
            self.latent == other.latent and \
            self.total == other.total and \
            self.recovereds == other.recovereds and \
            self.totals == other.totals

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
        parts = []

        parts.append(f"DAY: {self.day}")
        parts.append(f"S: {self.susceptibles}")

        if self.latent is not None:
            parts.append(f"E: {self.latent}")

        if self.total is not None:
            parts.append(f"I: {self.total}")

        if self.totals is not None:
            for key, value in self.totals.items():
                parts.append(f"{key}: {value}")

        if self.recovereds is not None:
            parts.append(f"R: {self.recovereds}")

        if self.n_inf_wards is not None:
            parts.append(f"IW: {self.n_inf_wards}")

        parts.append(f"TOTAL POPULATION {self.population}")

        s = "  ".join(parts)

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

        t = 0

        for val in [self.susceptibles, self.infecteds, self.recovereds]:
            if val is not None:
                t += val

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
                S += int(subpop.susceptibles or 0)
                E += int(subpop.latent or 0)
                I += int(subpop.total or 0)
                R += int(subpop.recovereds or 0)
                P += int(subpop.population or 0)

            if S != int(self.susceptibles or 0):
                errors.append(f"Disagreement in S: {S} "
                              f"versus {self.susceptibles}")

            if E != int(self.latent or 0):
                errors.append(f"Disagreement in E: {E} "
                              f"versus {self.latent}")

            if I != int(self.total or 0):
                errors.append(f"Disagreement in I: {I} "
                              f"versus {self.total}")

            if R != int(self.recovereds or 0):
                errors.append(f"Disagreement in R: {R} "
                              f"versus {self.recovereds}")

            if P != int(self.population or 0):
                errors.append(f"Disagreement in Population: {P} "
                              f"versus {self.population}")

        if len(errors) > 0:
            errors = "\nERROR: ".join(errors)
            from .utils._console import Console
            Console.error(errors)
            raise AssertionError(f"Disagreement in population sums!")

    def headers(self):
        """Return a list of the headers that should be used to report
           data from this population. This returns a list of headers,
           e.g. ["S", "E", "I", "R"]
        """
        headers = []

        if self.susceptibles is not None:
            headers.append("S")

        if self.latent is not None:
            headers.append(f"E")

        if self.total is not None:
            headers.append(f"I")

        if self.totals is not None:
            # use items as need to be same order as items below
            for key, _ in self.totals.items():
                headers.append(key)

        if self.recovereds is not None:
            headers.append("R")

        return headers

    def summary(self, demographics=None):
        """Return a short summary string that is suitable to be printed
           out during a model run

           Returns
           -------
           summary: str
             The short summary string
        """
        parts = []

        parts.append(f"S: {self.susceptibles}")

        if self.latent is not None:
            parts.append(f"E: {self.latent}")

        if self.total is not None:
            parts.append(f"I: {self.total}")

        if self.totals is not None:
            for key, value in self.totals.items():
                parts.append(f"{key}: {value}")

        if self.recovereds is not None:
            parts.append(f"R: {self.recovereds}")

        if self.n_inf_wards is not None:
            parts.append(f"IW: {self.n_inf_wards}")

        parts.append(f"POPULATION: {self.population}")

        summary = "  ".join(parts)

        if self.subpops is None or len(self.subpops) == 0:
            return summary

        from .utils._console import Table

        table = Table(show_edge=True, show_footer=True)

        table.add_column("", footer="total")
        table.add_column("S", footer=self.susceptibles)
        columns = {}
        count = 0
        columns[""] = count
        count += 1

        columns["S"] = count
        count += 1

        if self.latent is not None:
            table.add_column("E", footer=self.latent)
            columns["E"] = count
            count += 1

        if self.total is not None:
            table.add_column("I", footer=self.total)
            columns["I"] = count
            count += 1

        if self.totals is not None:
            for key, value in self.totals.items():
                table.add_column(key, footer=value)
                columns[key] = count
                count += 1

        if self.recovereds is not None:
            table.add_column("R", footer=self.recovereds)
            columns["R"] = count
            count += 1

        if self.n_inf_wards is not None:
            table.add_column("IW", footer=self.n_inf_wards)
            columns["IW"] = count
            count += 1

        table.add_column("POPULATION", footer=self.population)
        columns["POPULATION"] = count
        count += 1

        for i, subpop in enumerate(self.subpops):
            row = [None] * count
            if demographics is not None:
                name = demographics.get_name(i)
                row[0] = name
            else:
                row[0] = str(i)

            row[columns["S"]] = subpop.susceptibles
            row[columns["E"]] = subpop.latent
            row[columns["R"]] = subpop.recovereds
            row[columns["I"]] = subpop.total
            row[columns["IW"]] = subpop.n_inf_wards

            if subpop.totals is not None:
                for key, value in subpop.totals.items():
                    row[columns[key]] = value

            row[-1] = subpop.population

            table.add_row(row)

        return summary + "\n" + table.to_string()


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
