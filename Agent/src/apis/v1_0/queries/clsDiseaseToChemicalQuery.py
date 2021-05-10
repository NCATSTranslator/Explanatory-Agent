"""
WHAT: Query that retrieves all associated chemicals for a single disease across several Knowledge Providers then explains the associations.
WHY: Chemicals associated with a disease are useful for research.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: TZ 2021-01-27
"""

from .clsQuery import clsQuery
from ..knowledgeProviders.clsMolecularDataKnowledgeProvider import clsMolecularDataKnowledgeProvider
from utils.modTextUtils import isNullOrWhiteSpace


class clsDiseaseToChemicalQuery(clsQuery):
    """
    See header
    """

    def __init__(self, userRequestBody: dict):
        """
        Constructor
        :param userRequestBody: TRAPI user request body
        """
        super().__init__(userRequestBody=userRequestBody)

        self.diseaseToChemicalEdge = None
        self.diseaseToChemicalEdgeId = None

        self.diseaseId = None
        self.diseaseNode = None
        self.chemicalId = None
        self.chemicalNode = None

        self.molecularDataKnowledgeProvider = None

        self.knowledge_graph = None

    @property
    def predicates(self):
        """
        No predicates supported as the expected query for this case doesn't have one.
        """
        return {}

    @property
    def validCuries(self):
        """
        No curies supported either
        """
        return []

    def userRequestBodyIsSupported(self):
        """
        Checks if the provided TRAPI query contains all criteria for executing this case.
        :return: True if supported, False otherwise.
        """

        edges = self.userRequestBody['message']['query_graph']['edges']
        if len(edges) != 1: return False

        self.diseaseToChemicalEdgeId = list(edges.keys())[0]
        if isNullOrWhiteSpace(self.diseaseToChemicalEdgeId): return False
        self.diseaseToChemicalEdge = edges[self.diseaseToChemicalEdgeId]

        if type(self.diseaseToChemicalEdge) != dict: return False
        if sorted(list(self.diseaseToChemicalEdge.keys())) != ['object', 'subject']: return False
        if "predicate" in self.diseaseToChemicalEdge: return False
        if isNullOrWhiteSpace(self.diseaseToChemicalEdge['subject']): return False
        if isNullOrWhiteSpace(self.diseaseToChemicalEdge['object']): return False

        nodes = self.userRequestBody['message']['query_graph']['nodes']
        if len(nodes) != 2: return False

        self.diseaseId = None
        self.diseaseNode = None
        self.chemicalId = None
        self.chemicalNode = None

        for nodeId, node in nodes.items():
            if isNullOrWhiteSpace(nodeId): return False
            if sorted(list(node.keys())) == ['category'] and node['category'] == 'biolink:ChemicalSubstance':
                self.chemicalId = nodeId
                self.chemicalNode = node
            elif sorted(list(node.keys())) == ['category', 'id'] and node['category'] == 'biolink:Disease':
                self.diseaseId = nodeId
                self.diseaseNode = node
            else:
                return False
        if self.diseaseNode is None or self.chemicalNode is None: return False
        if self.diseaseId != self.diseaseToChemicalEdge['subject'] or self.chemicalId != self.diseaseToChemicalEdge['object']: return False

        return True

    def getDataFromKnowledgeProviders(self):
        """
        Gather data from Molecular Data Knowledge Provider.
        :return: None
        """
        edge = {
            "subject": self.diseaseId,
            "predicate": "biolink:treated_by",
            "object": self.chemicalId,
        }
        molecularDataKnowledgeProviderRequestBody = self.buildOneHopRequestBody(node1=self.diseaseNode, node2=self.chemicalNode, edge=edge)
        self.molecularDataKnowledgeProvider = clsMolecularDataKnowledgeProvider(requestBody=molecularDataKnowledgeProviderRequestBody)
        self.molecularDataKnowledgeProvider.execute()

    def populateKnowledgeGraph(self):
        """
        Assign knowledge provider response body to our knowledge_graph
        :return: None
        """
        self.knowledge_graph = self.molecularDataKnowledgeProvider.responseBody['message']['knowledge_graph']

    def createResults(self):
        """
        Generates placeholder results.
        :return: None
        """
        # todo
        self.createGenericPlaceholderResults()
