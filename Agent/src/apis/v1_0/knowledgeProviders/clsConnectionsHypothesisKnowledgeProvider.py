"""
WHAT: Queries the Connections Hypothesis Provider and returns results.
WHY: Connections Hypothesis Provider provides data such as genes associated with a disease, which is used in some of the Agent's cases.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: TZ 2021-01-27
"""

from ..knowledgeProviders.clsKnowledgeProvider import clsKnowledgeProvider


class clsConnectionsHypothesisKnowledgeProvider(clsKnowledgeProvider):
    """
    See header
    """
    
    url = "http://chp.thayer.dartmouth.edu/query/"

    def __init__(self):
        """
        Constructor
        Pass in empty dictionary as query, because it will be calculated with buildRequestBody
        """
        super().__init__(requestBody={})

    def buildRequestBody(
            self,
            diseaseId: str,
            geneId: str = None,
            hasGeneNode: bool = False,
            drugId: str = None,
            hasDrugNode: bool = False,
            survivalTime: str = None,  # todo, what is this datatype?
            hasSurvivalNode: bool = True
    ):

        # empty
        requestBody = {"query_graph": {"edges": {}, "nodes": {}}}

        nodeCount = 0
        edgeCount = 0

        # add gene node
        geneNodeIndex = None
        if hasGeneNode:
            if geneId is not None:
                requestBody['query_graph']['nodes']['n{}'.format(nodeCount)] = {
                    'category': 'biolink:Gene',
                    'id': geneId
                }
                geneNodeIndex = nodeCount
                nodeCount += 1
            else:
                requestBody['query_graph']['nodes']['n{}'.format(nodeCount)] = {
                    'category': 'biolink:Gene'
                }
                geneNodeIndex = nodeCount
                nodeCount += 1

        # add drug node
        drugNodeIndex = None
        if hasDrugNode:
            if drugId is not None:
                requestBody['query_graph']['nodes']['n{}'.format(nodeCount)] = {
                    'category': 'biolink:Drug',
                    'id': drugId
                }
                drugNodeIndex = nodeCount
                nodeCount += 1
            else:
                requestBody['query_graph']['nodes']['n{}'.format(nodeCount)] = {
                    'category': 'biolink:Drug'
                }
                drugNodeIndex = nodeCount
                nodeCount += 1

        # add in disease node
        diseaseNodeIndex = nodeCount
        requestBody['query_graph']['nodes']['n{}'.format(nodeCount)] = {
            'category': 'biolink:Disease',
            'id': diseaseId
        }
        nodeCount += 1

        # add survival node
        survivalNodeIndex = None
        if hasSurvivalNode:
            requestBody['query_graph']['nodes']['n{}'.format(nodeCount)] = {
                'category': 'biolink:PhenotypicFeature',
                'id': 'EFO:0000714'
            }
            survivalNodeIndex = nodeCount

        # link evidence to disease node
        if geneNodeIndex is not None:
            requestBody['query_graph']['edges']['e{}'.format(edgeCount)] = {
                'predicate': 'biolink:gene_associated_with_condition',
                'subject': 'n{}'.format(geneNodeIndex),
                'object': 'n{}'.format(diseaseNodeIndex)
            }
            edgeCount += 1

        if drugNodeIndex is not None:
            requestBody['query_graph']['edges']['e{}'.format(edgeCount)] = {
                'predicate': 'biolink:treats',
                'subject': 'n{}'.format(drugNodeIndex),
                'object': 'n{}'.format(diseaseNodeIndex)
            }
            edgeCount += 1

        # link disease to survival node
        if hasSurvivalNode:
            requestBody['query_graph']['edges']['e{}'.format(edgeCount)] = {
                'predicate': 'biolink:has_phenotype',
                'subject': 'n{}'.format(diseaseNodeIndex),
                'object': 'n{}'.format(survivalNodeIndex)
            }
            if survivalTime is not None:
                requestBody['query_graph']['edges']['e{}'.format(edgeCount)]['properties'] = {
                    'qualifier': '>=',
                    'days': survivalTime
                }

        self.requestBody = {"requestBody": requestBody}
