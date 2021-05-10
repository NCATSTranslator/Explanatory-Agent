"""
WHAT: A class which generates the query workflow logic
WHY: Removes this logic from the view, and puts in a testable class
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-04-25
"""

from jsonschema import ValidationError
import reasoner_validator
from .clsCaseSolutionManager import clsCaseSolutionManager
from utils.modTextUtils import isNullOrWhiteSpace


class clsQueryManager:
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
        self.caseSolutionManager = None

    def userRequestBodyValidation(self):
        """
        A function to evaluate whether the JSON body received from the client conforms to the proper input standard.
        :return: Boolean: True meaning the body is valid, False meaning the body is not valid
        """
        try:
            reasoner_validator.validate_Query(self.userRequestBody)
            return {"isValid": True, "error": None}
        except ValidationError as e:
            return {"isValid": False, "error": e}

    def userResponseBodyValidation(self):
        """
        A function to evaluate whether the JSON body sent to the client conforms to the proper input standard.
        :return: Boolean: True meaning the body is valid, False meaning the body is not valid
        """
        try:
            reasoner_validator.validate_Response(self.userResponseBody)
            return {"isValid": True, "error": None}
        except ValidationError as e:
            return {"isValid": False, "error": e}

    @property
    def userRequestBodyStructureIsSupported(self):
        """
        A function to evaluate whether the valid response is supported by our api
        :param body: A dictionary representing a JSON body
        :return: Boolean: True meaning our api supports these parameters, False meaning our api does not support these parameters
        """

        # todo, return why the structure isn't supported

        # validate edges in query_graph
        edges = self.userRequestBody['message']['query_graph']['edges']
        if type(edges) != dict: return False
        if len(edges) != 1: return False

        # validate the one edge
        edge = edges[list(edges.keys())[0]]
        if type(edge) != dict: return False

        # define expected keys in edge
        requiredEdgeKeys = ['object', 'predicates', 'subject']
        optionalEdgeKeys = ['constraints']
        allowedEdgeKeys = requiredEdgeKeys + optionalEdgeKeys

        # make sure all required edge keys are present
        for requiredEdgeKey in requiredEdgeKeys:
            if requiredEdgeKey not in list(edge.keys()):
                return False

        # make sure only certain edge keys are present
        for edgeKey in edge:
            if edgeKey not in allowedEdgeKeys:
                return False

        # make sure object and subject keys in edge are valid
        for key in ['object', 'subject']:
            if type(edge[key]) != str: return False
            if isNullOrWhiteSpace(edge[key]): return False

        # make sure object and subject keys in edge aren't the same
        if edge['object'] == edge['subject']: return False

        # make sure predicates in edge are valid
        if type(edge['predicates']) != list: return False
        for predicate in edge['predicates']:
            if type(predicate) != str: return False
            if isNullOrWhiteSpace(predicate): return False

        # validate nodes in query_graph
        nodes = self.userRequestBody['message']['query_graph']['nodes']
        if type(nodes) != dict: return False
        if len(nodes) != 2: return False

        # validate the two nodes
        if edge['object'] not in nodes: return False
        if edge['subject'] not in nodes: return False
        objectNode = nodes[edge['object']]
        subjectNode = nodes[edge['subject']]

        # define expected keys in nodes
        requiredNodeKeys = ['categories']
        optionalNodeKeys = ['constraints', 'ids']
        allowedNodeKeys = requiredNodeKeys + optionalNodeKeys

        for node in [objectNode, subjectNode]:
            if type(node) != dict: return False

            # make sure all required node keys are present
            for requiredNodeKey in requiredNodeKeys:
                if requiredNodeKey not in list(node.keys()):
                    return False

            # make sure only certain node keys are present
            for nodeKey in node:
                if nodeKey not in allowedNodeKeys:
                    return False

            # validate categories
            if type(node['categories']) != list: return False
            for category in node['categories']:
                if type(category) != str: return False
                if isNullOrWhiteSpace(category): return False

            # validate ids if present
            if 'ids' in node:
                if type(node['ids']) != list: return False
                for curieId in node['ids']:
                    if type(curieId) != str: return False
                    if isNullOrWhiteSpace(curieId): return False

        # validate common properties to edge and nodes
        for element in [edge, objectNode, subjectNode]:

            # validate constraints if present
            if 'constraints' in element:
                if type(element['constraints']) != list: return False
                for constraint in element['constraints']:
                    if type(constraint) != dict: return False

        # if everything else passes, its supported
        return True

    def findSupportedCaseSolution(self):
        """
        todo
        :return: None
        """
        self.caseSolutionManager = clsCaseSolutionManager(userRequestBody=self.userRequestBody)
        self.caseSolutionManager.extractMetadataFromUserRequestBody()
        self.caseSolutionManager.findMostSimilarCase()
        self.caseSolutionManager.findCaseSolution()

    @property
    def userRequestBodyCaseIsSupported(self):
        """
        todo
        """
        return self.caseSolutionManager.caseSolution is not None

    def generateSuccessUserResponseBody(self):
        """
        Generate a user response body for a healthy response
        :return: None
        """
        self.userResponseBody = {
            "description": "Success. {} results found".format(len(self.caseSolutionManager.results)),
            "logs": [],
            "status": "Success",
            "message": {
                "query_graph": self.caseSolutionManager.query_graph,
                "knowledge_graph": self.caseSolutionManager.knowledge_graph,
                "results": self.caseSolutionManager.results,
            }
        }

    def generateUnsupportedStructureUserResponseBody(self):
        """
        Generate a user response body for an unsupported structure response (mostly empty)
        :return: None
        """
        self.userResponseBody = {
            "description": "Unsupported query structure.",
            "logs": [],
            "status": "Unsupported",
            "message": {
                "query_graph": self.userRequestBody["message"]["query_graph"],
                "knowledge_graph": {"edges": {}, "nodes": {}},
                "results": [],
            }
        }

    def generateUnsupportedCaseUserResponseBody(self):
        """
        Generate a user response body for an unsupported knowledge provider response (mostly empty)
        :return: None
        """
        self.userResponseBody = {
            "description": "No knowledge provider supports query.",
            "logs": [],
            "status": "Unsupported",
            "message": {
                "query_graph": self.userRequestBody["message"]["query_graph"],
                "knowledge_graph": {"edges": {}, "nodes": {}},
                "results": [],
            }
        }
