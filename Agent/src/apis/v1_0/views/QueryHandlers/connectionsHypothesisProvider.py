"""
WHAT: Queries the Connections Hypothesis Provider and returns results.
WHY: Connections Hypothesis Provider provides data such as genes associated with a disease, which is used in some of the Agent's cases.
ASSUMES: None
FUTURE IMPROVEMENTS: N/A
WHO: TZ 2021-01-27
"""

import requests
import reasoner_validator


class ConnectionsHypothesisProvider:
    url = "http://chp.thayer.dartmouth.edu/query/"

    def __init__(self):
        pass

    @staticmethod
    def build_chp_query(disease, gene=None, gene_node=False, drug=None, drug_node=False, survival_time=None, survival_node=True):
        # empty response
        reasoner_std = {"query_graph": dict()}
        # empty query graph
        reasoner_std["query_graph"] = {"edges": dict(), "nodes": dict()}

        node_count = 0
        edge_count = 0

        # add gene node
        gene_node_idx = None
        if gene_node:
            if gene is not None:
                reasoner_std['query_graph']['nodes']['n{}'.format(node_count)] = {'category': 'biolink:Gene',
                                                                                  'id': gene}
                gene_node_idx = node_count
                node_count += 1
            else:
                reasoner_std['query_graph']['nodes']['n{}'.format(node_count)] = {'category': 'biolink:Gene'}
                gene_node_idx = node_count
                node_count += 1

        # add drug node
        drug_node_idx = None
        if drug_node:
            if drug is not None:
                reasoner_std['query_graph']['nodes']['n{}'.format(node_count)] = {'category': 'biolink:Drug',
                                                                                  'id': drug}
                drug_node_idx = node_count
                node_count += 1
            else:
                reasoner_std['query_graph']['nodes']['n{}'.format(node_count)] = {'category': 'biolink:Drug'}
                drug_node_idx = node_count
                node_count += 1

        # add in disease node
        disease_node_idx = node_count
        reasoner_std['query_graph']['nodes']['n{}'.format(node_count)] = {'category': 'biolink:Disease',
                                                                          'id': disease}
        node_count += 1

        # add survival node
        survival_node_idx = None
        if survival_node:
            phenotype = ('Survival_Time', 'EFO:0000714')
            reasoner_std['query_graph']['nodes']['n{}'.format(node_count)] = {'category': 'biolink:PhenotypicFeature',
                                                                              'id': 'EFO:0000714'}
            survival_node_idx = node_count

        # link evidence to disease node
        if gene_node_idx is not None:
            reasoner_std['query_graph']['edges']['e{}'.format(edge_count)] = {
                'predicate': 'biolink:gene_associated_with_condition',
                'subject': 'n{}'.format(gene_node_idx),
                'object': 'n{}'.format(disease_node_idx)}
            edge_count += 1

        if drug_node_idx is not None:
            reasoner_std['query_graph']['edges']['e{}'.format(edge_count)] = {'predicate': 'biolink:treats',
                                                                              'subject': 'n{}'.format(drug_node_idx),
                                                                              'object': 'n{}'.format(disease_node_idx)}
            edge_count += 1

        # link disease to survival node
        if survival_node:
            reasoner_std['query_graph']['edges']['e{}'.format(edge_count)] = {'predicate': 'biolink:has_phenotype',
                                                                              'subject': 'n{}'.format(disease_node_idx),
                                                                              'object': 'n{}'.format(survival_node_idx)}
            if survival_time is not None:
                reasoner_std['query_graph']['edges']['e{}'.format(edge_count)]['properties'] = {'qualifier': '>=',
                                                                                                'days': survival_time}

        return {"message": reasoner_std}

    def query(self, query: dict):
        """
        Sends a query to the Genetics Provider.
        :param query: TRAPI Message JSON object to send to the Genetics Provider
        :return: Query object of the response.
        """
        try:
            response = requests.post(url=ConnectionsHypothesisProvider.url, json=query)
            response.raise_for_status()
        except Exception as e:
            raise e

        # verify it is a TRAPI response
        trapi_response = response.json()
        try:
            reasoner_validator.validate_Query(trapi_response)
        except Exception as e:
            raise e

        return trapi_response
