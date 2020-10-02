"""
WHAT: A class which handles the logic involved with the clsAgentController
    * validates user request body
    * validates knowledge provider response body
    * applies query_graph from user request body after being validated
    * applies knowledge_graph from the knowledge provider response body after being validated
    * creates the results which maps nodes and edges from the query_graph and knowledge_graph
WHY: Need a class to handle data specific logic outside of clsAgentController to separate concerns
ASSUMES: 'Agent' is short for 'Explanatory Autonomous Relay Agent'
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-09-10
"""

from utils.modTextUtils import isNullOrWhiteSpace
from collections import OrderedDict


class clsAgent:
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

    @staticmethod
    def userRequestBodyIsValid(body):
        """
        A function to evaluate whether the JSON body received from the client conforms to the proper input standard.
        :param body: A dictionary representing a JSON body
        :return: Boolean: True meaning the body is valid, False meaning the body is not valid
        """
        if type(body) != dict: return False
        if sorted(list(body.keys())) != ['message']: return False

        if type(body['message']) != dict: return False
        if sorted(list(body['message'].keys())) != ['query_graph']: return False

        if type(body['message']['query_graph']) != dict: return False
        if sorted(list(body['message']['query_graph'].keys())) != ['edges', 'nodes']: return False

        edges = body['message']['query_graph']['edges']
        if type(edges) != list: return False
        if len(edges) != 1: return False

        edge = edges[0]
        if type(edge) != dict: return False
        if sorted(list(edge.keys())) != ['id', 'source_id', 'target_id', 'type']: return False
        if isNullOrWhiteSpace(edge['id']): return False
        if isNullOrWhiteSpace(edge['source_id']): return False
        if isNullOrWhiteSpace(edge['target_id']): return False
        if edge['type'] != 'associated': return False

        nodes = body['message']['query_graph']['nodes']
        if type(nodes) != list: return False
        if len(nodes) != 2: return False

        geneNodeFound = False
        diseaseNodeFound = False
        geneId = None
        diseaseId = None
        for node in nodes:
            if type(node) != dict: return False
            if sorted(list(node.keys())) == ['id', 'type'] and node['type'] == 'gene':
                if isNullOrWhiteSpace(node['id']): return False
                geneNodeFound = True
                geneId = node['id']
            elif sorted(list(node.keys())) == ['curie', 'id', 'type'] and node['type'] == 'disease':
                if isNullOrWhiteSpace(node['id']): return False
                if node['curie'] not in ['MONDO:0004981', 'MONDO:0005010', 'MONDO:0005300', 'EFO:0005208', 'EFO:0004612', 'EFO:0004611', 'EFO:0004340', 'MONDO:0007455', 'EFO:0004465', 'EFO:0004466', 'EFO:0004541']: return False
                diseaseNodeFound = True
                diseaseId = node['id']
            else:
                return False
        if not geneNodeFound or not diseaseNodeFound: return False
        if geneId != edge['target_id'] or diseaseId != edge['source_id']: return False
        return True

    @staticmethod
    def knowledgeProviderResponseBodyIsValid(body):
        """
        A function to evaluate whether the JSON body received from the knowledge provider conforms to our assumptions.
        :param body: A dictionary representing a JSON body
        :return: Boolean: True meaning the body is valid, False meaning the body is not valid (the knowledge provider has changed their api!)
        """
        if type(body) != dict: return False
        if sorted(list(body.keys())) != ['knowledge_graph', 'query_graph', 'results']: return False

        if type(body['knowledge_graph']) != dict: return False
        if sorted(list(body['knowledge_graph'].keys())) != ['edges', 'nodes']: return False

        edges = body['knowledge_graph']['edges']
        if type(edges) != list: return False
        for edge in edges:
            if type(edge) != dict: return False
            if sorted(list(edge.keys())) != ['id', 'score', 'score_direction', 'score_name', 'source_id', 'target_id', 'type']: return False

        nodes = body['knowledge_graph']['nodes']
        if type(nodes) != list: return False
        for node in nodes:
            if type(node) != dict: return False
            if sorted(list(node.keys())) != ['id', 'type']: return False

        return True

    def applyQueryGraphFromUserRequestBody(self, body):
        """
        Assigns a portion of the JSON request body from the client to the query_graph property
        :param body: A dictionary representing a JSON body
        :return: None
        """
        self.query_graph = body['message']['query_graph']

    def applyKnowledgeGraphFromKnowledgeProviderResponseBody(self, body):
        """
        Assigns a portion of the JSON response body from the knowledge provider to the knowledge_graph property
        :param body: A dictionary representing a JSON body
        :return: None
        """
        self.knowledge_graph = body['knowledge_graph']

    def generateResults(self):
        """
        Creates the results which maps nodes and edges from the query_graph and knowledge_graph.
        This is in-lieu of the results given by the knowledge provider, those are discarded.
        :return: None
        """
        self.results = []
        queryEdge = self.query_graph['edges'][0]
        for knowledgeEdge in self.knowledge_graph['edges']:
            result = OrderedDict()
            result['edge_bindings'] = [{'kg_id': knowledgeEdge['id'], 'qg_id': queryEdge['id']}]
            result['node_bindings'] = [
                {'kg_id': knowledgeEdge['source_id'], 'qg_id': queryEdge['source_id']},
                {'kg_id': knowledgeEdge['target_id'], 'qg_id': queryEdge['target_id']}
            ]
            result['Explanatory_Agent_Ranking'] = 1  # todo
            result['Explanatory_Agent_Explanation'] = "reserved for textual description"  # todo
            self.results.append(result)
