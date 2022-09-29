"""
WHAT: Requests and returns data from a node identifier lookup service.
WHY: Common identifiers are used for synonym lookups which are used in explanations.
ASSUMES: None
FUTURE IMPROVEMENTS:
WHO: TZ 2021-11-05
"""

from extensions.requests_extension import request_with_global_timeout
import logging


class clsNodeNormalizerProvider:
    """
    See header
    """
    timeoutSeconds = 30

    url = "https://nodenormalization-sri.renci.org/1.3/get_normalized_nodes"

    def __init__(self, curie_ids: list):
        """
        Constructor
        :param curie_ids: List of curie ids to get identifiers for
        """
        self.curie_ids = sorted(list(set(curie_ids)))
        self.requestBody = {"curies": self.curie_ids}
        self.responseBody = None
        self.identifiers = None

    def get_identifiers(self):
        """
        Gets identifiers for the curies
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

        self.identifiers = {}
        for curie, normalized_data in self.responseBody.items():
            if normalized_data is None:
                logging.info(f"CURIE '{curie}' did not return data.")
                normalized_data = {"id": {"identifier": curie}}
            identifier_data = normalized_data.get("id", {})
            identifier = identifier_data.get("identifier", "")
            if identifier == "":
                logging.info(f"CURIE '{curie}' did not return an identifier.")
                identifier = curie
            self.identifiers[curie] = identifier
