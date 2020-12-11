"""
WHAT: A class which super-sets a standard python dictionary.
      It it allows the keys to be accessed case-insensitive.
      For example, if keys 'A' and 'a' both exist, you can access only one of them (inconsistently) with either 'A' or 'a'.
      This inconsistency is acceptable because if a case-insensitivity exists, the values will be the same for this application.
      This inconsistency should be carefully considered if trying to port this class to another application.
      Idea taken from https://stackoverflow.com/questions/3296499/case-insensitive-dictionary-search
WHY: The multiple replacement algorithm has been adapted for case-insensitivity
ASSUMES: If a duplicate key occurs like 'A' and 'a', their values returned are NOT consistent when accessing via 'A' or 'a'.
         It's only acceptable because the values returned are the same in this problem.
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-13
"""

import collections


class clsCaseInsensitiveDictionary(collections.Mapping):
    """
    See header
    """

    def __init__(self, d):
        self._d = d
        self._s = dict((k.lower(), k) for k in d)

    def __contains__(self, k):
        return k.lower() in self._s

    def __len__(self):
        return len(self._s)

    def __iter__(self):
        return iter(self._s)

    def __getitem__(self, k):
        return self._d[self._s[k.lower()]]

    def actual_key_case(self, k):
        return self._s.get(k.lower())
