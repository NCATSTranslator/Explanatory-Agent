from copy import deepcopy
from collections import OrderedDict
import networkx


class clsCaseSolution:

    def __init__(self):
        self.id = None
        self.paths = None  # list of length 1 or 2

        self.subjectCurieIds = None
        self.objectCurieIds = None

        self.edgeConstraints = None
        self.subjectConstraints = None
        self.objectConstraints = None

        self.similarPredicates = None

        # output
        self.query_graph = None
        self.knowledge_graph = None
        self.results = None

        # helper knowledge_graph for merging
        self.networkx_knowledge_graph = None

        self.logs = None

        self.dispatchIdSuffix = None

    def solve(self):
        if len(self.paths) == 1:
            self.generateKnowledgeGraphForOnePath()
            self.generateQueryGraphForOnePath()
            self.generateResultsForOnePath()
        elif len(self.paths) == 2:
            self.generateKnowledgeGraphForTwoPaths()
            self.generateQueryGraphForTwoPaths()
            self.generateResultsForTwoPaths()
        else:
            raise AttributeError("Number of knowledge provider paths supported is either 1 or 2")

    @property
    def nominalKnowledgeProviderRequestBody(self):
        return {
            "message": {
                "query_graph": {
                    "edges": {
                        ("e00" + self.dispatchIdSuffix): {
                            "subject": "n00" + self.dispatchIdSuffix,
                            "predicates": None,
                            "object": "n01" + self.dispatchIdSuffix
                        }
                    },
                    "nodes": {
                        ("n00" + self.dispatchIdSuffix): {
                            "categories": None
                        },
                        ("n01" + self.dispatchIdSuffix): {
                            "categories": None
                        }
                    }
                }
            }
        }

    def generateKnowledgeGraphForOnePath(self):

        self.paths[0].knowledgeProvider.requestBody = deepcopy(self.nominalKnowledgeProviderRequestBody)
        self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['edges'][('e00' + self.dispatchIdSuffix)]['predicates'] = [self.paths[0].predicate]
        self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n00' + self.dispatchIdSuffix)]['categories'] = [self.paths[0].subject]
        self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n01' + self.dispatchIdSuffix)]['categories'] = [self.paths[0].object]

        if self.subjectCurieIds is not None:
            self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n00' + self.dispatchIdSuffix)]['ids'] = deepcopy(self.subjectCurieIds)
        if self.objectCurieIds is not None:
            self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n01' + self.dispatchIdSuffix)]['ids'] = deepcopy(self.objectCurieIds)

        if self.subjectConstraints is not None:
            self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n00' + self.dispatchIdSuffix)]['constraints'] = deepcopy(self.subjectConstraints)
        if self.objectConstraints is not None:
            self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n01' + self.dispatchIdSuffix)]['constraints'] = deepcopy(self.objectConstraints)
        if self.edgeConstraints is not None:
            self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['edges'][('e00' + self.dispatchIdSuffix)]['constraints'] = deepcopy(self.edgeConstraints)

        self.paths[0].knowledgeProvider.execute()
        self.knowledge_graph = deepcopy(self.paths[0].knowledgeProvider.responseBody['message']['knowledge_graph'])

        # adding knowledge provider to the edge of the knowlege_graph
        for edgeId in self.knowledge_graph['edges']:
            if "attributes" not in self.knowledge_graph['edges'][edgeId]:
                self.knowledge_graph['edges'][edgeId]["attributes"] = []
            self.knowledge_graph['edges'][edgeId]["attributes"].append({
                "attribute_type_id": "biolink:aggregator_knowledge_source",
                "value": self.paths[0].knowledgeProvider.name
            })

        # todo, how to add these and still pass validation? A: inject in "Attributes", but need correct biolink CURIEs
        # for edgeId, edge in self.knowledge_graph['edges'].items():
        #     edge.update({
        #         "KP_name": [self.paths[0].knowledgeProvider.name],
        #         "xARA_Explanation_Rationale": "TBD",
        #         "xARA_Explanation_Ranking": 1,
        #         "xARA_Explanation_Text": "TBD"
        #     })

    def generateQueryGraphForOnePath(self):
        self.query_graph = deepcopy(self.paths[0].knowledgeProvider.requestBody['message']['query_graph'])

    def generateResultsForOnePath(self):
        self.results = []
        # sorting for deterministic results. This can go away after index isn't used for rank.
        for index, (edgeId, edge) in enumerate(sorted(list(self.knowledge_graph['edges'].items()), key=lambda i: i[0])):
            result = OrderedDict()
            result['edge_bindings'] = {
                ("e00" + self.dispatchIdSuffix): [{
                    "id": edgeId,
                    "KP_name": [self.paths[0].knowledgeProvider.name],
                    "xARA_Explanation_Rationale": "TBD",
                    "xARA_Explanation_Ranking": 1,
                    "xARA_Explanation_Text": "TBD"
                }]
            }
            result['node_bindings'] = {
                ("n00" + self.dispatchIdSuffix): [{"id": edge['subject']}],
                ("n01" + self.dispatchIdSuffix): [{"id": edge['object']}],
            }

            self.results.append(result)

    def generateKnowledgeGraphForTwoPaths(self):
        # constraints not used for 2 path

        self.paths[0].knowledgeProvider.requestBody = deepcopy(self.nominalKnowledgeProviderRequestBody)
        self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['edges'][('e00' + self.dispatchIdSuffix)]['predicates'] = [self.paths[0].predicate]
        self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n00' + self.dispatchIdSuffix)]['categories'] = [self.paths[0].subject]
        self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n01' + self.dispatchIdSuffix)]['categories'] = [self.paths[0].object]

        if self.subjectCurieIds is not None:
            self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n00' + self.dispatchIdSuffix)]['ids'] = self.subjectCurieIds

        self.paths[0].knowledgeProvider.execute()

        # objectNodeIds from the first path are the subjectCurieIds of the second path
        subjectCurieIdsForNextPath = set()
        for edgeId, edge in self.paths[0].knowledgeProvider.responseBody["message"]["knowledge_graph"]["edges"].items():
            subjectCurieIdsForNextPath.add(edge['object'])  # objects of first path are subjects of second path

        # todo, if empty set then just be done here and assume only a 1 KP Path

        self.paths[1].knowledgeProvider.requestBody = deepcopy(self.nominalKnowledgeProviderRequestBody)
        self.paths[1].knowledgeProvider.requestBody['message']['query_graph']['edges'][('e00' + self.dispatchIdSuffix)]['predicates'] = [self.paths[1].predicate]
        self.paths[1].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n00' + self.dispatchIdSuffix)]['categories'] = [self.paths[1].subject]
        self.paths[1].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n01' + self.dispatchIdSuffix)]['categories'] = [self.paths[1].object]

        if subjectCurieIdsForNextPath != set():
            self.paths[1].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n00' + self.dispatchIdSuffix)]['ids'] = sorted(list(subjectCurieIdsForNextPath))
        if self.objectCurieIds is not None:
            self.paths[1].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n01' + self.dispatchIdSuffix)]['ids'] = deepcopy(self.objectCurieIds)
        # todo, what to do with empty set?

        self.paths[1].knowledgeProvider.execute()

        # create empty knowledge_graph
        self.knowledge_graph = {"nodes": {}, "edges": {}}

        # create a network graph of the knowledge graph so we can easily get the results
        self.networkx_knowledge_graph = networkx.DiGraph()

        # merge nodes
        for nodeId, node in self.paths[0].knowledgeProvider.responseBody["message"]["knowledge_graph"]["nodes"].items():
            self.knowledge_graph["nodes"][nodeId] = deepcopy(node)
            self.networkx_knowledge_graph.add_node(nodeId, **deepcopy(node))

        for nodeId, node in self.paths[1].knowledgeProvider.responseBody["message"]["knowledge_graph"]["nodes"].items():
            self.knowledge_graph["nodes"][nodeId] = deepcopy(node)
            self.networkx_knowledge_graph.add_node(nodeId, **deepcopy(node))

        # merge edges
        for edgeId, edge in self.paths[0].knowledgeProvider.responseBody["message"]["knowledge_graph"]["edges"].items():
            self.knowledge_graph["edges"][edgeId] = deepcopy(edge)
            if "attributes" not in self.knowledge_graph['edges'][edgeId]:
                self.knowledge_graph['edges'][edgeId]["attributes"] = []
            self.knowledge_graph['edges'][edgeId]["attributes"].append({
                "attribute_type_id": "biolink:aggregator_knowledge_source",
                "value": self.paths[0].knowledgeProvider.name
            })
            self.networkx_knowledge_graph.add_edge(edge["subject"], edge["object"], id=edgeId, **deepcopy(edge))

        for edgeId, edge in self.paths[1].knowledgeProvider.responseBody["message"]["knowledge_graph"]["edges"].items():
            self.knowledge_graph["edges"][edgeId] = deepcopy(edge)
            if "attributes" not in self.knowledge_graph['edges'][edgeId]:
                self.knowledge_graph['edges'][edgeId]["attributes"] = []
            self.knowledge_graph['edges'][edgeId]["attributes"].append({
                "attribute_type_id": "biolink:aggregator_knowledge_source",
                "value": self.paths[1].knowledgeProvider.name
            })
            self.networkx_knowledge_graph.add_edge(edge["subject"], edge["object"], id=edgeId, **deepcopy(edge))

        # todo, how to add these and still pass validation?
        # for edgeId, edge in self.knowledge_graph['edges'].items():
        #     edge.update({
        #         "KP_name": [self.paths[0].knowledgeProvider.name, self.paths[1].knowledgeProvider.name],
        #         "xARA_Explanation_Rationale": "TBD",
        #         "xARA_Explanation_Ranking": 1,
        #         "xARA_Explanation_Text": "TBD"
        #     })

    def generateQueryGraphForTwoPaths(self):
        # constraints not used for 2 path

        self.query_graph = {
            "edges": {
                ("e00" + self.dispatchIdSuffix): {
                    "subject": ("n00" + self.dispatchIdSuffix),
                    "predicates": [self.paths[0].predicate],
                    "object": ("n01" + self.dispatchIdSuffix)
                },
                ("e01" + self.dispatchIdSuffix): {
                    "subject": ("n01" + self.dispatchIdSuffix),
                    "predicates": [self.paths[1].predicate],
                    "object": ("n02" + self.dispatchIdSuffix)
                },
            },
            "nodes": {
                ("n00" + self.dispatchIdSuffix): deepcopy(self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n00' + self.dispatchIdSuffix)]),
                ("n01" + self.dispatchIdSuffix): deepcopy(self.paths[0].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n01' + self.dispatchIdSuffix)]),
                ("n02" + self.dispatchIdSuffix): deepcopy(self.paths[1].knowledgeProvider.requestBody['message']['query_graph']['nodes'][('n01' + self.dispatchIdSuffix)]),
            }
        }

    def generateResultsForTwoPaths(self):
        self.results = []

        subjectCurieIdsForResults = set()
        for edgeId, edge in self.paths[0].knowledgeProvider.responseBody['message']['knowledge_graph']['edges'].items():
            subjectCurieIdsForResults.add(edge['subject'])
        subjectCurieIdsForResults = sorted(list(subjectCurieIdsForResults))

        for subjectCurieId in subjectCurieIdsForResults:
            for intermediateCurieId in self.networkx_knowledge_graph.successors(subjectCurieId):
                intermediateNode = self.networkx_knowledge_graph[intermediateCurieId]  # not needed
                edge00 = self.networkx_knowledge_graph.get_edge_data(subjectCurieId, intermediateCurieId)
                for objectCurieId in self.networkx_knowledge_graph.successors(intermediateCurieId):
                    objectNode = self.networkx_knowledge_graph[objectCurieId]  # not needed
                    edge01 = self.networkx_knowledge_graph.get_edge_data(intermediateCurieId, objectCurieId)
                    result = OrderedDict()

                    result['edge_bindings'] = {
                        ("e00" + self.dispatchIdSuffix): [{
                            "id": edge00['id'],
                            "KP_name": [self.paths[0].knowledgeProvider.name, self.paths[1].knowledgeProvider.name],
                            "xARA_Explanation_Rationale": "TBD",
                            "xARA_Explanation_Ranking": 1,
                            "xARA_Explanation_Text": "TBD"
                        }],
                        ("e01" + self.dispatchIdSuffix): [{
                            "id": edge01['id'],
                            "KP_name": [self.paths[0].knowledgeProvider.name, self.paths[1].knowledgeProvider.name],
                            "xARA_Explanation_Rationale": "TBD",
                            "xARA_Explanation_Ranking": 1,
                            "xARA_Explanation_Text": "TBD"
                        }],
                    }

                    result['node_bindings'] = {
                        ("n00" + self.dispatchIdSuffix): [{"id": subjectCurieId}],
                        ("n01" + self.dispatchIdSuffix): [{"id": intermediateCurieId}],
                        ("n02" + self.dispatchIdSuffix): [{"id": objectCurieId}],
                    }

                    self.results.append(result)


   # def generateResultsForTwoPaths(self):
   #      self.results = []
   #
   #      subjectCurieIdsForResults = set()
   #      for edgeId, edge in self.paths[0].knowledgeProvider.responseBody['message']['knowledge_graph']['edges'].items():
   #          subjectCurieIdsForResults.add(edge['subject'])
   #      subjectCurieIdsForResults = sorted(list(subjectCurieIdsForResults))
   #
   #      newEdgesToAdd = {}
   #      for subjectCurieId in subjectCurieIdsForResults:
   #          for intermediateCurieId in self.networkx_knowledge_graph.successors(subjectCurieId):
   #              for objectCurieId in self.networkx_knowledge_graph.successors(intermediateCurieId):
   #
   #                  newEdgeId = subjectCurieId + "___" + objectCurieId
   #
   #                  # todo, what do we do if its already in the dictionaries?
   #                  if newEdgeId in newEdgesToAdd or newEdgeId in self.knowledge_graph['edges']:
   #                      raise AttributeError(f"Duplicate newEdgeId in results {newEdgeId}")
   #
   #                  newEdge = {
   #                      "subject": subjectCurieId,
   #                      "object": objectCurieId,
   #                      "predicates": self.similarPredicates,
   #                      "KP_name": [self.paths[0].knowledgeProvider.name, self.paths[1].knowledgeProvider.name],
   #                      "xARA_Explanation_Rationale": "TBD",
   #                      "xARA_Explanation_Ranking": 1,
   #                      "xARA_Explanation_Text": "TBD"
   #                  }
   #
   #                  self.knowledge_graph['edges'][newEdgeId] = deepcopy(newEdge)
   #                  newEdgesToAdd[newEdgeId] = deepcopy(newEdge)
   #
   #                  result = OrderedDict()
   #
   #                  result['edge_bindings'] = {
   #                      "e00": [{
   #                          "id": newEdgeId,
   #                          "KP_name": [self.paths[0].knowledgeProvider.name, self.paths[1].knowledgeProvider.name],
   #                          "xARA_Explanation_Rationale": "TBD",
   #                          "xARA_Explanation_Ranking": 1,
   #                          "xARA_Explanation_Text": "TBD"
   #                      }],
   #                  }
   #
   #                  result['node_bindings'] = {
   #                      "n00": [{"id": subjectCurieId}],
   #                      "n01": [{"id": objectCurieId}],
   #                  }
   #
   #                  self.results.append(result)
   #
   #      # add all new edges back to networkx_knowledge_graph
   #      for newEdgeId, newEdge in newEdgesToAdd.items():
   #          self.networkx_knowledge_graph.add_edge(newEdge['subject'], newEdge['object'], id=newEdgeId, **deepcopy(newEdge))
