"""
WHAT: Query that retrieves all associated genes for a single disease across several Knowledge Providers then explains the associations.
WHY: Genes associated with a disease are useful for research.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: TZ 2021-01-27
"""

from .clsQuery import clsQuery
from ..knowledgeProviders.clsGeneticsKnowledgeProvider import clsGeneticsKnowledgeProvider
from utils.modTextUtils import isNullOrWhiteSpace
from collections import OrderedDict


class clsDiseaseAssociatedGeneQuery(clsQuery):
    explanations = {
        0: "Disease-Gene association was not identified to be MAGMA_GENE or INTEGRATED_GENETICS. As such, no explanation can be made.",  # default
        1: "Disease-Gene association was identified via MAGMA_GENE (a standard method for identifying gene-condition associations from variant-level associations using proximity-based assignments from GWAS data) AND was also identified by INTEGRATED_GENETICS (an experimental method for identifying gene-condition associations using a novel combination of established methods). INTEGRATED_GENETICS is still in development and undergoing optimization; false-positives may be present.\nConfirmation of the association with both available methods from this KP gives us high confidence in these results.",
        2: "Disease-Gene association was identified via MAGMA_GENE (a standard method for identifying gene-condition associations from variant-level associations using proximity-based assignments from GWAS data), but was not confirmed by INTEGRATED_GENETICS (an experimental method that for identifying gene-condition associations using a novel combination of established methods).\nINTEGRATED_GENETICS is still in development and undergoing optimization; false-positives may be present. Considering MAGMA_GENE is a standard method in the field, we still maintain acceptable confidence in these results.",
        3: "Disease-Gene association was identified only by INTEGRATED_GENETICS (an experimental method for identifying gene-condition associations using a novel combination of established methods). Results were not confirmed using the standard MAGMA_GENE method.\nINTEGRATED_GENETICS is still in development and undergoing optimization; false-positives may be present. For this reason, we consider these results to be the associations with lowest confidence.",
    }

    def __init__(self, userRequestBody: dict):
        """
        Constructor
        :param userRequestBody: TRAPI user request body
        """
        super().__init__(userRequestBody=userRequestBody)

        self.geneticsKnowledgeProvider = None

    @property
    def predicates(self):
        """
        Assigned predicates property
        :return: predicates dictionary
        """
        return {
            "biolink:Disease": {
                "biolink:Gene": [
                    "biolink:condition_associated_with_gene"
                ]
            }
        }

    @property
    def validCuries(self):
        """
        Assigned validCuries property
        :return: validCuries list
        """
        return ["EFO:0000249", "EFO:0000253", "EFO:0000270", "EFO:0000275", "EFO:0000289", "EFO:0000341",
                "EFO:0000378", "EFO:0000384", "EFO:0000401", "EFO:0000551", "EFO:0000612", "EFO:0000692",
                "EFO:0000729", "EFO:0001359", "EFO:0001360", "EFO:0001365", "EFO:0002506", "EFO:0003144",
                "EFO:0003761", "EFO:0003767", "EFO:0003884", "EFO:0003931", "EFO:0004190", "EFO:0004305",
                "EFO:0004312", "EFO:0004314", "EFO:0004326", "EFO:0004338", "EFO:0004339", "EFO:0004340",
                "EFO:0004342", "EFO:0004343", "EFO:0004458", "EFO:0004462", "EFO:0004465", "EFO:0004466",
                "EFO:0004469", "EFO:0004471", "EFO:0004501", "EFO:0004502", "EFO:0004509", "EFO:0004518",
                "EFO:0004530", "EFO:0004532", "EFO:0004533", "EFO:0004534", "EFO:0004535", "EFO:0004541",
                "EFO:0004555", "EFO:0004570", "EFO:0004574", "EFO:0004611", "EFO:0004612", "EFO:0004614",
                "EFO:0004615", "EFO:0004616", "EFO:0004623", "EFO:0004631", "EFO:0004683", "EFO:0004698",
                "EFO:0004703", "EFO:0004704", "EFO:0004705", "EFO:0004713", "EFO:0004735", "EFO:0004736",
                "EFO:0004741", "EFO:0004761", "EFO:0004808", "EFO:0004838", "EFO:0004844", "EFO:0004861",
                "EFO:0004997", "EFO:0005000", "EFO:0005001", "EFO:0005055", "EFO:0005058", "EFO:0005093",
                "EFO:0005094", "EFO:0005208", "EFO:0005246", "EFO:0005271", "EFO:0005665", "EFO:0005680",
                "EFO:0005763", "EFO:0006335", "EFO:0006336", "EFO:0006340", "EFO:0006807", "EFO:0006831",
                "EFO:0006832", "EFO:0007630", "EFO:0007778", "EFO:0007788", "EFO:0007789", "EFO:0007800",
                "EFO:0007817", "EFO:0007828", "EFO:0007878", "EFO:0007929", "EFO:0008000", "EFO:0008036",
                "EFO:0008037", "EFO:0008039", "EFO:0008328", "EFO:0008373", "EFO:0008455", "EFO:0008456",
                "EFO:0008595", "EFO:0008596", "EFO:0009270", "EFO:0009282", "EFO:0009283", "EFO:0009284",
                "EFO:0009718", "EFO:0009765", "EFO:0009767", "EFO:0009768", "EFO:0009769", "EFO:0009770",
                "EFO:0009792", "EFO:0009793", "EFO:0009881", "EFO:0009961", "EFO:0010074", "EFO:0010075",
                "EFO:0010076", "EFO:0010111", "EFO:0010112", "EFO:0010114", "EFO:0010115", "EFO:0010116",
                "EFO:0010117", "EFO:0010118", "EFO:0010119", "EFO:0010120", "EFO:0010177", "EFO:0010178",
                "EFO:0010465", "EFO:0010555", "EFO:1000783", "EFO:1000786", "EFO:1001506",
                'MONDO:0004981', 'MONDO:0005010', 'MONDO:0005300', 'MONDO:0007455']

    def userRequestBodyIsSupported(self):
        """
        Checks if the provided TRAPI query contains all criteria for executing this case. This is defined as a classmethod because inheriting classes may wish
        to override supported queries via .get_valid_curies().
        :param trapi_query: TRAPI Message JSON object to check for support.
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
        if edge['predicate'] != 'biolink:condition_associated_with_gene': return False

        nodes = self.userRequestBody['message']['query_graph']['nodes']
        if len(nodes) != 2: return False

        geneNodeFound = False
        diseaseNodeFound = False
        geneId = None
        diseaseId = None

        for nodeId, node in nodes.items():
            if isNullOrWhiteSpace(nodeId): return False
            if sorted(list(node.keys())) == ['category'] and node['category'] == 'biolink:Gene':
                geneNodeFound = True
                geneId = nodeId
            elif sorted(list(node.keys())) == ['category', 'id'] and node['category'] == 'biolink:Disease':
                if node['id'] not in self.validCuries: return False
                diseaseNodeFound = True
                diseaseId = nodeId
            else:
                return False
        if not geneNodeFound or not diseaseNodeFound: return False
        if geneId != edge['object'] or diseaseId != edge['subject']: return False

        return True

    def getDataFromKnowledgeProviders(self):
        """
        Gather data from Genetics Knowledge Provider.
        """
        self.geneticsKnowledgeProvider = clsGeneticsKnowledgeProvider(requestBody=self.buildSlimRequestBody())
        self.geneticsKnowledgeProvider.execute()

    def populateKnowledgeGraph(self):
        """
        Assign knowledge provider response body to our knowledge_graph
        :return: None
        """
        self.knowledge_graph = self.geneticsKnowledgeProvider.responseBody['message']['knowledge_graph']

    def createResults(self):
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
                "Explanatory_Agent_Explanation": self.explanations[explanationCode]

            }]}
            result['node_bindings'] = {
                "n00": [{"id": knowledgeEdge['subject']}],
                "n01": [{"id": knowledgeEdge['object']}],
            }

            self.results.append(result)

    def generateTargetIdExplanationCounts(self):
        """
        Generates a dictionary of where the key is a target id and the value is another dictionary with the key as a explanation code and value is the count
        :return: dict
        """

        targetIdExplanationCounts = {}
        for edgeId, knowledgeEdge in self.knowledge_graph['edges'].items():
            targetId = knowledgeEdge['object']
            if targetId not in targetIdExplanationCounts:
                targetIdExplanationCounts[targetId] = {code: 0 for code in
                                                       self.explanations.keys()}  # initialize keys with 0 as value
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
