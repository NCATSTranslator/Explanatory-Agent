"""
WHAT: A base class for other knowledge providers.
WHY: Need a common class for methods and properties.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-04-25
"""

from abc import ABC, abstractmethod
import requests
import reasoner_validator


class clsKnowledgeProvider(ABC):
    """
    See header
    """

    def __init__(self, requestBody: dict):
        """
        Constructor
        :param requestBody: TRAPI Message JSON object to send to the Knowledge Provider
        """
        self.requestBody = requestBody
        self.responseBody = None

    @property
    @abstractmethod
    def url(self):
        """
        Forcing url property to be set at runtime
        :return: url string
        """
        pass

    def execute(self):
        """
        Sends a query to the Knowledge Provider and sets the responseBody property
        :return: None
        """
        response = requests.post(url=self.url, json=self.requestBody)
        response.raise_for_status()
        self.responseBody = response.json()

    def validate(self):
        """
        Verify its a valid TRAPI response
        :return: None
        :raises: Will raise if not valid
        """
        # todo, Multiomics provider is sending bad TRAPI format!
        reasoner_validator.validate_Query(self.responseBody)
