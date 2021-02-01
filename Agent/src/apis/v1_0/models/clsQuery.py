"""
WHAT: A class which handles the logic involved with the clsAgentView
    * validates user request body
    * validates knowledge provider response body
    * applies query_graph from user request body after being validated
    * applies knowledge_graph from the knowledge provider response body after being validated
    * creates the results which maps nodes and edges from the query_graph and knowledge_graph
WHY: Need a class to handle data specific logic outside of clsAgentView to separate concerns
ASSUMES: 'Agent' is short for 'Explanatory Autonomous Relay Agent'
FUTURE IMPROVEMENTS: Speed up generateResults() method
WHO: SL 2020-09-10
"""

from apis.common.utils.modTextUtils import isNullOrWhiteSpace
from collections import OrderedDict
import reasoner_validator
from jsonschema import ValidationError


explanations = {
    0: "Disease-Gene association was not identified to be MAGMA_GENE or INTEGRATED_GENETICS. As such, no explanation can be made.",  # default
    1: "Disease-Gene association was identified via MAGMA_GENE (a standard method for identifying gene-condition associations from variant-level associations using proximity-based assignments from GWAS data) AND was also identified by INTEGRATED_GENETICS (an experimental method for identifying gene-condition associations using a novel combination of established methods). INTEGRATED_GENETICS is still in development and undergoing optimization; false-positives may be present.\nConfirmation of the association with both available methods from this KP gives us high confidence in these results.",
    2: "Disease-Gene association was identified via MAGMA_GENE (a standard method for identifying gene-condition associations from variant-level associations using proximity-based assignments from GWAS data), but was not confirmed by INTEGRATED_GENETICS (an experimental method that for identifying gene-condition associations using a novel combination of established methods).\nINTEGRATED_GENETICS is still in development and undergoing optimization; false-positives may be present. Considering MAGMA_GENE is a standard method in the field, we still maintain acceptable confidence in these results.",
    3: "Disease-Gene association was identified only by INTEGRATED_GENETICS (an experimental method for identifying gene-condition associations using a novel combination of established methods). Results were not confirmed using the standard MAGMA_GENE method.\nINTEGRATED_GENETICS is still in development and undergoing optimization; false-positives may be present. For this reason, we consider these results to be the associations with lowest confidence.",
}


class clsQuery:
    """
    See header
    """

    def __init__(self):
        """
        Constructor
        """

        # don't change these variable names, they are exposed to the client
        self.query_graph = None  # the user supplied information
        self.knowledge_graph = None  # the information retrieved from the outbound api call
        self.results = None  # the created mapping between the query_graph and knowledge_graph

    def generateQueryOnlyMessage(self):
        """
        Generates a message with only a Query Graph as content. Useful for sending to KPs.
        """
        return {
            "message": {
                "query_graph": self.query_graph,
            }
        }

    def generateTRAPIUnsupportedResponse(self):
        return {
            "description": "Unsupported query.",
            "logs": [],
            "status": "Unsupported",
            "message": {
                "query_graph": self.query_graph,
                "knowledge_graph": self.knowledge_graph,
                "results": self.results,
            }
        }

    def generateTRAPISuccessResponse(self):
        return {
            "description": "Success. {} results found".format(len(self.results), ),
            "logs": [],
            "status": "Success",
            "message": {
                "query_graph": self.query_graph,
                "knowledge_graph": self.knowledge_graph,
                "results": self.results,
            }
        }

    @staticmethod
    def userRequestBodyIsValid(body: dict):
        """
        A function to evaluate whether the JSON body received from the client conforms to the proper input standard.
        :param body: A dictionary representing a JSON body
        :return: Boolean: True meaning the body is valid, False meaning the body is not valid
        """

        try:
            reasoner_validator.validate_Query(body)
            return True
        except ValidationError as e:
            return False

    @staticmethod
    def userRequestBodyValidate(body: dict):
        """
        A function to evaluate whether the JSON body received from the client conforms to the proper input standard.
        :param body: A dictionary representing a JSON body
        :return: Boolean: True meaning the body is valid, False meaning the body is not valid
        """

        try:
            reasoner_validator.validate_Query(body)
            return None
        except ValidationError as e:
            return e

    @staticmethod
    def userResponseBodyIsValid(body: dict):
        """
        A function to evaluate whether the JSON body received from the client conforms to the proper input standard.
        :param body: A dictionary representing a JSON body
        :return: Boolean: True meaning the body is valid, False meaning the body is not valid
        """

        try:
            reasoner_validator.validate_Response(body)
            return True
        except Exception as e:
            return False

    @staticmethod
    def knowledgeProviderResponseBodyIsValid(body: dict):
        """
        A function to evaluate whether the JSON body received from the knowledge provider conforms to our assumptions.
        :param body: A dictionary representing a JSON body
        :return: Boolean: True meaning the body is valid, False meaning the body is not valid (the knowledge provider has changed their api!)
        """

        try:
            reasoner_validator.validate_Query(body)
            return True
        except Exception as e:
            return False

    def applyQueryGraphFromUserRequestBody(self, body: dict):
        """
        Assigns a portion of the JSON request body from the client to the query_graph property
        :param body: A dictionary representing a JSON body
        :return: None
        """
        self.query_graph = body['message']['query_graph']

    def applyKnowledgeGraphFromKnowledgeProviderResponseBody(self, body: dict):
        """
        Assigns a portion of the JSON response body from the knowledge provider to the knowledge_graph property
        :param body: A dictionary representing a JSON body
        :return: None
        """
        self.knowledge_graph = body['message']['knowledge_graph']

    def generateTargetIdExplanationCounts(self):
        """
        Generates a dictionary of where the key is a target id and the value is another dictionary with the key as a explanation code and value is the count
        :return: dict
        """
        targetIdExplanationCounts = {}
        for edgeId, knowledgeEdge in self.knowledge_graph['edges'].items():
            targetId = knowledgeEdge['object']
            if targetId not in targetIdExplanationCounts:
                targetIdExplanationCounts[targetId] = {code: 0 for code in explanations.keys()}  # initialize keys with 0 as value
            if edgeId.upper().startswith("MAGMA_GENE"):
                targetIdExplanationCounts[targetId][2] += 1
            elif edgeId.upper().startswith("INTEGRATED_GENETICS"):
                targetIdExplanationCounts[targetId][3] += 1
            else:
                targetIdExplanationCounts[targetId][0] += 1
        return targetIdExplanationCounts

    @staticmethod
    def resolveTargetIdExplanationCount(targetIdExplanationCount: dict):
        """
        Returns the final explanation code based on the observed counts of the target id explanation codes
        :param targetIdExplanationCount: A dictionary representing the key as the explanation code and the value as the observation count
        :return: explanation code as integer
        :raises: Attribute error if it does not resolve
        """
        if targetIdExplanationCount[2] > 0 and targetIdExplanationCount[3] > 0:
            return 1
        elif targetIdExplanationCount[2] > 0:
            return 2
        elif targetIdExplanationCount[3] > 0:
            return 3
        elif targetIdExplanationCount[0] > 0:
            return 0
        else:
            raise AttributeError("Target explanation codes could not resolve for: %s" % str(targetIdExplanationCount))

    def generateResults(self):
        """
        Creates the results which maps nodes and edges from the query_graph and knowledge_graph.
        This is in-lieu of the results given by the knowledge provider, those are discarded.
        :return: None
        """
        targetIdExplanationCounts = self.generateTargetIdExplanationCounts()

        self.results = []
        for knowledgeEdgeId, knowledgeEdge in self.knowledge_graph['edges'].items():
            explanationCode = self.resolveTargetIdExplanationCount(targetIdExplanationCounts[knowledgeEdge['object']])

            result = OrderedDict()
            result['edge_bindings'] = {"e00": [{
                "id": knowledgeEdgeId,
                "Explanatory_Agent_Ranking": explanationCode,
                "Explanatory_Agent_Explanation": explanations[explanationCode]

            }]}
            result['node_bindings'] = {
                "n00": [{"id": knowledgeEdge['subject']}],
                "n01": [{"id": knowledgeEdge['object']}],
            }

            self.results.append(result)

    def generateEmptyKnowledgeGraph(self):
        """
        Generates an empty knowledge graph for when the userRequestBody is valid but not supported by our api
        :return: None
        """
        self.knowledge_graph = {"edges": {}, "nodes": {}}

    def generateEmptyResults(self):
        """
        Generates an empty results for when the userRequestBody is valid but not supported by our api
        :return: None
        """
        self.results = []

    @staticmethod
    def build_one_hop_query(node_1, node_2, edge):
        """
        Builds a TRAPI one hop query message.
        """

        message = {
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
                            "category": node_1["category"]
                        },
                        "n1": {
                            "category": node_2["category"]
                        }
                    }
                }
            }
        }
        if "id" in node_1:
            message["message"]["query_graph"]["nodes"]["n0"]["id"] = node_1["id"]
        if "id" in node_2:
            message["message"]["query_graph"]["nodes"]["n0"]["id"] = node_2["id"]

        # ensure the message is valid before returning it
        reasoner_validator.validate_Query(message)

        return message
