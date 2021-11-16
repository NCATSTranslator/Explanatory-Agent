"""
WHAT: A class for communicating with the cure ids provider.
WHY: Need to get curie ids for given names.
ASSUMES: None
FUTURE IMPROVEMENTS: See clsKnowledgeProvider for log style
WHO: SL 2021-05-31
"""

from extensions.requests_extension import request_with_global_timeout


class clsCurieIdsProvider:
    """
    See header
    """
    timeoutSeconds = 30

    url = "https://name-resolution-sri.renci.org/lookup"

    def __init__(self, names: list):
        """
        Constructor
        :param names: List of names to get cure ids for
        """
        self.names = sorted(list(set(names)))
        self.curieIds = None

    def getCurieIds(self):
        """
        Method to call the provider via http and get the valid curie ids
        :returns: None
        """

        curieIds = set()
        for name in self.names:
            response = request_with_global_timeout(
                method="post",
                url=self.url,
                # global_timeout=self.timeoutSeconds,
                global_timeout=None,
                params={
                    "string": name,
                    "offset": 0,
                    "limit": 1
                }
            )
            response.raise_for_status()
            responseBody = response.json()
            for curieId, names in responseBody.items():
                curieIds.add(curieId)

        self.curieIds = sorted(list(curieIds))

        if len(self.curieIds) == 0:
            raise AttributeError("No curie ids found for given names")
