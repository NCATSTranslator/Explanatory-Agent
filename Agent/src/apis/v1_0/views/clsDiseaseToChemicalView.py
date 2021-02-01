"""
WHAT: Workflow that retrieves all associated chemicals for a single disease across several Knowledge Providers then explains the associations.
WHY: Chemicals associated with a disease are useful for research.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: TZ 2021-01-27
"""
from apis.v1_0.models.clsQuery import clsQuery
from apis.v1_0.views.clsDiseaseAssociatedGeneView import DiseaseAssociatedGeneView
from apis.v1_0.views.QueryHandlers.molecularDataProvider import MolecularDataProvider
from apis.common.utils.modTextUtils import isNullOrWhiteSpace
from collections import OrderedDict


class DiseaseToChemicalView(DiseaseAssociatedGeneView):
    @staticmethod
    def predicates():
        """
        No predicates supported as the expected query for this case doesn't have one.
        """
        return {}

    def __init__(self, *args, **kwargs):
        self.disease_to_chemical_edge = None
        self.disease_to_chemical_edge_id = None

        self.disease_id = None
        self.disease_node = None
        self.chemical_id = None
        self.chemical_node = None

        self.molepro_results = None

        self.knowledge_graph = None

        super(DiseaseToChemicalView, self).__init__(*args, **kwargs)

    def supports_query(self, trapi_query):
        """
        Checks if the provided TRAPI query contains all criteria for executing this case. This is defined as a classmethod because inheriting classes may wish
        to override supported queries via .get_valid_curies().
        :param trapi_query: TRAPI Message JSON object to check for support.
        :return: True if supported, False otherwise.
        """

        edges = trapi_query['message']['query_graph']['edges']
        if len(edges) != 1: return False

        self.disease_to_chemical_edge_id = list(edges.keys())[0]
        if isNullOrWhiteSpace(self.disease_to_chemical_edge_id): return False
        self.disease_to_chemical_edge = edges[self.disease_to_chemical_edge_id]

        if type(self.disease_to_chemical_edge) != dict: return False
        if sorted(list(self.disease_to_chemical_edge.keys())) != ['object', 'subject']: return False
        if "predicate" in self.disease_to_chemical_edge: return False
        if isNullOrWhiteSpace(self.disease_to_chemical_edge['subject']): return False
        if isNullOrWhiteSpace(self.disease_to_chemical_edge['object']): return False

        nodes = trapi_query['message']['query_graph']['nodes']
        if len(nodes) != 2: return False

        self.disease_id = None
        self.disease_node = None
        self.chemical_id = None
        self.chemical_node = None

        for nodeId, node in nodes.items():
            if isNullOrWhiteSpace(nodeId): return False
            if sorted(list(node.keys())) == ['category'] and node['category'] == 'biolink:ChemicalSubstance':
                self.chemical_id = nodeId
                self.chemical_node = node
            elif sorted(list(node.keys())) == ['category', 'id'] and node['category'] == 'biolink:Disease':
                self.disease_id = nodeId
                self.disease_node = node
            else:
                return False
        if self.disease_node is None or self.chemical_node is None: return False
        if self.disease_id != self.disease_to_chemical_edge['subject'] or self.chemical_id != self.disease_to_chemical_edge['object']: return False

        return True

    def retrieve(self):
        """
        Gather data from one KP: Molecular Data Provider (MolePro).
        """
        edge = {
            "subject": self.disease_id,
            "predicate": "biolink:treated_by",
            "object": self.chemical_id,
        }

        molepro_query = clsQuery.build_one_hop_query(self.disease_node, self.chemical_node, edge)

        molepro = MolecularDataProvider()
        self.query_results = molepro.query(molepro_query)

    def create_results(self):
        """
        Generates placeholder results.
        :return: None
        """
        self.query.results = []
        # sorting for deterministic results. This can go away after index isn't used for rank.
        for index, (knowledgeEdgeId, knowledgeEdge) in enumerate(
                sorted(list(self.query.knowledge_graph['edges'].items()), key=lambda i: i[0])):
            result = OrderedDict()
            result['edge_bindings'] = {"e00": [{
                "id": knowledgeEdgeId,
                "Explanatory_Agent_Ranking": index + 1,
                "Explanatory_Agent_Explanation": "TBD"
            }]}
            result['node_bindings'] = {
                "n00": [{"id": knowledgeEdge['subject']}],
                "n01": [{"id": knowledgeEdge['object']}],
            }

            self.query.results.append(result)

