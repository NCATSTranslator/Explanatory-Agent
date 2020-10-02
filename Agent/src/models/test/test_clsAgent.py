import unittest
from ..clsAgent import clsAgent
import json
import os
from inspect import stack


class test_clsAgent(unittest.TestCase):

    @staticmethod
    def loadJsonFromFile(fileName):
        fullPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), fileName)
        with open(fullPath) as file:
            return json.load(file)

    def test_user_request_body_nominal(self):
        self.assertEqual(True, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_nominal_swapped_sub_nodes(self):
        self.assertEqual(True, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_nominal_swapped_edges_and_nodes(self):
        self.assertEqual(True, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_nominal_swapped_edges_and_nodes_and_sub_nodes(self):
        self.assertEqual(True, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_not_dictionary(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_message_missing(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_message_with_extra_field(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_message_not_dictionary(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_query_graph_missing(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_query_graph_with_extra_field(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_query_graph_not_dictionary(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_edges_or_nodes_missing(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_edges_not_list(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_nodes_not_list(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_edges_length_1(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_nodes_length_2(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_edge_not_dictionary(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_disease_node_not_dictionary(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_gene_node_not_dictionary(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_node_keys_invalid(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_node_disease_invalid(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_edge_type_invalid(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_edge_id_null(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_edge_id_blank(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_edge_source_id_null(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_edge_source_id_blank(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_edge_target_id_null(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_edge_target_id_blank(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_disease_ids_mismatch(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_gene_ids_mismatch(self):
        self.assertEqual(False, clsAgent().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_knowledge_provider_response_body_nominal(self):
        self.assertEqual(True, clsAgent().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_knowledge_provider_response_body_not_dictionary(self):
        self.assertEqual(False, clsAgent().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_knowledge_provider_response_body_knowledge_graph_with_extra_field(self):
        self.assertEqual(False, clsAgent().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_knowledge_provider_response_body_knowledge_graph_missing(self):
        self.assertEqual(False, clsAgent().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_knowledge_provider_response_body_edges_or_nodes_missing(self):
        self.assertEqual(False, clsAgent().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_knowledge_provider_response_body_edge_keys_invalid(self):
        self.assertEqual(False, clsAgent().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_knowledge_provider_response_body_edge_not_dictionary(self):
        self.assertEqual(False, clsAgent().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_knowledge_provider_response_body_node_keys_invalid(self):
        self.assertEqual(False, clsAgent().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_knowledge_provider_response_body_node_not_dictionary(self):
        self.assertEqual(False, clsAgent().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_results_body_nominal(self):
        expectedBody = self.loadJsonFromFile(stack()[0][3] + ".json")
        agent = clsAgent()
        agent.query_graph = expectedBody['query_graph']
        agent.knowledge_graph = expectedBody['knowledge_graph']
        agent.generateResults()
        self.assertEqual(expectedBody['results'], agent.results)


if __name__ == '__main__':
    unittest.main()
