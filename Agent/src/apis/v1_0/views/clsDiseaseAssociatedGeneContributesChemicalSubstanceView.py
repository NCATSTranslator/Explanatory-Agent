"""
WHAT: Workflow that retrieves all associated genes for a single disease across several Knowledge Providers then explains the associations.
WHY: Genes associated with a disease are useful for research.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: TZ 2021-01-27
"""

from apis.v1_0.views.QueryHandlers.geneticsProvider import GeneticsProvider
from apis.v1_0.views.QueryHandlers.multiomicsProvider import MultiomicsProvider
from apis.v1_0.models.clsQuery import clsQuery
from apis.v1_0.views.clsDiseaseAssociatedGeneView import DiseaseAssociatedGeneView
from apis.common.utils.modTextUtils import isNullOrWhiteSpace
from collections import OrderedDict
import copy
import networkx


class DiseaseAssociatedGeneContributesChemicalSubstanceView(DiseaseAssociatedGeneView):
    CONDITION_ASSOCIATED_WITH_GENE = "biolink:condition_associated_with_gene"

    @staticmethod
    def predicates():
        # TODO: Is this right? Technically it should be nested even further, but the spec doesn't have a way to do that.
        return {
            "biolink:Disease": {
                "biolink:Gene": [
                    "biolink:gene_associated_with_condition"
                ]
            },
            "biolink:Gene": {
                "biolink:ChemicalSubstance": [
                    "biolink:gene_has_variant_that_contributes_to_drug_response_association"
                ]
            }
        }

    @staticmethod
    def get_valid_curies():
        return ["MONDO:0007254"]

    def __init__(self, *args, **kwargs):
        self.disease_associated_gene_edge = None
        self.disease_associated_gene_edge_id = None
        self.gene_contributes_chemical_edge = None
        self.gene_contributes_chemical_edge_id = None

        self.geneId = None
        self.geneNode = None
        self.diseaseId = None
        self.diseaseNode = None
        self.chemicalId = None
        self.chemicalNode = None

        self.genetics_results = None
        self.multiomics_results = None

        self.knowledge_graph = None

        super(DiseaseAssociatedGeneContributesChemicalSubstanceView, self).__init__(*args, **kwargs)

    def supports_query(self, trapi_query):
        """
        Checks if the provided TRAPI query contains all criteria for executing this case. This is defined as a classmethod because inheriting classes may wish
        to override supported queries via .get_valid_curies().
        :param trapi_query: TRAPI Message JSON object to check for support.
        :return: True if supported, False otherwise.
        """

        edges = trapi_query['message']['query_graph']['edges']
        if len(edges) != 2: return False

        self.disease_associated_gene_edge = None
        self.disease_associated_gene_edge_id = None
        self.gene_contributes_chemical_edge = None
        self.gene_contributes_chemical_edge_id = None

        for edge_id, edge in edges.items():
            if edge["predicate"] == DiseaseAssociatedGeneContributesChemicalSubstanceView.CONDITION_ASSOCIATED_WITH_GENE:
                self.disease_associated_gene_edge = edge
                self.disease_associated_gene_edge_id = edge_id
            elif edge["predicate"] == "biolink:gene_has_variant_that_contributes_to_drug_response_association":
                self.gene_contributes_chemical_edge = edge
                self.gene_contributes_chemical_edge_id = edge_id
            else:
                return False

        if isNullOrWhiteSpace(self.disease_associated_gene_edge_id): return False
        if isNullOrWhiteSpace(self.gene_contributes_chemical_edge_id): return False

        for edge in (self.disease_associated_gene_edge, self.gene_contributes_chemical_edge):
            if type(edge) != dict: return False
            if sorted(list(edge.keys())) != ['object', 'predicate', 'subject']: return False
            if isNullOrWhiteSpace(edge['subject']): return False
            if isNullOrWhiteSpace(edge['object']): return False

        nodes = trapi_query['message']['query_graph']['nodes']
        if len(nodes) != 3: return False

        self.geneId = None
        self.geneNode = None
        self.diseaseId = None
        self.diseaseNode = None
        self.chemicalId = None
        self.chemicalNode = None
        # validCuries = cls.get_valid_curies()

        for nodeId, node in nodes.items():
            if isNullOrWhiteSpace(nodeId): return False
            if sorted(list(node.keys())) == ['category', 'id'] and node['category'] == 'biolink:Disease':
                # if node['id'] not in validCuries: return False
                self.diseaseNode = node
                self.diseaseId = nodeId
            elif sorted(list(node.keys())) == ['category'] and node['category'] == 'biolink:Gene':
                self.geneNode = node
                self.geneId = nodeId
            elif sorted(list(node.keys())) == ['category'] and node['category'] == 'biolink:ChemicalSubstance':
                self.chemicalNode = node
                self.chemicalId = nodeId
            else:
                return False

        if isNullOrWhiteSpace(self.diseaseNode): return False
        if isNullOrWhiteSpace(self.geneNode): return False
        if isNullOrWhiteSpace(self.chemicalNode): return False

        if self.diseaseId != self.disease_associated_gene_edge['subject']: return False
        if self.geneId != self.disease_associated_gene_edge['object'] or self.geneId != self.gene_contributes_chemical_edge['subject']: return False
        if self.chemicalId != self.gene_contributes_chemical_edge['object']: return False

        return True

    def retrieve(self):
        """
        Gather data from two KPs: Genetics Provider and Multiomics Provider.
        """
        self.gp_results = None
        self.multiomics_results = None

        genetics_query = clsQuery.build_one_hop_query(self.diseaseNode, self.geneNode, self.disease_associated_gene_edge)

        genetics_provider = GeneticsProvider()
        self.genetics_results = genetics_provider.query(genetics_query)

        # extract all NCBI genes from the results to pass to Multiomics Provider
        genes = set()
        for edge_id, edge in self.genetics_results["message"]["knowledge_graph"]["edges"].items():
            if edge["predicate"] == DiseaseAssociatedGeneContributesChemicalSubstanceView.CONDITION_ASSOCIATED_WITH_GENE:
                gene = edge["object"]
                if gene.startswith("NCBIGene:"):
                    genes.add(gene)

        genesNode = {
            "id": sorted(list(genes))[:10],
            "category": self.geneNode["category"]
        }
        multiomics_query = clsQuery.build_one_hop_query(genesNode, self.chemicalNode, self.gene_contributes_chemical_edge)

        multiomics_provider = MultiomicsProvider()
        self.multiomics_results = multiomics_provider.query(multiomics_query)

    def populate_knowledge_graph(self):
        """
        Merge the Genetics and Multiomics Providers' queries' knowledge graphs together.
        """
        merged_knowledge_graph = {"nodes": {}, "edges": {}}

        # create a network graph of the knowledge graph so we can easily get the results
        self.knowledge_graph = networkx.DiGraph()

        # merge nodes
        for node_id, node in self.genetics_results["message"]["knowledge_graph"]["nodes"].items():
            merged_knowledge_graph["nodes"][node_id] = node
            self.knowledge_graph.add_node(node_id, **node)

        for node_id, node in self.multiomics_results["message"]["knowledge_graph"]["nodes"].items():
            merged_knowledge_graph["nodes"][node_id] = node
            self.knowledge_graph.add_node(node_id, **node)

        # merge edges
        for edge_id, edge in self.genetics_results["message"]["knowledge_graph"]["edges"].items():
            merged_knowledge_graph["edges"][edge_id] = edge
            self.knowledge_graph.add_edge(edge["subject"], edge["object"], id=edge_id, **edge)

        for edge_id, edge in self.multiomics_results["message"]["knowledge_graph"]["edges"].items():
            merged_knowledge_graph["edges"][edge_id] = edge
            self.knowledge_graph.add_edge(edge["subject"], edge["object"], id=edge_id, **edge)

        self.query.knowledge_graph = merged_knowledge_graph

        networkx.write_gpickle(self.knowledge_graph, "/tmp/kg.gpkl")

        # q = 5
        # import matplotlib.pyplot as plt
        # # sudo apt-get install python3-dev graphviz libgraphviz-dev pkg-config
        # from networkx.drawing.nx_agraph import graphviz_layout
        # positions = graphviz_layout(self.knowledge_graph)
        # plt.clf()
        # # nx.draw_networkx(graph, pos, with_labels=True, arrows=True, font_size=8, labels=labels)
        # # networkx.draw_networkx(self.knowledge_graph, positions, with_labels=True, arrows=True, font_size=8, labels=labels)
        # networkx.draw_networkx(self.knowledge_graph, positions, with_labels=True, arrows=True, font_size=8)
        # # plt.pause(0.05)
        # plt.show()

    def create_results(self):
        """
        Starting with the disease node requested, iterate over all connected gene nodes. For those gene nodes, iterate over all connected chemical nodes. For each chemical node,
        generate a result set of three nodes and two edges that is a constrained set of Disease -> Gene -> Chemical.
        :return: None
        """

        self.query.results = []

        disease_id = self.diseaseNode["id"]
        if disease_id not in self.knowledge_graph:
            return

        for gene_id in self.knowledge_graph.successors(disease_id):
            if gene_id.startswith("NCBIGene:"):
                gene_node = self.knowledge_graph[gene_id]
                disease_gene_edge = self.knowledge_graph.get_edge_data(disease_id, gene_id)
                for chemical_id in self.knowledge_graph.successors(gene_id):
                    chemical_node = self.knowledge_graph[chemical_id]
                    gene_chemical_edge = self.knowledge_graph.get_edge_data(gene_id, chemical_id)
                    result = OrderedDict()
                    result['edge_bindings'] = {
                        "e0": [{
                            "id": disease_gene_edge["id"],
                            "Explanatory_Agent_Ranking": len(self.query.results) + 1,
                            "Explanatory_Agent_Explanation": "TBD"
                        }],
                        "e1": [{
                            "id": gene_chemical_edge["id"],
                            "Explanatory_Agent_Ranking": len(self.query.results) + 1,
                            "Explanatory_Agent_Explanation": "TBD"
                        }]
                    }
                    result['node_bindings'] = {
                        "n0": [{"id": disease_id}],
                        "n1": [{"id": gene_id}],
                        "n2": [{"id": chemical_id}],
                    }

                    self.query.results.append(result)

    def validate(self):
        """
        Ensure the query we have generated is valid
        """
        response_message = self.query.generateTRAPISuccessResponse()
        # Multiomics provider is missing 'type' in their nodes' attributes, so we have to exclude nodes from validation.
        censored_message = copy.deepcopy(response_message)
        del censored_message["message"]["knowledge_graph"]["nodes"]
        self.query.userResponseBodyIsValid(censored_message)
