"""
WHAT: A query base class to be inherited by other specific queries.
WHY: Need a place for common methods and properties.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-04-25
"""

from abc import ABC, abstractmethod
from collections import OrderedDict
import reasoner_validator


class clsQuery(ABC):
    """
    See header
    """

    def __init__(self, userRequestBody: dict):
        """
        Constructor
        :param userRequestBody: TRAPI user request body
        """
        self.userRequestBody = userRequestBody
        self.userResponseBody = None

        # outputs
        self.query_graph = None
        self.knowledge_graph = None
        self.results = None

    @property
    @abstractmethod
    def predicates(self):
        """
        An abstract property to be overridden to force 'predicates' to be set
        :return: 'predicates' property as a dictionary
        """
        pass

    @property
    @abstractmethod
    def validCuries(self):
        """
        An abstract property to be overridden for force 'validCuries' to be set
        :return: 'validCuries' property as a list
        """
        pass

    @staticmethod
    @abstractmethod
    def userRequestBodyIsSupported():
        """
        A function to evaluate whether the valid response is supported by our api
        :return: Boolean: True meaning our api supports these parameters, False meaning our api does not support these parameters
        """
        pass

    @abstractmethod
    def getDataFromKnowledgeProviders(self):
        """
        An abstract method to execute calls to knowledge providers
        :return: None
        """
        pass

    @abstractmethod
    def populateKnowledgeGraph(self):
        """
        An abstract method to assign data from knowledge provider responses to our knowledge_graph
        :return: None
        """
        pass

    @abstractmethod
    def createResults(self):
        """
        An abstract method to generate results for our response
        :return:
        """
        pass

    def execute(self):
        """
        Execute a group of primary methods together for simplicity
        :return: None
        """
        self.getDataFromKnowledgeProviders()
        self.populateKnowledgeGraph()
        self.createResults()

    @staticmethod
    def buildOneHopRequestBody(node1: dict, node2: dict, edge: dict):
        """
        Builds a TRAPI one hop query message.
        :param node1: node1 dictionary
        :param node2: node2 dictioanry
        :param edge: edge dictionary
        :return:
        """

        requestBody = {
            "message": {
                "query_graph": {
                    "edges": {
                        "e0": {
                            "subject": "n0",
                            "predicate": edge["predicate"],
                            "object": "n1"
                        }
                    },
                    "nodes": {
                        "n0": {
                            "category": node1["category"]
                        },
                        "n1": {
                            "category": node2["category"]
                        }
                    }
                }
            }
        }
        if "id" in node1:
            requestBody["message"]["query_graph"]["nodes"]["n0"]["id"] = node1["id"]
        if "id" in node2:
            requestBody["message"]["query_graph"]["nodes"]["n0"]["id"] = node2["id"]

        # ensure the message is valid before returning it
        reasoner_validator.validate_Query(requestBody)

        return requestBody

    def buildSlimRequestBody(self):
        """
        Generates a request body with only a query_graph as content. Useful for sending to knowledge providers.
        """
        return {
            "message": {
                "query_graph": self.query_graph,
            }
        }

    def createGenericPlaceholderResults(self):
        """
        Generates placeholder results.
        :return: None
        """
        self.results = []
        # sorting for deterministic results. This can go away after index isn't used for rank.
        for index, (knowledgeEdgeId, knowledgeEdge) in enumerate(sorted(list(self.knowledge_graph['edges'].items()), key=lambda i: i[0])):
            result = OrderedDict()
            result['edge_bindings'] = {"e0": [{
                "id": knowledgeEdgeId,
                "Explanatory_Agent_Ranking": index + 1,
                "Explanatory_Agent_Explanation": "TBD"
            }]}
            result['node_bindings'] = {
                "n0": [{"id": knowledgeEdge['subject']}],
                "n1": [{"id": knowledgeEdge['object']}],
            }

            self.results.append(result)
