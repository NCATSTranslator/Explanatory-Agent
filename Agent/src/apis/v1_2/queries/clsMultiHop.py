"""
A list of Case Solutions to be executed in order, which them merges the resulting knowledge graphs and creates results.
"""
from utils.multithreading.clsNode import clsNode
from copy import deepcopy
from utils.clsLog import clsLogEvent
import networkx
from itertools import product, chain
import traceback


class clsMultiHop(clsNode):
    def __init__(self, dispatchId: int, dispatchDescription: str, case_solutions):
        super().__init__(dispatchId=dispatchId, dispatchDescription=dispatchDescription, dispatchMode="parallel", dispatchList=[])

        self.case_solutions = case_solutions
        self.query_graph = None
        self.knowledge_graph = None
        self.results = None

        self.logs = []

        # for case_solution in self.case_solutions:
        #     case_solution.logs = self.logs
            # for path in case_solution.paths:
            #     path.logs = case_solution.logs
            #     path.knowledgeProvider.logs = path.logs

        self.successful = False
        self.finished = False

    def execute_hops(self):
        for i, case_solution in enumerate(self.case_solutions):
            # if we are on a second+ hop, then try to populate its unknown node ids
            if i > 0:
                previous_solution = self.case_solutions[i-1]
                response_body = previous_solution.paths[-1].knowledgeProvider.responseBody
                if response_body is None or len(response_body["message"]["results"]) <= 0:
                    raise AbortMultihopException(f"Previous hop KP did not return results: '{previous_solution.paths[-1].knowledgeProvider.url}'")

                # build a list of all ids in the previous case's response for each node to be used in the current case
                response_node_ids = {}
                for result in response_body["message"]["results"]:
                    for node_id, node_bindings in result["node_bindings"].items():
                        if node_id not in response_node_ids:
                            response_node_ids[node_id] = set()
                        for node_binding in node_bindings:
                            if "id" in node_binding:
                                response_node_ids[node_id].add(node_binding["id"])

                # for each current case node see if it does not have any ids set already. If it doesn't set them.
                if case_solution.subjectCurieIds is None:
                    if case_solution.subject_query_graph_node_id in response_node_ids:
                        subject_new_ids = sorted(list(response_node_ids[case_solution.subject_query_graph_node_id]))
                        if len(subject_new_ids) > 50:
                            self.logs.append(clsLogEvent(
                                identifier=f"MH{self.dispatchId}",
                                level="INFO",
                                code="Info",
                                message=f"Too many previous hop subject ids to provide {len(subject_new_ids)}, reducing to 50."
                            ))
                            subject_new_ids = subject_new_ids[:50]
                        case_solution.subjectCurieIds = subject_new_ids

                if case_solution.objectCurieIds is None:
                    if case_solution.object_query_graph_node_id in response_node_ids:
                        object_new_ids = sorted(list(response_node_ids[case_solution.object_query_graph_node_id]))
                        if len(object_new_ids) > 50:
                            self.logs.append(clsLogEvent(
                                identifier=f"MH{self.dispatchId}",
                                level="INFO",
                                code="Info",
                                message=f"Too many previous hop object ids to provide {len(object_new_ids)}, reducing to 50."
                            ))
                            object_new_ids = object_new_ids[:50]
                        case_solution.objectCurieIds = object_new_ids

            case_solution.execute(no_results=False)

    def generate_results(self):
        for case_solution in self.case_solutions:
            case_solution.generate_results()

    def merge_query_graphs(self):
        self.query_graph = {"nodes": {}, "edges": {}}
        for case_solution in self.case_solutions:
            if case_solution.query_graph:
                self.query_graph['edges'].update(deepcopy(case_solution.query_graph['edges']))
                self.query_graph['nodes'].update(deepcopy(case_solution.query_graph['nodes']))

    def merge_knowledge_graphs(self):
        self.knowledge_graph = {"nodes": {}, "edges": {}}
        for case_solution in self.case_solutions:
            if case_solution.knowledge_graph:
                self.knowledge_graph['edges'].update(deepcopy(case_solution.knowledge_graph['edges']))
                self.knowledge_graph['nodes'].update(deepcopy(case_solution.knowledge_graph['nodes']))
                # self.knowledge_graph.update(case_solution.knowledge_graph)

    def merge_results(self):
        """
        Combine results from each case solution into full results that address all nodes and edges in the query graph. This is accomplished by generating a
        network graph of results then walking from a starting node to all linked nodes, building result objects as the graph is walked.
        :return:
        """
        self.results = []

        # if there is only one case solution, this is a one-hop query and the results don't need to be reformatted.
        if len(self.case_solutions) == 1:
            if self.case_solutions[0].results:
                self.results += self.case_solutions[0].results
            return

        nx_results = networkx.DiGraph()
        start_nodes = set()

        nx_results_node_format = "{}_{}"
        for i, case_solution in enumerate(self.case_solutions):
            # if any case doesn't have results then we can't complete the multihop query, so just abort.
            if len(case_solution.results) <= 0:
                return

            if case_solution.results:
                for result in case_solution.results:
                    if i == 0:
                        # n0 will ALWAYS be specified! If this changes a lot more will need to be done.
                        starting_node_qg_id = sorted(list(result["node_bindings"].keys()))[0]
                        for node_binding in result["node_bindings"][starting_node_qg_id]:
                            start_nodes.add(nx_results_node_format.format(starting_node_qg_id, node_binding['id']))

                    for edge_qg_id, edge_bindings in result["edge_bindings"].items():
                        for edge_binding in edge_bindings:
                            edge_kg_id = edge_binding["id"]

                            # ALWAYS 2 nodes! The edge directionality isn't implied, so we must refer to the query graph to find the node ids.
                            # node_binding_ids = sorted(list(result["node_bindings"]))
                            node1_qg_id = case_solution.query_graph['edges'][edge_qg_id]['subject']
                            node2_qg_id = case_solution.query_graph['edges'][edge_qg_id]['object']
                            node_pairs = product(*[result["node_bindings"][node1_qg_id], result["node_bindings"][node2_qg_id]])
                            for node1_binding, node2_binding in node_pairs:
                                node1_id = nx_results_node_format.format(node1_qg_id, node1_binding['id'])
                                node2_id = nx_results_node_format.format(node2_qg_id, node2_binding['id'])
                                nx_results.add_node(node1_id, query_graph_id=node1_qg_id, knowledge_graph_id=node1_binding['id'])
                                nx_results.add_node(node2_id, query_graph_id=node2_qg_id, knowledge_graph_id=node2_binding['id'])

                                nx_results.add_edge(node1_id, node2_id, score=result['score'], attributes=result['attributes'], result=result)

        # nx_results.remove_edges_from(networkx.selfloop_edges(nx_results))  # not needed anymore due to qg id disambiguation?

        def add_to_result(new_result, source_node, excluded_qg_ids):
            successors = nx_results.successors(source_node)
            predecessors = nx_results.predecessors(source_node)
            for neighbor in chain(successors, predecessors):
                node = nx_results.nodes[neighbor]
                if node['query_graph_id'] in excluded_qg_ids:
                    continue

                nx_edge = nx_results.get_edge_data(source_node, neighbor)
                # since we are looking in both directions the source -> neighbor edge may not exist, so look in the other direction.
                if nx_edge is None:
                    nx_edge = nx_results.get_edge_data(neighbor, source_node)
                edge_result = nx_edge["result"]

                # edge_result = nx_results.get_edge_data(source_node, successor)["result"]

                neighbor_result = deepcopy(new_result)
                neighbor_result["node_bindings"].update(edge_result["node_bindings"])
                neighbor_result["edge_bindings"].update(edge_result["edge_bindings"])

                # add the explanations from the result to the edge binding
                edge_bindings = neighbor_result["edge_bindings"][list(edge_result["edge_bindings"].keys())[0]]
                for edge_binding in edge_bindings:
                    edge_binding["attributes"] = edge_result["attributes"]
                    edge_binding["score"] = edge_result["score"]

                path_excluded_qg_ids = deepcopy(excluded_qg_ids)
                path_excluded_qg_ids.add(node['query_graph_id'])
                add_to_result(neighbor_result, neighbor, path_excluded_qg_ids)
                if len(neighbor_result["edge_bindings"]) == len(self.case_solutions):
                    self.results.append(neighbor_result)

        for starting_node_kg_id in start_nodes:
            new_result = {"node_bindings": {}, "edge_bindings": {}, "score": 0.0}

            add_to_result(new_result, starting_node_kg_id, {starting_node_qg_id})

        # compute the score for each result by averaging all edge binding scores
        for result in self.results:
            edge_scores = []
            for edge_qg_id, edge_bindings in result["edge_bindings"].items():
                for edge_binding in edge_bindings:
                    score = edge_binding["score"]
                    edge_scores.append(score)
            result["score"] = sum(edge_scores) / len(edge_scores)

    def merge_logs(self):
        for case_solution in self.case_solutions:
            if case_solution.logs:
                self.logs += case_solution.logs

    def execute(self):
        try:
            self.execute_hops()
            self.generate_results()
            # self.merge_query_graphs()  # not used anymore since the QG must remain constant (except for derived queries)
            self.merge_knowledge_graphs()
            self.merge_results()
            # self.merge_logs()
            self.successful = True
        except AbortMultihopException as e:
            self.logs.append(clsLogEvent(
                identifier=f"MH{self.dispatchId}",
                level="DEBUG",
                code="",
                message=f"Aborting Multihop execution: {e}"
            ))
        except Exception as e:
            print(traceback.format_exc())
            self.logs.append(clsLogEvent(
                identifier=f"MH{self.dispatchId}",
                level="ERROR",
                code="Error",
                message=f"Unhandled {type(e).__name__} Exception: {e}"
            ))
        finally:
            self.merge_logs()
            self.finished = True

import sys
# import tblib.pickling_support


class AbortMultihopException(Exception):

    def __init__(self, ee):
        self.ee = ee
        __, __, self.tb = sys.exc_info()
        super(AbortMultihopException, self).__init__(str(ee))

    def re_raise(self):
        raise self.ee.with_traceback(self.tb)
