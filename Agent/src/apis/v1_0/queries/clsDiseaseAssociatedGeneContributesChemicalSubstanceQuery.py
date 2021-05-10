"""
WHAT: Query that retrieves all associated genes for a single disease across several Knowledge Providers then explains the associations.
WHY: Genes associated with a disease are useful for research.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: TZ 2021-01-27
"""

from .clsQuery import clsQuery
from ..knowledgeProviders.clsGeneticsKnowledgeProvider import clsGeneticsKnowledgeProvider
from ..knowledgeProviders.clsMultiomicsKnowledgeProvider import clsMultiomicsKnowledgeProvider
from utils.modTextUtils import isNullOrWhiteSpace
from collections import OrderedDict
import networkx


class clsDiseaseAssociatedGeneContributesChemicalSubstanceQuery(clsQuery):
    """
    See header
    """

    CONDITION_ASSOCIATED_WITH_GENE = "biolink:condition_associated_with_gene"

    def __init__(self, userRequestBody: dict):
        super().__init__(userRequestBody=userRequestBody)

        self.diseaseAssociatedGeneEdge = None
        self.diseaseAssociatedGeneEdgeId = None
        self.geneContributesChemicalEdge = None
        self.geneContributesChemicalEdgeId = None

        self.geneId = None
        self.geneNode = None
        self.diseaseId = None
        self.diseaseNode = None
        self.chemicalId = None
        self.chemicalNode = None

        self.geneticsKnowledgeProvider = None
        self.multiomicsKnowledgeProvider = None

        self.networkx_knowledge_graph = None
        self.knowledge_graph = None

    @property
    def predicates(self):
        """
        Assigned predicates property
        :return: predicates dictionary
        """
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
        if len(edges) != 2: return False

        self.diseaseAssociatedGeneEdge = None
        self.diseaseAssociatedGeneEdgeId = None
        self.geneContributesChemicalEdge = None
        self.geneContributesChemicalEdgeId = None

        for edge_id, edge in edges.items():
            if edge["predicate"] == self.CONDITION_ASSOCIATED_WITH_GENE:
                self.diseaseAssociatedGeneEdge = edge
                self.diseaseAssociatedGeneEdgeId = edge_id
            elif edge["predicate"] == "biolink:gene_has_variant_that_contributes_to_drug_response_association":
                self.geneContributesChemicalEdge = edge
                self.geneContributesChemicalEdgeId = edge_id
            else:
                return False

        if isNullOrWhiteSpace(self.diseaseAssociatedGeneEdgeId): return False
        if isNullOrWhiteSpace(self.geneContributesChemicalEdgeId): return False

        for edge in (self.diseaseAssociatedGeneEdge, self.geneContributesChemicalEdge):
            if type(edge) != dict: return False
            if sorted(list(edge.keys())) != ['object', 'predicate', 'subject']: return False
            if isNullOrWhiteSpace(edge['subject']): return False
            if isNullOrWhiteSpace(edge['object']): return False

        nodes = self.userRequestBody['message']['query_graph']['nodes']
        if len(nodes) != 3: return False

        self.geneId = None
        self.geneNode = None
        self.diseaseId = None
        self.diseaseNode = None
        self.chemicalId = None
        self.chemicalNode = None

        for nodeId, node in nodes.items():
            if isNullOrWhiteSpace(nodeId): return False
            if sorted(list(node.keys())) == ['category', 'id'] and node['category'] == 'biolink:Disease':
                # if node['id'] not in self.validCuries: return False
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

        if self.diseaseId != self.diseaseAssociatedGeneEdge['subject']: return False
        if self.geneId != self.diseaseAssociatedGeneEdge['object'] or self.geneId != self.geneContributesChemicalEdge['subject']: return False
        if self.chemicalId != self.geneContributesChemicalEdge['object']: return False

        return True

    def getDataFromKnowledgeProviders(self):
        """
        Gather data from two Knowledge Providers: Genetics Knowledge Provider and Multiomics Knowledge Provider.
        :return: None
        """

        geneticsKnowledgeProviderRequestBody = self.buildOneHopRequestBody(node1=self.diseaseNode, node2=self.geneNode, edge=self.diseaseAssociatedGeneEdge)
        self.geneticsKnowledgeProvider = clsGeneticsKnowledgeProvider(requestBody=geneticsKnowledgeProviderRequestBody)
        self.geneticsKnowledgeProvider.execute()

        # extract all NCBI genes from the results to pass to Multiomics Provider
        genes = set()
        for edgeId, edge in self.geneticsKnowledgeProvider.responseBody["message"]["knowledge_graph"]["edges"].items():
            if edge["predicate"] == self.CONDITION_ASSOCIATED_WITH_GENE:
                gene = edge["object"]
                if gene.startswith("NCBIGene:"):
                    genes.add(gene)

        genesNode = {
            "id": sorted(list(genes)),  # todo, was [:10], check unit tests
            "category": self.geneNode["category"]
        }
        
        multiomicsKnowledgeProviderRequestBody = self.buildOneHopRequestBody(node1=genesNode, node2=self.chemicalNode, edge=self.geneContributesChemicalEdge)
        self.multiomicsKnowledgeProvider = clsMultiomicsKnowledgeProvider(requestBody=multiomicsKnowledgeProviderRequestBody)
        self.multiomicsKnowledgeProvider.execute()

    def populateKnowledgeGraph(self):
        """
        Merge the Genetics and Multiomics Knowledge Providers' queries' knowledge graphs together.
        :return: None
        """

        self.knowledge_graph = {"nodes": {}, "edges": {}}

        # create a network graph of the knowledge graph so we can easily get the results
        self.networkx_knowledge_graph = networkx.DiGraph()

        # merge nodes
        for nodeId, node in self.geneticsKnowledgeProvider.responseBody["message"]["knowledge_graph"]["nodes"].items():
            self.knowledge_graph["nodes"][nodeId] = node
            self.networkx_knowledge_graph.add_node(nodeId, **node)

        for nodeId, node in self.multiomicsKnowledgeProvider.responseBody["message"]["knowledge_graph"]["nodes"].items():
            self.knowledge_graph["nodes"][nodeId] = node
            self.networkx_knowledge_graph.add_node(nodeId, **node)

        # merge edges
        for edgeId, edge in self.geneticsKnowledgeProvider.responseBody["message"]["knowledge_graph"]["edges"].items():
            self.knowledge_graph["edges"][edgeId] = edge
            self.networkx_knowledge_graph.add_edge(edge["subject"], edge["object"], id=edgeId, **edge)

        for edgeId, edge in self.multiomicsKnowledgeProvider.responseBody["message"]["knowledge_graph"]["edges"].items():
            self.knowledge_graph["edges"][edgeId] = edge
            self.networkx_knowledge_graph.add_edge(edge["subject"], edge["object"], id=edgeId, **edge)

    def createResults(self):
        """
        Starting with the disease node requested, iterate over all connected gene nodes. For those gene nodes, iterate over all connected chemical nodes. For each chemical node,
        generate a result set of three nodes and two edges that is a constrained set of Disease -> Gene -> Chemical.
        :return: None
        """

        self.results = []

        diseaseId = self.diseaseNode["id"]
        if diseaseId not in self.networkx_knowledge_graph: return

        for geneId in self.networkx_knowledge_graph.successors(diseaseId):
            if geneId.startswith("NCBIGene:"):
                geneNode = self.networkx_knowledge_graph[geneId]
                diseaseGeneEdge = self.networkx_knowledge_graph.get_edge_data(diseaseId, geneId)
                for chemicalId in self.networkx_knowledge_graph.successors(geneId):
                    chemicalNode = self.networkx_knowledge_graph[chemicalId]
                    geneChemicalEdge = self.networkx_knowledge_graph.get_edge_data(geneId, chemicalId)
                    result = OrderedDict()
                    result['edge_bindings'] = {
                        "e0": [{
                            "id": diseaseGeneEdge["id"],
                            "Explanatory_Agent_Ranking": len(self.results) + 1,
                            "Explanatory_Agent_Explanation": "TBD"
                        }],
                        "e1": [{
                            "id": geneChemicalEdge["id"],
                            "Explanatory_Agent_Ranking": len(self.results) + 1,
                            "Explanatory_Agent_Explanation": "TBD"
                        }]
                    }
                    result['node_bindings'] = {
                        "n0": [{"id": diseaseId}],
                        "n1": [{"id": geneId}],
                        "n2": [{"id": chemicalId}],
                    }

                    self.results.append(result)
