"""
WHAT: Requests and returns data from a synonyms lookup service.
WHY: Synonyms are needed for explanations.
ASSUMES: None
FUTURE IMPROVEMENTS:
WHO: TZ 2021-09-25
"""

from extensions.requests_extension import request_with_global_timeout


class clsNameResolutionProvider:
    """
    See header
    """
    timeoutSeconds = 30

    url = "https://name-resolution-sri.renci.org/reverse_lookup"

    def __init__(self, curie_ids: list):
        """
        Constructor
        :param curie_ids: List of curie ids to get categories for
        """
        self.curie_ids = sorted(list(set(curie_ids)))
        self.requestBody = {"curies": self.curie_ids}
        self.responseBody = None
        self.synonyms = None

    def get_synonyms(self):
        """
        Gets all synonyms for the curies
        :return: None
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

        self.synonyms = {}
        for curie, synonyms in self.responseBody.items():
            self.synonyms[curie] = synonyms
