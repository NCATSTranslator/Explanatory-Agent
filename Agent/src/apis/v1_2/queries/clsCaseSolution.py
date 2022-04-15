from copy import deepcopy
from collections import OrderedDict
import networkx
from utils.multithreading.clsElement import clsElement
from utils.clsLog import clsLogEvent
from .clsExplanationSolutionFinder import ExplanationSolutionFinder
from ..modSettings import version
from utils.multithreading.modDispatcher import runner
from .clsMultiHop import clsMultiHop
import random
import string
import json
import traceback
from requests.exceptions import HTTPError
from ..modSettings import submitter


class clsCaseSolution(clsElement):
    def __init__(self, dispatchId: int, dispatchDescription: str):
        super().__init__(dispatchId=dispatchId, dispatchDescription=dispatchDescription)
        self.id = None  # the auto-increment id in the table
        self.caseId = None  # the string representation of a case id
        self.paths = None  # list of length 1 or 2
        # Case Solutions to run for each path to allow for explanations
        self.path_solutions = None
        self.explanation_solution_finder = None

        self.subject_query_graph_node_id = None
        self.object_query_graph_node_id = None
        self.predicate_query_graph_edge_id = None

        self.subjectCurieIds = None
        self.objectCurieIds = None

        self.edgeConstraints = None
        self.subjectConstraints = None
        self.objectConstraints = None

        # The subject, object, and predicate the case is trying to answer
        self.similarSubject = None
        self.similarObject = None
        self.similarPredicate = None

        # output
        self.query_graph = None
        self.knowledge_graph = None
        self.results = None

        # helper knowledge_graph for merging
        self.networkx_knowledge_graph = None

        self.logs = None

        self.dispatchIdSuffix = None

        self.explanation_similarity = 0.8
        self.explanation_case_solution = None

        # Finished if all attempts have been made, even if errors occurred.
        self.finished = False
        # Successful when all KPs have returned data, there were no errors, and the results were generated.
        self.successful = False

    def __repr__(self):
        return f"Case Solution: {self.id} Case ID: {self.caseId}"

    @property
    def derived(self):
        return len(self.paths) >= 2

    def execute(self, no_results=False):
        self.logs.append(clsLogEvent(
            identifier=self.id,
            level="DEBUG",
            code="",
            message=f"Executing Solution ID '{self.id}' for Case ID '{self.caseId}'"
        ))
        try:
            if len(self.paths) == 1:
                self.generateQueryGraphForOnePath()
                self.generateKnowledgeGraphForOnePath()
                # if no_results is False:
                #     self.generateResultsForOnePath()
                # else:
                #     self.results = []
            elif len(self.paths) == 2:
                self.createCaseSolutions()
                self.generateKnowledgeGraphForTwoPaths()
                self.generateQueryGraphForTwoPaths()
                # if no_results is False:
                #     self.generateResultsForTwoPaths()
                # else:
                #     self.results = []
            else:
                raise AttributeError("Number of knowledge provider paths supported is either 1 or 2")
            edges = sorted(list(self.knowledge_graph["edges"].keys()))
            self.logs.append(clsLogEvent(
                identifier=self.id,
                level="DEBUG",
                code="",
                message=f"Case executed successfully. KP: {self.paths[0].knowledgeProvider.name}({self.paths[0].knowledgeProvider.url}) Query: {self.paths[0].knowledgeProvider.requestBody} Found {len(edges)} edges: {edges}"
            ))
            # if no_results is False and len(self.knowledge_graph["edges"]) > 0 and len(self.results) == 0:
            #     raise AssertionError(f"Results were not generated for solution ID {self.id}.")
            self.successful = True
        except HTTPError as e:
            self.logs.append(clsLogEvent(
                identifier=self.id,
                level="ERROR",
                code="Error",
                message=f"{type(e).__name__} Exception: {e}"
            ))
            self.knowledge_graph = {"nodes": {}, "edges": {}}
            if len(self.paths) == 1:
                self.generateQueryGraphForOnePath()
        except Exception as e:
            print(traceback.format_exc())
            self.logs.append(clsLogEvent(
                identifier=self.id,
                level="ERROR",
                code="Error",
                message=f"Unhandled {type(e).__name__} Exception: {e}"
            ))
            raise e
        finally:
            self.updateKnowledgeProviderLogs()
            self.finished = True

    def generate_results(self):
        if len(self.paths) == 1:
            self.generateResultsForOnePath()
        elif len(self.paths) == 2:
            self.generateResultsForTwoPaths()
        else:
            self.results = []

    @property
    def nominalKnowledgeProviderRequestBody(self):
        return {
            "message": {
                "query_graph": {
                    "edges": {
                        self.predicate_query_graph_edge_id: {
                            "subject": self.subject_query_graph_node_id,
                            "predicates": None,
                            "object": self.object_query_graph_node_id
                        }
                    },
                    "nodes": {
                        self.subject_query_graph_node_id: {
                            "categories": None
                        },
                        self.object_query_graph_node_id: {
                            "categories": None
                        }
                    }
                }
            },
            "submitter": submitter
        }

    def generateKnowledgeGraphForOnePath(self):
        self.paths[0].knowledgeProvider.requestBody = deepcopy(self.nominalKnowledgeProviderRequestBody)
        self.paths[0].knowledgeProvider.requestBody['message']['query_graph'] = deepcopy(self.query_graph)
        # self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['edges'][self.predicate_query_graph_edge_id]['predicates'] = [self.paths[0].predicate]
        # self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][self.subject_query_graph_node_id]['categories'] = [self.paths[0].subject]
        # self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][self.object_query_graph_node_id]['categories'] = [self.paths[0].object]
        #
        # if self.subjectCurieIds is not None:
        #     self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][self.subject_query_graph_node_id]['ids'] = deepcopy(self.subjectCurieIds)
        # if self.objectCurieIds is not None:
        #     self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][self.object_query_graph_node_id]['ids'] = deepcopy(self.objectCurieIds)
        #
        # if self.subjectConstraints is not None:
        #     self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][self.subject_query_graph_node_id]['constraints'] = deepcopy(self.subjectConstraints)
        # if self.objectConstraints is not None:
        #     self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][self.object_query_graph_node_id]['constraints'] = deepcopy(self.objectConstraints)
        # if self.edgeConstraints is not None:
        #     self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['edges'][self.predicate_query_graph_edge_id]['constraints'] = deepcopy(self.edgeConstraints)

        self.paths[0].knowledgeProvider.execute()

        self.knowledge_graph = deepcopy(self.paths[0].knowledgeProvider.responseBody['message']['knowledge_graph'])

        # adding knowledge provider to the edge of the knowledge_graph
        # adding unique identifier to each edge, as some KPs do not
        new_edges = {}
        for edgeId, edge in self.knowledge_graph['edges'].items():
            new_edge_id = f"{edgeId}-{''.join(random.choice(string.ascii_lowercase) for _ in range(10))}"

            if "attributes" not in edge:
                edge["attributes"] = []
            elif edge["attributes"] is None:
                edge["attributes"] = []
            edge["attributes"].append(self.explanatory_agent_provenance_attribute)

            new_edges[new_edge_id] = edge
        self.knowledge_graph['edges'] = new_edges

    def generateQueryGraphForOnePath(self):
        query_graph = deepcopy(self.nominalKnowledgeProviderRequestBody)['message']['query_graph']
        query_graph['edges'][self.predicate_query_graph_edge_id]['predicates'] = [self.paths[0].predicate]
        query_graph['nodes'][self.subject_query_graph_node_id]['categories'] = [self.paths[0].subject]
        query_graph['nodes'][self.object_query_graph_node_id]['categories'] = [self.paths[0].object]

        if self.subjectCurieIds is not None:
            query_graph['nodes'][self.subject_query_graph_node_id]['ids'] = deepcopy(self.subjectCurieIds)
        if self.objectCurieIds is not None:
            query_graph['nodes'][self.object_query_graph_node_id]['ids'] = deepcopy(self.objectCurieIds)

        if self.subjectConstraints is not None:
            query_graph['nodes'][self.subject_query_graph_node_id]['constraints'] = deepcopy(self.subjectConstraints)
        if self.objectConstraints is not None:
            query_graph['nodes'][self.object_query_graph_node_id]['constraints'] = deepcopy(self.objectConstraints)
        if self.edgeConstraints is not None:
            query_graph['edges'][self.predicate_query_graph_edge_id]['constraints'] = deepcopy(self.edgeConstraints)

        self.query_graph = query_graph
        # self.query_graph = deepcopy(self.paths[0].knowledgeProvider.requestBody['message']['query_graph'])

    def generateResultsForOnePath(self):
        self.explanation_case_solution = self.explanation_solution_finder.search(self.similarSubject, self.similarObject, self.similarPredicate,
                                                                                 self.knowledge_graph,
                                                                                 self.paths[0].knowledgeProvider.name,
                                                                                 similarity_threshold=self.explanation_similarity)
        self.explanation_case_solution.logs = self.logs
        self.logs.append(clsLogEvent(
            identifier=self.id,
            level="DEBUG",
            code="",
            message=f"Executing explanation case '{self.explanation_case_solution.case_id}'."
        ))

        self.results = self.explanation_case_solution.create_results_and_explain(self)

    subdispatch_offset = 1000000
    def createCaseSolutions(self):
        """
        Create a case solution for each path. This allows each solution to have their own explanations, which can be combined as a single result in this
        parent case solution.
        :return:
        """

        self.path_solutions = []
        for i, path in enumerate(self.paths):
            new_dispatch_id = self.dispatchId + (clsCaseSolution.subdispatch_offset * (i+1))
            caseSolution = clsCaseSolution(
                dispatchId=new_dispatch_id,
                dispatchDescription=f"Solution {self.id} for Case {self.caseId} Path {i} / {len(self.paths)}"
            )
            caseSolution.dispatchIdSuffix = "" if new_dispatch_id == 1 else ("-" + str(new_dispatch_id))
            # caseSolution.logs = []
            caseSolution.logs = self.logs  # enables shared log across all objects by passing by reference. Don't want currently.
            caseSolution.id = self.id
            caseSolution.caseId = self.caseId
            caseSolution.similarSubject = path.subject
            caseSolution.similarObject = path.object
            caseSolution.similarPredicate = path.predicate
            if i == 0:
                caseSolution.subjectCurieIds = self.subjectCurieIds
                caseSolution.objectCurieIds = None
                caseSolution.subjectConstraints = self.subjectConstraints
                caseSolution.objectConstraints = None
            else:
                caseSolution.subjectCurieIds = None
                caseSolution.objectCurieIds = self.objectCurieIds
                caseSolution.subjectConstraints = None
                caseSolution.objectConstraints = self.objectConstraints
            caseSolution.explanation_similarity = self.explanation_similarity
            caseSolution.explanation_solution_finder = self.explanation_solution_finder

            caseSolution.subject_query_graph_node_id = f"n0{i}"
            caseSolution.object_query_graph_node_id = f"n0{i+1}"
            caseSolution.predicate_query_graph_edge_id = f"e0{i}"

            caseSolutionPath1 = path
            caseSolution.paths = [caseSolutionPath1]

            self.path_solutions.append(caseSolution)

        self.multihop = clsMultiHop(self.dispatchId, self.dispatchDescription, self.path_solutions)

    def generateKnowledgeGraphForTwoPaths(self):
        self.multihop.execute()

        if self.multihop.knowledge_graph:
            self.knowledge_graph = self.multihop.knowledge_graph
        # if the multihop stopped midway through, build a skeleton knowledge graph.
        else:
            self.knowledge_graph = {"nodes": {}, "edges": {}}

        # create empty knowledge_graph
        # self.knowledge_graph = {"nodes": {}, "edges": {}}

        # create a network graph of the knowledge graph so we can easily get the results
        # self.networkx_knowledge_graph = networkx.DiGraph()
        #
        # for i, case_solution in enumerate(self.path_solutions):
        #     case_solution.execute()
        #
        #     if case_solution.paths[0].knowledgeProvider.checkForEmptyResponseBody():
        #         raise ValueError(f"Derived two-KP query returned no data from query {i+1}.")
        #
        #     case_solution.generate_results()
        #
        #     # if this isn't the last case solution set the next hop's subject to this hop's object results
        #     if i < len(self.path_solutions) - 1:
        #         next_case_solution = self.path_solutions[i+1]
        #         # update the object node id and node binding ids to maintain consistency across query graphs.
        #         # e.g. n0-10001 -> n1-20001 -> n2-20001 (n1 technically has two ids without this, n1-10001 and -20001)
        #         case_solution.query_graph['nodes'][f"n01"] = case_solution.query_graph['nodes'][f"n01"]
        #         del case_solution.query_graph['nodes'][f"n01"]
        #
        #         for result in case_solution.results:
        #             # some explanation cases generate multiple results per edge (X00002), and the edge ids are passed by reference (somehow) so when one changes, they all change in every result.
        #             if f"n01" in result['node_bindings']:
        #                 result['node_bindings'][f"n01"] = result['node_bindings'][f"n01"]
        #                 del result['node_bindings'][f"n01"]
        #
        #         # objectNodeIds from this path are the subjectCurieIds of the next path
        #         subjectCurieIdsForNextPath = set()
        #         for edgeId, edge in self.paths[0].knowledgeProvider.responseBody["message"]["knowledge_graph"]["edges"].items():
        #             subjectCurieIdsForNextPath.add(edge['object'])  # objects of first path are subjects of second path
        #
        #         self.path_solutions[i+1].subjectCurieIds = sorted(list(subjectCurieIdsForNextPath))
        #         self.path_solutions[i+1].paths[0].subjectCurieIds = sorted(list(subjectCurieIdsForNextPath))
        #
        #     for nodeId, node in case_solution.paths[0].knowledgeProvider.responseBody["message"]["knowledge_graph"]["nodes"].items():
        #         self.knowledge_graph["nodes"][nodeId] = deepcopy(node)
        #         self.networkx_knowledge_graph.add_node(nodeId, **deepcopy(node))
        #
        #     for edgeId, edge in case_solution.paths[0].knowledgeProvider.responseBody["message"]["knowledge_graph"]["edges"].items():
        #         self.knowledge_graph["edges"][edgeId] = deepcopy(edge)
        #         if "attributes" not in self.knowledge_graph['edges'][edgeId]:
        #             self.knowledge_graph['edges'][edgeId]["attributes"] = []
        #         elif self.knowledge_graph['edges'][edgeId]["attributes"] is None:
        #             self.knowledge_graph['edges'][edgeId]["attributes"] = []
        #
        #         self.knowledge_graph['edges'][edgeId]["attributes"].append(self.explanatory_agent_provenance_attribute)
        #         self.networkx_knowledge_graph.add_edge(edge["subject"], edge["object"], id=edgeId, **deepcopy(edge))
        #
        # return

    @property
    def explanatory_agent_provenance_attribute(self):
        return {
            "attribute_type_id": "biolink:aggregator_knowledge_source",
            "value": "infores:explanatory-agent",
            "value_type_id": "biolink:InformationResource",
            "value_url": f"https://explanatory-agent.azurewebsites.net/{version}",
            "description": "The eXplanatory Autonomous Relay Agent (xARA) utilizes a case-based reasoning approach to execute ARS queries by obtaining results from multiple knowledge providers (KPs) and utilizes various methods such as natural language understanding models that traverse biomedical literature to score and explain its scores.",
            "attribute_source": "infores:explanatory-agent"
        }

    def generateQueryGraphForTwoPaths(self):
        query_graph = {"nodes": {}, "edges": {}}

        for case_solution in self.multihop.case_solutions:
            # if the case solution has no query graph is wasn't called because the prior case failed. We can still build a skeleton query graph, though.
            if case_solution.query_graph is None:
                case_solution.generateQueryGraphForOnePath()
            query_graph['nodes'].update(deepcopy(case_solution.query_graph['nodes']))
            query_graph['edges'].update(deepcopy(case_solution.query_graph['edges']))

        # remove the specified IDs from the second KP query graph, as they weren't specified in the original query.
        if 'ids' in query_graph['nodes']['n01']:
            del query_graph['nodes']['n01']['ids']

        self.query_graph = query_graph

        # # constraints not used for 2 path
        #
        # # path0_dispatch_suffix = self.path_solutions[0].dispatchIdSuffix
        # # path1_dispatch_suffix = self.path_solutions[1].dispatchIdSuffix
        # path0_dispatch_suffix = ""
        # path1_dispatch_suffix = ""
        #
        # self.query_graph = {
        #     "edges": {
        #         ("e00" + path0_dispatch_suffix): {
        #             "subject": ("n00" + path0_dispatch_suffix),
        #             "predicates": [self.paths[0].predicate],
        #             "object": ("n01" + path1_dispatch_suffix)
        #         },
        #         ("e01" + path1_dispatch_suffix): {
        #             "subject": ("n01" + path1_dispatch_suffix),
        #             "predicates": [self.paths[1].predicate],
        #             "object": ("n02" + path1_dispatch_suffix)
        #         },
        #     },
        #     "nodes": {
        #         ("n00" + path0_dispatch_suffix): deepcopy(self.path_solutions[0].paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n00' + path0_dispatch_suffix)]),
        #         ("n01" + path0_dispatch_suffix): deepcopy(self.path_solutions[0].paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n01' + path1_dispatch_suffix)]),
        #         # ("n01" + path1_dispatch_suffix): deepcopy(self.path_solutions[1].paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n00' + path1_dispatch_suffix)]),
        #         ("n02" + path1_dispatch_suffix): deepcopy(self.path_solutions[1].paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n01' + path1_dispatch_suffix)]),
        #     }
        # }

    def generateResultsForTwoPaths(self):
        if self.multihop.results:
            self.results = self.multihop.results
        else:
            self.results = []

        # self.results = []
        # # for case_solution in self.path_solutions:
        # #     self.results += case_solution.results
        #
        # subjectCurieIdsForResults = set()
        # for edgeId, edge in self.paths[0].knowledgeProvider.responseBody['message']['knowledge_graph']['edges'].items():
        #     subjectCurieIdsForResults.add(edge['subject'])
        # subjectCurieIdsForResults = sorted(list(subjectCurieIdsForResults))
        #
        # for subjectCurieId in subjectCurieIdsForResults:
        #     for intermediateCurieId in self.networkx_knowledge_graph.successors(subjectCurieId):
        #         intermediateNode = self.networkx_knowledge_graph[intermediateCurieId]  # not needed
        #         edge00 = self.networkx_knowledge_graph.get_edge_data(subjectCurieId, intermediateCurieId)
        #         for objectCurieId in self.networkx_knowledge_graph.successors(intermediateCurieId):
        #             objectNode = self.networkx_knowledge_graph[objectCurieId]  # not needed
        #             edge01 = self.networkx_knowledge_graph.get_edge_data(intermediateCurieId, objectCurieId)
        #             result = OrderedDict()
        #
        #             result['edge_bindings'] = {
        #                 "e00": [{
        #                     "id": edge00['id'],
        #                 }],
        #                 "e01": [{
        #                     "id": edge01['id'],
        #                 }],
        #             }
        #
        #             result['node_bindings'] = {
        #                 "n00": [{"id": subjectCurieId}],
        #                 "n01": [{"id": intermediateCurieId}],
        #                 "n02": [{"id": objectCurieId}],
        #             }
        #
        #             result['score'] = 0.0
        #             result['attributes'] = []
        #
        #             self.results.append(result)

    def updateKnowledgeProviderLogs(self):
        """
        Updates the logs' identifier to the solution ID, as the KPs don't know it when they are logging.
        :return:
        """

        for path in self.paths:
            for log in path.logs:
                log.identifier = self.id

            for log in path.knowledgeProvider.logs:
                log.identifier = self.id

            self.logs += path.logs
