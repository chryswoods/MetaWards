
from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import List as _List

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


@_dataclass
class WardInfos:
    """Simple class that holds a list of WardInfo objects, and provides
       useful search functions over that list. This prevents me from
       cluttering up the interface of Network
    """
    #: The list of WardInfo objects, one for each ward in order
    wards: _List[WardInfo] = _field(default_factory=list)

    def __len__(self):
        return len(self.wards)

    def __getitem__(self, index):
        return self.wards[index]

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
             Name or code of the ward to search
           authority: str or regexp
             Name or code of the authority to search
           region: str or regexp
             Name or code of the region to search
           match: bool (False)
             Use a regular expression match for the ward rather than a
             search. This forces the match to be at the start of the string
           match_authority_and_region: bool (False)
             Use a regular expression match for the authority and region
             rather than a search. This forces the match to be at the start
             of the string
           include_alternates: bool (True)
             Whether or not to include alternative names and codes when
             searching for the ward
        """
        wards = None

        if name is not None:
            wards = self._find_ward(name, match=match,
                                    include_alternates=include_alternates)

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
