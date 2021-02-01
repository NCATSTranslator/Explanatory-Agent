"""
WHAT: Workflow that retrieves all associated genes for a single disease across several Knowledge Providers then explains the associations.
WHY: Genes associated with a disease are useful for research.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: TZ 2021-01-27
"""

from apis.v1_0.views.QueryHandlers.connectionsHypothesisProvider import ConnectionsHypothesisProvider
from apis.v1_0.models.clsQuery import clsQuery
from apis.v1_0.views.clsDiseaseAssociatedGeneView import DiseaseAssociatedGeneView
from apis.common.utils.modTextUtils import isNullOrWhiteSpace
from collections import OrderedDict


class GeneAssociatedDiseaseView(DiseaseAssociatedGeneView):
    @staticmethod
    def predicates():
        return {
            "biolink:Gene": {
                "biolink:Disease": [
                    "biolink:gene_associated_with_condition"
                ]
            }
        }

    @staticmethod
    def get_valid_curies():
        return ["MONDO:0007254"]

    def supports_query(self, trapi_query):
        """
        Checks if the provided TRAPI query contains all criteria for executing this case. This is defined as a classmethod because inheriting classes may wish
        to override supported queries via .get_valid_curies().
        :param trapi_query: TRAPI Message JSON object to check for support.
        :return: True if supported, False otherwise.
        """

        edges = trapi_query['message']['query_graph']['edges']
        if len(edges) != 1: return False

        edgeId = list(edges.keys())[0]
        if isNullOrWhiteSpace(edgeId): return False
        edge = edges[edgeId]

        if type(edge) != dict: return False
        if sorted(list(edge.keys())) != ['object', 'predicate', 'subject']: return False
        if isNullOrWhiteSpace(edge['subject']): return False
        if isNullOrWhiteSpace(edge['object']): return False
        if edge['predicate'] != 'biolink:gene_associated_with_condition': return False

        nodes = trapi_query['message']['query_graph']['nodes']
        if len(nodes) != 2: return False

        geneNodeFound = False
        diseaseNodeFound = False
        geneId = None
        diseaseId = None
        validCuries = GeneAssociatedDiseaseView.get_valid_curies()

        for nodeId, node in nodes.items():
            if isNullOrWhiteSpace(nodeId): return False
            if sorted(list(node.keys())) == ['category'] and node['category'] == 'biolink:Gene':
                geneNodeFound = True
                geneId = nodeId
            elif sorted(list(node.keys())) == ['category', 'id'] and node['category'] == 'biolink:Disease':
                if node['id'] not in validCuries: return False
                diseaseNodeFound = True
                diseaseId = nodeId
            else:
                return False
        if not geneNodeFound or not diseaseNodeFound: return False
        if geneId != edge['subject'] or diseaseId != edge['object']: return False

        return True

    def retrieve(self):
        """
        Gather data from two KPs: Genetics Provider and Connections Hypothesis Provider.
        """
        edge = list(self.query.query_graph["edges"].keys())[0]
        disease_node = self.query.query_graph["edges"][edge]["object"]
        disease_id = self.query.query_graph["nodes"][disease_node]["id"]

        chp = ConnectionsHypothesisProvider()
        chp_query = ConnectionsHypothesisProvider.build_chp_query(disease_id, gene_node=True, survival_node=False)
        self.query_results = chp.query(chp_query)

    def create_results(self):
        """
        Generates placeholder results.
        :return: None
        """
        self.query.results = []
        # sorting for deterministic results. This can go away after index isn't used for rank.
        for index, (knowledgeEdgeId, knowledgeEdge) in enumerate(sorted(list(self.query.knowledge_graph['edges'].items()), key=lambda i: i[0])):
            result = OrderedDict()
            result['edge_bindings'] = {"e0": [{
                "id": knowledgeEdgeId,
                "Explanatory_Agent_Ranking": index + 1,
                "Explanatory_Agent_Explanation": "TBD"
            }]}
            result['node_bindings'] = {
                "n0": [{"id": knowledgeEdge['subject']}],
                "n1": [{"id": knowledgeEdge['object']}],
            }

            self.query.results.append(result)
