"""
WHAT: Query that retrieves all associated genes for a single disease across several Knowledge Providers then explains the associations.
WHY: Genes associated with a disease are useful for research.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: TZ 2021-01-27
"""

from .clsQuery import clsQuery
from ..knowledgeProviders.clsConnectionsHypothesisKnowledgeProvider import clsConnectionsHypothesisKnowledgeProvider
from utils.modTextUtils import isNullOrWhiteSpace


class clsDrugTreatsDiseaseQuery(clsQuery):
    """
    See header
    """

    def __init__(self, userRequestBody: dict):
        """
        Constructor
        :param userRequestBody: TRAPI user request body
        """
        super().__init__(userRequestBody=userRequestBody)

        self.connectionHypothesisKnowledgeProvider = None

    @property
    def predicates(self):
        """
        Assigned predicates property
        :return: predicates dictionary
        """
        return {
            "biolink:Drug": {
                "biolink:Disease": [
                    "biolink:treats"
                ]
            }
        }

    @property
    def validCuries(self):
        """
        Assigned validCuries property
        :return: validCuries list
        """
        return ["MONDO:0007254"]

    def userRequestBodyIsSupported(self):
        """
        Checks if the provided TRAPI query contains all criteria for executing this case.
        :return: True if supported, False otherwise.
        """

        edges = self.userRequestBody['message']['query_graph']['edges']
        if len(edges) != 1: return False

        edgeId = list(edges.keys())[0]
        if isNullOrWhiteSpace(edgeId): return False
        edge = edges[edgeId]

        if type(edge) != dict: return False
        if sorted(list(edge.keys())) != ['object', 'predicate', 'subject']: return False
        if isNullOrWhiteSpace(edge['subject']): return False
        if isNullOrWhiteSpace(edge['object']): return False
        if edge['predicate'] != 'biolink:treats': return False

        nodes = self.userRequestBody['message']['query_graph']['nodes']
        if len(nodes) != 2: return False

        geneNodeFound = False
        diseaseNodeFound = False
        geneId = None
        diseaseId = None

        for nodeId, node in nodes.items():
            if isNullOrWhiteSpace(nodeId): return False
            if sorted(list(node.keys())) == ['category'] and node['category'] == 'biolink:Drug':
                geneNodeFound = True
                geneId = nodeId
            elif sorted(list(node.keys())) == ['category', 'id'] and node['category'] == 'biolink:Disease':
                # if node['id'] not in self.validCuries: return False
                diseaseNodeFound = True
                diseaseId = nodeId
            else:
                return False
        if not geneNodeFound or not diseaseNodeFound: return False
        if geneId != edge['subject'] or diseaseId != edge['object']: return False

        return True

    def getDataFromKnowledgeProviders(self):
        """
        Gather data from Connections Hypothesis Knowledge Provider.
        :return: None
        """
        edge = list(self.userRequestBody['message']['query_graph']["edges"].keys())[0]
        diseaseNode = self.userRequestBody['message']['query_graph']["edges"][edge]["object"]
        diseaseId = self.userRequestBody['message']['query_graph']["nodes"][diseaseNode]["id"]

        self.connectionHypothesisKnowledgeProvider = clsConnectionsHypothesisKnowledgeProvider()
        self.connectionHypothesisKnowledgeProvider.buildRequestBody(diseaseId=diseaseId, hasDrugNode=True, hasSurvivalNode=False)
        self.connectionHypothesisKnowledgeProvider.execute()

    def populateKnowledgeGraph(self):
        """
        Assign knowledge provider response body to our knowledge_graph
        :return: None
        """
        self.knowledge_graph = self.connectionHypothesisKnowledgeProvider.responseBody['message']['knowledge_graph']

    def createResults(self):
        """
        Generates placeholder results.
        :return: None
        """
        # todo
        self.createGenericPlaceholderResults()
