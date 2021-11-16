"""
WHAT: A class for communicating with the categories provider.
WHY: Need to get categories for given curie ids.
ASSUMES: None
FUTURE IMPROVEMENTS: See clsKnowledgeProvider for log style
WHO: SL 2021-05-18
"""

from extensions.requests_extension import request_with_global_timeout


class clsCategoriesProvider:
    """
    See header
    """
    timeoutSeconds = 30

    url = "https://nodenormalization-sri.renci.org/1.2/get_normalized_nodes"

    def __init__(self, curieIds: list):
        """
        Constructor
        :param curieIds: List of curie ids to get categories for
        """
        self.curieIds = sorted(list(set(curieIds)))
        self.requestBody = {"curies": self.curieIds}
        self.responseBody = None
        self.categories = None

    def getCategories(self):
        """
        Method to call the provider via http and get the valid categories
        :returns: None
        """

        response = request_with_global_timeout(
            method="post",
            url=self.url,
            # global_timeout=self.timeoutSeconds,
            global_timeout=None,
            json=self.requestBody
        )
        response.raise_for_status()
        self.responseBody = response.json()

        # making sure their response is consistent
        categories = set()
        for curieId in self.curieIds:
            metadata = self.responseBody.get(curieId)
            if metadata is None: continue
            if type(metadata) != dict: continue
            if 'type' not in metadata: continue
            if type(metadata['type']) != list: continue
            if len(metadata['type']) == 0: continue
            if type(metadata['type'][0]) != str: continue
            categories.add(metadata['type'][0])

        self.categories = sorted(list(categories))

        if len(self.categories) == 0:
            raise AttributeError("No categories found for given curie ids")
