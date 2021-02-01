"""
WHAT: Queries the Genetics Provider and returns results.
WHY: Genetics Provider provides data such as genes associated with a disease, which is used in some of the Agent's cases.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: TZ 2021-01-27
"""

import requests
import reasoner_validator


class MultiomicsProvider:
    url = "https://api.bte.ncats.io/v1/smartapi/adf20dd6ff23dfe18e8e012bde686e31/query"

    def __init__(self):
        pass

    def query(self, query: dict):
        """
        Sends a query to the Genetics Provider.
        :param query: TRAPI Message JSON object to send to the Genetics Provider
        :return: Query object of the response.
        """
        try:
            response = requests.post(url=MultiomicsProvider.url, json=query)
            response.raise_for_status()
        except Exception as e:
            raise e

        # verify it is a TRAPI response
        try:
            trapi_response = response.json()
            # Multiomics provider is sending bad TRAPI format!
            # reasoner_validator.validate_Query(trapi_response)
        except Exception as e:
            raise e

        return trapi_response
