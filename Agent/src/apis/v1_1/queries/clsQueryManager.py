"""
WHAT: A class which generates the query workflow logic
WHY: Removes this logic from the view, and puts in a testable class
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: SL 2021-04-25
"""

from jsonschema import ValidationError
import reasoner_validator
from utils.modTextUtils import isNullOrWhiteSpace
from .clsCaseSolutionManager import clsCaseSolutionManager
from .clsCategoriesProvider import clsCategoriesProvider
from .clsCurieIdsProvider import clsCurieIdsProvider
from utils.multithreading.clsNode import clsNode
from copy import deepcopy
from flask import current_app


class clsQueryManager(clsNode):
    """
    See header
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__(dispatchId=-1, dispatchDescription="Query Manager", dispatchMode="parallel", dispatchList=[])
        self.userRequestBody = None
        self.userResponseBody = None
        self.edgePredicates = None
        self.logs = []  # this reference gets set for all children
        self.query_graph = None
        self.knowledge_graph = None
        self.results = None

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
            if requiredEdgeKey not in edge: return False

        # make sure only certain edge keys are present
        for edgeKey in edge:
            if edgeKey not in allowedEdgeKeys: return False

        # make sure object and subject keys in edge are valid
        for key in ['object', 'subject']:
            if type(edge[key]) != str: return False
            if isNullOrWhiteSpace(edge[key]): return False

        # make sure object and subject keys in edge aren't the same
        if edge['object'] == edge['subject']: return False

        # make sure predicates in edge are valid
        if type(edge['predicates']) != list: return False
        if not 1 <= len(list(set(edge['predicates']))) <= 10: return False  # at least 1, max of 10
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
        requiredNodeKeys = []
        optionalNodeKeys = ['constraints', 'names', 'ids', 'categories']
        allowedNodeKeys = requiredNodeKeys + optionalNodeKeys

        for node in [objectNode, subjectNode]:
            if type(node) != dict: return False

            # make sure all required node keys are present
            for requiredNodeKey in requiredNodeKeys:
                if requiredNodeKey not in node: return False

            # make sure only certain node keys are present
            for nodeKey in node:
                if nodeKey not in allowedNodeKeys: return False

            # make sure exclusive node keys don't clash
            if "names" in node:
                if "ids" in node or "categories" in node: return False
            else:
                if "ids" not in node and "categories" not in node: return False

            # validate names if present
            if 'names' in node:
                if type(node['names']) != list: return False
                if len(node['names']) == 0: return False
                for name in node['names']:
                    if type(name) != str: return False
                    if isNullOrWhiteSpace(name): return False

            # validate ids if present
            if 'ids' in node:
                if type(node['ids']) != list: return False
                if len(node['ids']) == 0: return False
                for curieId in node['ids']:
                    if type(curieId) != str: return False
                    if isNullOrWhiteSpace(curieId): return False

            # validate categories
            if 'categories' in node:
                if type(node['categories']) != list: return False
                if len(node['categories']) == 0: return False
                for category in node['categories']:
                    if type(category) != str: return False
                    if isNullOrWhiteSpace(category): return False

        # validate common properties to edge and nodes
        for element in [edge, objectNode, subjectNode]:

            # validate constraints if present
            if 'constraints' in element:
                if type(element['constraints']) != list: return False
                if len(element['constraints']) == 0: return False
                for constraint in element['constraints']:
                    if type(constraint) != dict: return False

        # if everything else passes, its supported
        return True

    def getCurieIds(self):
        """
        A function to get the appropriate curie ids from the names for each node (if applicable)
        :return: None
        """
        for nodeId, node in self.userRequestBody['message']['query_graph']['nodes'].items():
            if 'names' not in node: continue
            curieIdsProvider = clsCurieIdsProvider(names=node['names'])
            curieIdsProvider.getCurieIds()
            node['ids'] = curieIdsProvider.curieIds
            del node['names']  # delete this, otherwise knowledge provider will throw 500

    def getCategories(self):
        """
        A function to get the appropriate categories from the curie ids for each node (if applicable)
        :return: None
        """
        for nodeId, node in self.userRequestBody['message']['query_graph']['nodes'].items():
            if 'categories' in node: continue
            categoriesProvider = clsCategoriesProvider(curieIds=node['ids'])
            categoriesProvider.getCategories()
            node['categories'] = categoriesProvider.categories

    def extractUniqueEdgePredicates(self):
        """
        Reduces duplicate predicates (if any duplicates are present)
        :return: None
        """
        edges = self.userRequestBody['message']['query_graph']['edges']
        edge = edges[list(edges.keys())[0]]
        self.edgePredicates = list(dict.fromkeys(edge['predicates']))  # unique set but preserve order

    def createCaseSolutionManagers(self):
        """
        Create multiple case solutions managers, 1 for each predicate.
        Assigning them to a dispatchList property to run async to improve speed of request.
        :return: None
        """

        for dispatchId, edgePredicate in enumerate(self.edgePredicates):

            # create a deep copy of the user request body
            # override with single edge predicates, 1 at a time
            userRequestBodyCopy = deepcopy(self.userRequestBody)
            edgesCopy = userRequestBodyCopy['message']['query_graph']['edges']
            edgeCopy = edgesCopy[list(edgesCopy.keys())[0]]
            edgeCopy['predicates'] = [edgePredicate]

            # create a case solution manager for each edge predicate
            # use ids as base 10 to help with node and edge id separation
            caseSolutionManager = clsCaseSolutionManager(dispatchId=dispatchId, dispatchDescription=edgePredicate, userRequestBody=userRequestBodyCopy)
            caseSolutionManager.app = current_app._get_current_object()  # pass app by reference
            caseSolutionManager.logs = self.logs  # pass logs by reference
            self.dispatchList.append(caseSolutionManager)

    @property
    def userRequestBodyHasAtLeastOneSupportedCaseSolutionManager(self):
        """
        Property which determines if at least one case solution manager found a solution or not (meaning it was found in the database)
        :return: boolean
        """
        return any(caseSolutionManager.caseSolution is not None for caseSolutionManager in self.dispatchList)

    def mergeCaseSolutionManagers(self):
        """
        Method to merge results across different case solution managers.
        * query_graph is a blind merge using dict.update
            - the keys are controlled so clashing is impossible
        * knowledge_graph is a blind merge using dict.update
            - WARNING the keys are random but UNCONTROLLED from the knowledge providers
            - the keys appear highly randomized so a clash is very unlikely
        * results is a blind merge using list.extend
            - the keys within the list elements are controlled so clashing is impossible
        :return: None
        """

        for caseSolutionManager in self.dispatchList:

            # if the solution wasn't found, skip it
            if caseSolutionManager.caseSolution is None: continue

            # if the properties weren't set yet, then copy the first one found
            if self.query_graph is None and self.knowledge_graph is None and self.results is None:
                self.query_graph = deepcopy(caseSolutionManager.query_graph)
                self.knowledge_graph = deepcopy(caseSolutionManager.knowledge_graph)
                self.results = deepcopy(caseSolutionManager.results)
                continue

            # update for the rest of them
            self.query_graph['edges'].update(deepcopy(caseSolutionManager.query_graph['edges']))
            self.query_graph['nodes'].update(deepcopy(caseSolutionManager.query_graph['nodes']))
            self.knowledge_graph['edges'].update(deepcopy(caseSolutionManager.knowledge_graph['edges']))
            self.knowledge_graph['nodes'].update(deepcopy(caseSolutionManager.knowledge_graph['nodes']))
            self.results.extend(deepcopy(caseSolutionManager.results))

    def generateSuccessUserResponseBody(self):
        """
        Generate a user response body for a healthy response
        :return: None
        """

        self.userResponseBody = {
            "description": f"Success. {len(self.results)} results found",
            "logs": self.logs,
            "status": "Success",
            "message": {
                "query_graph": self.query_graph,
                "knowledge_graph": self.knowledge_graph,
                "results": self.results,
            }
        }

    def generateEmptyUserResponseBody(self, status: str, description: str):
        """
        Generate an empty response body for an unhealthy response
        :return: None
        """
        # this is a hack to make sure we return the users query_graph if its valid
        try:
            query_graph = dict(self.userRequestBody["message"]["query_graph"])
        except Exception as e:
            query_graph = {"edges": {}, "nodes": {}}
            pass

        self.userResponseBody = {
            "description": description,
            "logs": self.logs,
            "status": status,
            "message": {
                "query_graph": query_graph,
                "knowledge_graph": {"edges": {}, "nodes": {}},
                "results": [],
            }
        }
