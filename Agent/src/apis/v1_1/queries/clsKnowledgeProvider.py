"""
WHAT: A class for communicating with knowledge providers.
WHY: Need to separate concerns.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-04-25
"""

import requests
import reasoner_validator
from jsonschema import ValidationError
from datetime import datetime


class clsKnowledgeProvider:
    """
    See header
    """

    def __init__(self, name: str, url: str):
        """
        Constructor
        :param name: Common name of knowledge provider
        :param url: Url to request
        """
        self.name = name
        self.url = url

        self.requestBody = None
        self.responseBody = None

        self.logs = None

    def validateRequestBody(self):
        """
        Verify its a valid TRAPI request
        :return: None
        :raises: Will raise if not valid
        """
        reasoner_validator.validate_Query(self.requestBody)
        # don't log this crash, it's our fault

    def execute(self):
        """
        Sends a query to the Knowledge Provider and sets the responseBody property
        :return: None
        """
        self.validateRequestBody()
        response = requests.post(url=self.url, json=self.requestBody)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            self.logs.append({
                "timestamp": datetime.utcnow().isoformat()[:19],
                "level": "ERROR",
                "code": "KPNotAvailable",
                "message": f"Knowledge Provider {self.url} returned HTTP error code {str(response.status_code)}"
            })
            raise
        self.responseBody = response.json()
        self.validateResponseBody()
        self.checkForEmptyResponseBody()

    def validateResponseBody(self):
        """
        Verify its a valid TRAPI response
        :return: None
        :raises: Will raise InvalidSchema if not valid
        """
        try:
            reasoner_validator.validate_Response(self.responseBody)
        except ValidationError as e:
            self.logs.append({
                "timestamp": datetime.utcnow().isoformat()[:19],
                "level": "ERROR",
                "code": "KPMalformedResponse",
                "message": f"Knowledge Provider {self.url} did not return a valid TRAPI v1.1 response"
            })
            raise requests.exceptions.InvalidSchema  # force raise a request.exception to know its the KP's fault

    def checkForEmptyResponseBody(self):
        """
        Just log if the response body is empty, helpful for the users
        :return: None
        """
        knowledge_graph = self.responseBody['message']['knowledge_graph']
        if len(knowledge_graph['edges']) == 0 or len(knowledge_graph['nodes']) == 0:
            self.logs.append({
                "timestamp": datetime.utcnow().isoformat()[:19],
                "level": "WARNING",
                "code": "KPEmptyResponse",
                "message": f"Knowledge Provider {self.url} returned an empty knowledge graph"
            })
