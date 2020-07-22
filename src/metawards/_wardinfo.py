
from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import List as _List
from typing import Dict as _Dict

__all__ = ["WardInfo", "WardInfos"]


@_dataclass
class WardInfo:
    """This class holds metadata about a ward, e.g. its name(s),
       any ID code(s), any information about the region or
       authority it is in etc.
    """
    #: Name of the ward
    name: str = ""
    #: Any alternative names of the ward
    alternate_names: _List[str] = _field(default_factory=list)

    #: Official ID code of the ward
    code: str = ""
    #: Any alternative ID codes of the ward
    alternate_codes: _List[str] = _field(default_factory=list)

    #: The name of the local authority it is in
    authority: str = ""

    #: The ID of the local authority it is in
    authority_code: str = ""

    #: The name of the region it is in
    region: str = ""

    #: The ID of the region it is in
    region_code: str = ""

    def __hash__(self):
        return f"{self.name} | {self.authority} | {self.region}".__hash__()

    def is_null(self):
        return self == WardInfo()

    def summary(self):
        """Return a summary string that identifies this WardInfo"""
        s = []

        if len(self.name) > 0:
            s.append(self.name)
        elif len(self.alternate_names) > 0:
            s.append(self.alternate_names[0])
        elif len(self.code) > 0:
            s.append(self.code)
        elif len(self.alternate_codes) > 0:
            s.append(self.alternate_codes[0])

        if len(self.authority) > 0:
            s.append(self.authority)
        elif len(self.authority_code) > 0:
            s.append(self.authority_code)

        if len(self.region) > 0:
            s.append(self.region)
        elif len(self.region_code) > 0:
            s.appened(self.region_code)

        return "/".join(s)

    def to_data(self):
        """Return a dictionary that contains all of this data, in
           a format that can be serialised to JSON
        """
        data = {}

        if self.name is not None and len(self.name) > 0:
            data["name"] = str(self.name)

        if self.alternate_names is not None and len(self.alternate_names) > 0:
            data["alternate_names"] = [str(x) for x in self.alternate_names]

        if self.code is not None and len(self.code) > 0:
            data["code"] = str(self.code)

        if self.alternate_codes is not None and len(self.alternate_codes) > 0:
            data["alternate_codes"] = [str(x) for x in self.alternate_codes]

        if self.authority is not None and len(self.authority) > 0:
            data["authority"] = str(self.authority)

        if self.authority_code is not None and len(self.authority_code) > 0:
            data["authority_code"] = str(self.authority_code)

        if self.region is not None and len(self.region) > 0:
            data["region"] = str(self.region)

        if self.region_code is not None and len(self.region_code) > 0:
            data["region_code"] = str(self.region_code)

        return data

    @staticmethod
    def from_data(data):
        """Construct from the passed dictionary, which has, e.g. been
           deserialised from JSON
        """
        if data is None or len(data) == 0:
            return WardInfo()

        info = WardInfo()

        info.name = str(data.get("name", ""))
        info.alternate_names = [str(x) for x in
                                data.get("alternate_names", [])]
        info.code = str(data.get("code", ""))
        info.alternate_codes = [str(x) for x in
                                data.get("alternate_codes", [])]
        info.authority = str(data.get("authority", ""))
        info.authority_code = str(data.get("authority_code", ""))
        info.region = str(data.get("region", ""))
        info.region_code = str(data.get("region_code", ""))

        return info


@_dataclass
class WardInfos:
    """Simple class that holds a list of WardInfo objects, and provides
       useful search functions over that list. This prevents me from
       cluttering up the interface of Network
    """
    #: The list of WardInfo objects, one for each ward in order
    wards: _List[WardInfo] = _field(default_factory=list)

    #: The index used to speed up lookup of wards
    _index: _Dict[WardInfo, int] = None

    def __len__(self):
        return len(self.wards)

    def __getitem__(self, index: int) -> WardInfo:
        return self.wards[index]

    def __setitem__(self, i: int, info: WardInfo) -> None:
        """Set the ith WardInfo equal to 'info'."""
        if info is not None:
            if not isinstance(info, WardInfo):
                raise TypeError(
                    f"Setting item at index {i} to not a WardInfo {info} "
                    f"is not allowed")

        if i >= len(self.wards):
            self.wards += [None] * (i - len(self.wards) + 1)
            self.wards[i] = info

            if info is not None and self._index is not None:
                self._index[info] = i

            return

        elif i < 0:
            i = len(self.wards) + i

            if i < 0:
                raise IndexError(f"Invalid index")

        if self.wards[i] == info:
            # nothing to do
            return

        elif self.wards[i] is not None:
            self._index = None
            self.wards[i] = info
            return

        else:
            self.wards[i] = info

            if self._index is not None:
                index = self._index.get(info, None)

                if index is None or index > i:
                    self._index[info] = i

            return

    def reindex(self):
        """Rebuild the WardInfo index. You must call this function after
           you have modified the list of WardInfo objects, as otherwise
           this will fall out of date. Note that this will be automatically
           called the first time you use the "contains" or "index" functions
        """
        self._index = {}

        for i, ward in enumerate(self.wards):
            if ward is not None:
                if not isinstance(ward, WardInfo):
                    raise TypeError(
                        f"Item at index {i} is not a WardInfo! {ward}")

                if ward not in self._index:
                    self._index[ward] = i

    def __contains__(self, info: WardInfo) -> bool:
        """Return whether or not this contains the passed WardInfo"""
        if self._index is None:
            self.reindex()

        return info in self._index

    def contains(self, info: WardInfo) -> bool:
        """Return whether or not this contains the passed WardInfo"""
        return self.__contains__(info)

    def index(self, info: WardInfo) -> int:
        """Return the index of the passed 'info' object if it is in this
           list. If not, then a ValueError exception is raised. Note that
           only the first matching WardInfo will be returned
        """
        if self._index is None:
            self.reindex()

        i = self._index.get(info, None)

        if i is None:
            raise ValueError(f"Missing ward! {info}")
        else:
            return i

    def _find_ward(self, name: str, match: bool, include_alternates: bool):
        """Internal function that flexibly finds a ward by name"""
        import re

        if not isinstance(name, re.Pattern):
            search = re.compile(name, re.IGNORECASE)
        else:
            search = name

        if match:
            search = search.match
        else:
            search = search.search

        matches = []

        for i, ward in enumerate(self.wards):
            if ward is None:
                continue

            is_match = False

            if search(ward.name):
                is_match = True
            elif search(ward.code):
                is_match = True
            elif include_alternates:
                for alternate in ward.alternate_names:
                    if search(alternate):
                        is_match = True
                        break

                if not is_match:
                    for alternate in ward.alternate_codes:
                        if search(alternate):
                            is_match = True
                            break

            if is_match:
                matches.append(i)

        return matches

    def _find_authority(self, name: str, match: bool):
        """Internal function that flexibly finds a ward by authority"""
        import re

        if not isinstance(name, re.Pattern):
            search = re.compile(name, re.IGNORECASE)
        else:
            search = name

        if match:
            search = search.match
        else:
            search = search.search

        matches = []

        for i, ward in enumerate(self.wards):
            if ward is None:
                continue

            is_match = False

            if search(ward.authority):
                is_match = True
            elif search(ward.authority_code):
                is_match = True

            if is_match:
                matches.append(i)

        return matches

    def _find_region(self, name: str, match: bool):
        """Internal function that flexibly finds a ward by region"""
        import re

        if not isinstance(name, re.Pattern):
            search = re.compile(name, re.IGNORECASE)
        else:
            search = name

        if match:
            search = search.match
        else:
            search = search.search

        matches = []

        for i, ward in enumerate(self.wards):
            if ward is None:
                continue

            is_match = False

            if search(ward.region):
                is_match = True
            elif search(ward.region_code):
                is_match = True

            if is_match:
                matches.append(i)

        return matches

    def _intersect(self, list1, list2):
        """Return the intersection of two lists"""
        return [value for value in list1 if value in list2]

    def find(self, name: str = None,
             authority: str = None, region: str = None,
             match: bool = False, match_authority_and_region: bool = False,
             include_alternates: bool = True):
        """Generic search function that will search using any or all
           of the terms provided. This returns a list of indicies
           of wards that match the search

           Parameters
           ----------
           name: str or regexp
             Name or code of the ward to search. You can also include
             the authority adn region by separating usign "/", e.g.
             "Clifton/Bristol".
           authority: str or regexp
             Name or code of the authority to search
           region: str or regexp
             Name or code of the region to search
           match: bool(False)
             Use a regular expression match for the ward rather than a
             search. This forces the match to be at the start of the string
           match_authority_and_region: bool(False)
             Use a regular expression match for the authority and region
             rather than a search. This forces the match to be at the start
             of the string
           include_alternates: bool(True)
             Whether or not to include alternative names and codes when
             searching for the ward
        """
        wards = None

        if name is not None:
            parts = name.split("/")

            if len(parts) == 1:
                wards = self._find_ward(name, match=match,
                                        include_alternates=include_alternates)
            else:
                wards = self._find_ward(name=parts[0].strip(), match=match,
                                        include_alternates=include_alternates)
                authority = parts[1].strip()

                if len(parts) > 2:
                    region = "/".join(parts[2:]).strip()

            if len(wards) == 0:
                return wards

        if authority is not None:
            authorities = self._find_authority(
                authority,
                match=match_authority_and_region)

            if len(authorities) == 0:
                return authorities

            if wards is None:
                wards = authorities
            else:
                wards = self._intersect(wards, authorities)
                wards.sort()
                if len(wards) == 0:
                    return wards

        if region is not None:
            regions = self._find_region(region,
                                        match=match_authority_and_region)

            if len(regions) == 0:
                return regions

            if wards is None:
                wards = regions
            else:
                wards = self._intersect(wards, regions)
                wards.sort()

        if wards is None:
            # we have not searched for anything, so return everything
            return list(range(1, len(self.wards)))
        else:
            return wards
