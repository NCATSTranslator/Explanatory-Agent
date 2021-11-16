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
from utils.modMiscUtils import isNullOrEmptyList
from .clsCaseSolutionManager import clsCaseSolutionManager
from .clsCategoriesProvider import clsCategoriesProvider
from .clsCurieIdsProvider import clsCurieIdsProvider
from utils.multithreading.clsNode import clsNode
from copy import deepcopy
from flask import current_app
import time
from copy import deepcopy
from itertools import product
from utils.multithreading.modDispatcher import query_dispatch
from ..modSettings import version, trapi_version
from utils.clsLog import clsLogEvent
from .clsBioLinkSimilarity import clsBiolinkSimilarity
from .clsExplanationSolutionFinder import ExplanationSolutionFinder


class clsQueryManager(clsNode):
    """
    See header
    """
    dispatchIdScaleFactor = 100

    def __init__(self):
        """
        Constructor
        """
        # super().__init__(dispatchId=-1, dispatchDescription="Query Manager", dispatchMode="serial", dispatchList=[])
        super().__init__(dispatchId=-1, dispatchDescription="Query Manager", dispatchMode="parallel", dispatchList=[])
        self.userRequestBody = None
        self.userResponseBody = None
        self.edgePredicates = None
        self.logs = []  # this reference gets set for all children

        self.caseSolutions = None

        self.query_graph = None
        self.batch_query_graphs = None
        self.knowledge_graph = None
        self.results = None
        # start a clock to determine when solutions should be aborted
        self.started_time = time.time()
        # time allowed to process all cases before the remaining are cancelled and results are merged
        self.processing_timeout = 3.0 * 60

    def userRequestBodyValidation(self):
        """
        A function to evaluate whether the JSON body received from the client conforms to the proper input standard.
        :return: Boolean: True meaning the body is valid, False meaning the body is not valid
        """
        try:
            # reasoner_validator.validate_Query(self.userRequestBody)
            reasoner_validator.validate(self.userRequestBody, "Query", trapi_version)
            return {"isValid": True, "error": None}
        except ValidationError as e:
            return {"isValid": False, "error": e}

    def userResponseBodyValidation(self):
        """
        A function to evaluate whether the JSON body sent to the client conforms to the proper input standard.
        :return: Boolean: True meaning the body is valid, False meaning the body is not valid
        """
        validity_status = {"isValid": True, "error": None}

        # ensure all edge attribute lists end with the Explanatory Agent provenance attribute
        try:
            if self.userResponseBody['message']['knowledge_graph'] and "edges" in self.userResponseBody['message']['knowledge_graph']:
                for edge_id, edge in self.userResponseBody['message']['knowledge_graph']['edges'].items():
                    last_attribute = edge['attributes'][-1]
                    assert last_attribute["attribute_type_id"] == "biolink:aggregator_knowledge_source", "Edge missing xARA provenance data"
                    assert last_attribute["attribute_source"] == "infores:explanatory-agent", "Edge missing xARA provenance data"
        except AssertionError as e:
            self.logs.append(clsLogEvent(identifier="", level="DEBUG", code="", message=f"Provenance assertion failure: {e}").dict())
            # validity_status = {"isValid": False, "error": e}
        except Exception as e:
            self.logs.append(clsLogEvent(identifier="", level="DEBUG", code="", message=f"Provenance assertion failure: {e}").dict())

        try:
            reasoner_validator.validate(self.userResponseBody, "Response", trapi_version)
        except ValidationError as e:
            validity_status = {"isValid": False, "error": e}

        return validity_status

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
        # if len(edges) != 1: return False

        # validate the one edge
        edge = edges[list(edges.keys())[0]]
        if type(edge) != dict: return False

        # define expected keys in edge
        requiredEdgeKeys = ['object', 'subject']
        optionalEdgeKeys = ['constraints']
        allowedEdgeKeys = requiredEdgeKeys + optionalEdgeKeys

        # make sure all required edge keys are present
        for requiredEdgeKey in requiredEdgeKeys:
            if requiredEdgeKey not in edge: return False

        # make sure only certain edge keys are present
        # 2021-09-28 disabling all strict requirements
        # for edgeKey in edge:
        #     if edgeKey not in allowedEdgeKeys: return False

        # make sure object and subject keys in edge are valid
        for key in ['object', 'subject']:
            if type(edge[key]) != str: return False
            if isNullOrWhiteSpace(edge[key]): return False

        # make sure object and subject keys in edge aren't the same
        if edge['object'] == edge['subject']: return False

        # make sure predicates in edge are valid
        if "predicates" in edge and type(edge["predicates"]) == list:
            if type(edge['predicates']) != list: return False
            if not 1 <= len(list(set(edge['predicates']))) <= 10: return False  # at least 1, max of 10
            for predicate in edge['predicates']:
                if type(predicate) != str: return False
                if isNullOrWhiteSpace(predicate): return False

        # validate nodes in query_graph
        nodes = self.userRequestBody['message']['query_graph']['nodes']
        if type(nodes) != dict: return False
        # if len(nodes) != 2: return False

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
            # 2021-09-28 disabling all strict requirements
            # for nodeKey in node:
            #     if nodeKey not in allowedNodeKeys: return False

            # make sure exclusive node keys don't clash
            # if "names" in node:
            #     if "ids" in node or "categories" in node: return False
            # else:
            #     if "ids" not in node and "categories" not in node: return False

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
        # for element in [edge, objectNode, subjectNode]:
        #
        #     # validate constraints if present
        #     if 'constraints' in element:
        #         if type(element['constraints']) != list: return False
        #         if len(element['constraints']) == 0: return False
        #         for constraint in element['constraints']:
        #             if type(constraint) != dict: return False

        # if everything else passes, its supported
        return True

    def getCurieIds(self):
        """
        A function to get the appropriate curie ids from the names for each node (if applicable)
        :return: None
        """
        for nodeId, node in self.userRequestBody['message']['query_graph']['nodes'].items():
            if 'names' not in node and 'name' not in node: continue
            if 'names' in node:
                curieIdsProvider = clsCurieIdsProvider(names=node['names'])
            elif 'name' in node:
                curieIdsProvider = clsCurieIdsProvider(names=[node['name']])
            else:
                continue
            curieIdsProvider.getCurieIds()
            node['ids'] = curieIdsProvider.curieIds
            # del node['names']  # delete this, otherwise knowledge provider will throw 500

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

    def deriveQueryPaths(self):
        """
        Splits apart the query graph into multiples so a query path can be created.
        Voc P 3 Step 4, 4a, 4b

        IF there are batch node categories and batch node names:  
         for each batch node category create a new qg q' (ignore names) 
        ELSEIF there are batch node categories and batch node ids:  
         for each batch node id create a new qg q' (ignore categories)
         ELSEIF there are batch node names and batch node ids:  
         for each batch node id create a new qg q' (ignore names) 
        ELSEIF there is a batch in only one entity (name, id, or category): 
         for each batch node entity create a new qg q'  

        :return:
        """
        query_graph = self.userRequestBody['message']['query_graph']

        def node_generator(node_id, node_data):
            if "names" in node_data and len(node_data["names"]) > 1 and len(node_data["categories"]) > 1:
                for category in node_data["categories"]:
                    new_node = deepcopy(node_data)
                    new_node["categories"] = [category]
                    yield node_id, new_node
            elif "ids" in node_data and len(node_data["ids"]) > 1 and len(node_data["categories"]) > 1:
                for curie in node_data["ids"]:
                    new_node = deepcopy(node_data)
                    new_node["ids"] = [curie]
                    yield node_id, new_node
            elif "names" in node_data and len(node_data["names"]) > 1 and "ids" in node_data and len(node_data["ids"]) > 1:
                for curie in node_data["ids"]:
                    new_node = deepcopy(node_data)
                    new_node["ids"] = [curie]
                    yield node_id, new_node
            elif "names" in node_data and len(node_data["names"]) > 1:
                for name in node_data["names"]:
                    new_node = deepcopy(node_data)
                    new_node["names"] = [name]
                    yield node_id, new_node
            elif "categories" in node_data and len(node_data["categories"]) > 1:
                for category in node_data["categories"]:
                    new_node = deepcopy(node_data)
                    new_node["categories"] = [category]
                    yield node_id, new_node
            elif "ids" in node_data and len(node_data["ids"]) > 1:
                for curie in node_data["ids"]:
                    new_node = deepcopy(node_data)
                    new_node["ids"] = [curie]
                    yield node_id, new_node
            else:
                yield node_id, node_data

        def edge_generator(edge_id, edge_data):
            if "predicates" not in edge_data:
                edge_data["predicates"] = ["ANY"]

            if edge_data["predicates"] is None or len(edge_data["predicates"]) == 0:
                edge_data["predicates"] = ["ANY"]

            for predicate in edge_data["predicates"]:
                new_edge = deepcopy(edge_data)
                new_edge["predicates"] = [predicate]
                yield edge_id, new_edge

        args = [node_generator(node_id, node_data) for node_id, node_data in query_graph["nodes"].items()]
        node_lists = list(product(*args))

        args = [edge_generator(edge_id, edge_data) for edge_id, edge_data in query_graph["edges"].items()]
        edge_lists = list(product(*args))

        batch_query_graphs = []
        for node_list in node_lists:
            for edge_list in edge_lists:
                query_graph = {
                    "nodes": dict(node_list),
                    "edges": dict(edge_list),
                }
                batch_query_graphs.append(query_graph)

        self.batch_query_graphs = batch_query_graphs

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

        app = current_app._get_current_object()
        # use the same searcher class across all solution managers
        # case_problem_searcher = clsBiolinkSimilarity.instance()
        # if clsBiolinkSimilarity.instance().app is None:
        #     clsBiolinkSimilarity.instance().app = current_app._get_current_object()
        case_problem_searcher = clsBiolinkSimilarity(app)
        explanation_solution_finder = ExplanationSolutionFinder(app)

        for dispatchId, query_graph in enumerate(self.batch_query_graphs):

            # create a deep copy of the user request body
            # override with single edge predicates, 1 at a time
            userRequestBodyCopy = deepcopy(self.userRequestBody)
            userRequestBodyCopy["query_graph"] = query_graph
            # edgesCopy = userRequestBodyCopy['message']['query_graph']['edges']
            # edgeCopy = edgesCopy[list(edgesCopy.keys())[0]]
            # edgeCopy['predicates'] = [edgePredicate]

            # create a case solution manager for each edge predicate
            # use base 100 to create separation for children case solutions
            caseSolutionManager = clsCaseSolutionManager(
                dispatchId=dispatchId * self.dispatchIdScaleFactor,
                dispatchDescription=query_graph,
                userRequestBody=userRequestBodyCopy
            )
            caseSolutionManager.app = current_app._get_current_object()  # pass app by reference
            caseSolutionManager.initialize_db_data()
            caseSolutionManager.case_problem_searcher = case_problem_searcher
            caseSolutionManager.explanation_solution_finder = explanation_solution_finder

            # caseSolutionManager.logs = self.logs  # pass logs by reference
            caseSolutionManager.logs = []  # each manager has its own log
            self.dispatchList.append(caseSolutionManager)

    def dispatch(self):
        if self.dispatchList is not None:
            self.logs.append(clsLogEvent(
                identifier="",
                level="DEBUG",
                code="",
                message=f"Executing {len(self.dispatchList)} predicate searches."
            ))

            query_dispatch(
                objects=self.dispatchList,
                method=self.dispatchMode,
                parentId=self.dispatchId,
                abort_time=int(self.started_time + self.processing_timeout)
            )

            # all solution managers have identified case solutions to use, now we aggregate and dispatch those
            self.caseMultiHops = []
            for case_solution_manager in self.dispatchList:
                # also merge any logs
                self.logs += case_solution_manager.logs

                if case_solution_manager.dispatchList:
                    self.caseMultiHops += case_solution_manager.dispatchList
            # self.caseMultiHops = self.caseMultiHops[:5]
            # test_solutions = [c for c in self.caseSolutions if c.caseId == 'Q000391' and c.id == 2065]  # Solution ID '2065' for Case ID 'Q000391'
            # self.caseMultiHops = [c for c in self.caseMultiHops if c.caseId != 'Q001884'][:10] + test_solutions
            # self.caseMultiHops = test_solutions

            # self.caseSolutions = self.caseSolutions[:200]

            # self.logs.append(clsLogEvent(
            #     identifier="",
            #     level="DEBUG",
            #     code="",
            #     message=f"Matched {len(self.caseSolutions)} Case Solutions."
            # ))

            query_dispatch(
                objects=self.caseMultiHops,
                method=self.dispatchMode,
                parentId=self.dispatchId,
                abort_time=int(self.started_time + self.processing_timeout),
                # abort_time=10,
                pool_size=5
            )

            self.logs.append(clsLogEvent(
                identifier="",
                level="DEBUG",
                code="",
                message=f"Fully ran {len([s for s in self.caseMultiHops if s.finished])} Case Solutions."
            ))

            return

    @property
    def userRequestBodyHasAtLeastOneSupportedCaseSolution(self):
        """
        Property which determines if at least one case solution manager found a solution or not (meaning it was found in the database)
        :return: boolean
        """
        if isNullOrEmptyList(self.dispatchList): return False
        for caseSolutionManager in self.dispatchList:
            if caseSolutionManager is None: continue
            if isNullOrEmptyList(caseSolutionManager.dispatchList): continue
            for caseSolution in caseSolutionManager.dispatchList:
                if caseSolution is not None: return True
        return False

    def mergeCaseSolutions(self):
        """
        Merges all finished solutions into one TRAPI response. Finished solution includes solutions that errored out!
        """

        # Query graph is the submitted QG unless derived case solutions were used. In that case the query graph is the one used by the derived cases.
        self.query_graph = deepcopy(self.userRequestBody["message"]["query_graph"])
        for multi_hop in self.caseMultiHops:
            if len(multi_hop.case_solutions) == 1 and multi_hop.case_solutions[0].derived is True and multi_hop.case_solutions[0].query_graph:
                self.query_graph = deepcopy(multi_hop.case_solutions[0].query_graph)

        all_cases_unsuccessful = True
        for multi_hop in self.caseMultiHops:
            # add the logs to the final log list
            self.logs += multi_hop.logs

            # if the solution was able to fully execute, even with errors.
            if multi_hop.finished:
                # only include successful solution results
                if multi_hop.successful:
                    all_cases_unsuccessful = False
                    # if the properties weren't set yet, then copy the first one found
                    if self.knowledge_graph is None and self.results is None:
                        self.knowledge_graph = deepcopy(multi_hop.knowledge_graph)
                        self.results = deepcopy(multi_hop.results)
                        continue

                    self.knowledge_graph['edges'].update(deepcopy(multi_hop.knowledge_graph['edges']))
                    self.knowledge_graph['nodes'].update(deepcopy(multi_hop.knowledge_graph['nodes']))
                    self.results.extend(deepcopy(multi_hop.results))

        if all_cases_unsuccessful:
            self.query_graph = deepcopy(self.userRequestBody["message"]["query_graph"])
            self.knowledge_graph = {'nodes': {}, 'edges': {}}
            self.results = []

        # delete all predicates with the value "ANY", as that is our own internal special case
        for edge_id, edge in self.query_graph["edges"].items():
            if "ANY" in edge["predicates"]:
                del edge["predicates"]

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
            # if no solutions were found for that solution manager, skip it
            if isNullOrEmptyList(caseSolutionManager.dispatchList): continue

            # iterate case solutions
            for caseSolution in caseSolutionManager.dispatchList:

                # if the properties weren't set yet, then copy the first one found
                if self.query_graph is None and self.knowledge_graph is None and self.results is None:
                    self.query_graph = deepcopy(caseSolution.query_graph)
                    self.knowledge_graph = deepcopy(caseSolution.knowledge_graph)
                    self.results = deepcopy(caseSolution.results)
                    continue

                # update for the rest of them
                self.query_graph['edges'].update(deepcopy(caseSolution.query_graph['edges']))
                self.query_graph['nodes'].update(deepcopy(caseSolution.query_graph['nodes']))
                self.knowledge_graph['edges'].update(deepcopy(caseSolution.knowledge_graph['edges']))
                self.knowledge_graph['nodes'].update(deepcopy(caseSolution.knowledge_graph['nodes']))
                self.results.extend(deepcopy(caseSolution.results))

    # def appendProvenance(self):
    #     """
    #     DONE IN CaseSolution NOW
    #     Adds an additional attribute to all Knowledge Graph nodes denoting they came from this agent.
    #     :return:
    #     """
    #     if self.knowledge_graph and "edges" in self.knowledge_graph:
    #         for edge_id, edge in self.knowledge_graph["edges"].items():
    #             if "attributes" not in edge:
    #                 edge["attributes"] = []
    #             edge["attributes"].append({
    #                 "attribute_type_id": "biolink:aggregator_knowledge_source",
    #                 "value": "infores:explanatory-agent",
    #                 "value_type_id": "biolink:InformationResource",
    #                 "value_url":  f"https://explanatory-agent.azurewebsites.net/{version}",
    #                 "description": "The eXplanatory Autonomous Relay Agent (xARA) utilizes a case-based reasoning approach to execute ARS queries by obtaining results from multiple knowledge providers (KPs) and utilizes various methods such as natural language understanding models that traverse biomedical literature to score and explain its scores.",
    #                 "attribute_source": "infores:explanatory-agent"
    #             })

    def formatLog(self):
        """

        :return:
        """
        self.logs = [log.dict() for log in self.logs]

    def generateSuccessUserResponseBody(self):
        """
        Generate a user response body for a healthy response
        :return: None
        """

        results_count = 0
        if self.results:
            results_count = len(self.results)

        self.userResponseBody = {
            "description": f"Success. {results_count} results found",
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
