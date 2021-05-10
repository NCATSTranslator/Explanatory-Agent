"""
WHAT: A base class for other knowledge providers.
WHY: Need a common class for methods and properties.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-04-25
"""

import requests
import reasoner_validator
from apis.v1_0 import reasoner_validator as reasoner_validator_v1_0
from copy import deepcopy


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

        self.requestBody_v1_0 = None
        self.responseBody_v1_0 = None

    def downgradeRequestBody(self):
        #todo, shit hack
        edgesCopy = deepcopy(self.requestBody['message']['query_graph']['edges'])
        nodesCopy = deepcopy(self.requestBody['message']['query_graph']['nodes'])
        self.requestBody_v1_0 = deepcopy(self.requestBody)

        self.requestBody_v1_0['message']['query_graph']['edges']['e00']['predicate'] = edgesCopy['e00']['predicates'][0]
        del self.requestBody_v1_0['message']['query_graph']['edges']['e00']['predicates']

        self.requestBody_v1_0['message']['query_graph']['nodes']['n00']['category'] = nodesCopy['n00']['categories'][0]
        del self.requestBody_v1_0['message']['query_graph']['nodes']['n00']['categories']

        self.requestBody_v1_0['message']['query_graph']['nodes']['n01']['category'] = nodesCopy['n01']['categories'][0]
        del self.requestBody_v1_0['message']['query_graph']['nodes']['n01']['categories']

        if "ids" in self.requestBody_v1_0['message']['query_graph']['nodes']['n00']:
            self.requestBody_v1_0['message']['query_graph']['nodes']['n00']['id'] = nodesCopy['n00']['ids'][0]
            del self.requestBody_v1_0['message']['query_graph']['nodes']['n00']['ids']

        if "ids" in self.requestBody_v1_0['message']['query_graph']['nodes']['n01']:
            self.requestBody_v1_0['message']['query_graph']['nodes']['n01']['id'] = nodesCopy['n01']['ids'][0]
            del self.requestBody_v1_0['message']['query_graph']['nodes']['n01']['ids']

    def upgradeResponseBody(self):
        # todo, shit hack
        self.responseBody = deepcopy(self.responseBody_v1_0)
        del self.responseBody['message']['query_graph']
        self.responseBody['message']['query_graph'] = deepcopy(self.requestBody['message']['query_graph'])

    def validateRequestBody(self):
        """
        Verify its a valid TRAPI request
        :return: None
        :raises: Will raise if not valid
        """
        # todo, Multiomics provider is sending bad TRAPI format!
        reasoner_validator.validate_Query(self.requestBody)
        # reasoner_validator_v1_0.validate_Query(self.requestBody_v1_0)

    def execute(self):
        """
        Sends a query to the Knowledge Provider and sets the responseBody property
        :return: None
        """
        # self.downgradeRequestBody()
        self.validateRequestBody()
        # response = requests.post(url=self.url, json=self.requestBody_v1_0)
        response = requests.post(url=self.url, json=self.requestBody)
        response.raise_for_status()
        # self.responseBody_v1_0 = response.json()
        self.responseBody = response.json()
        # self.upgradeResponseBody()
        self.validateResponseBody()

    def validateResponseBody(self):
        """
        Verify its a valid TRAPI response
        :return: None
        :raises: Will raise if not valid
        """
        # todo, Multiomics provider is sending bad TRAPI format!
        # reasoner_validator.validate_Query(self.responseBody)
        # reasoner_validator_v1_0.validate_Query(self.responseBody_v1_0)
        pass
