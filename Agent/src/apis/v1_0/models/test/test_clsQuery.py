import unittest
from apis.v1_0.models.clsQuery import clsQuery
import json
import os
from inspect import stack


class test_clsQuery(unittest.TestCase):

    @staticmethod
    def loadJsonFromFile(fileName):
        fullPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), fileName)
        with open(fullPath) as file:
            return json.load(file)

    # def test_user_request_body_nominal(self):
    #     self.assertEqual(True, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_nominal_swapped_sub_nodes(self):
    #     self.assertEqual(True, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_nominal_swapped_edges_and_nodes(self):
    #     self.assertEqual(True, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_nominal_swapped_edges_and_nodes_and_sub_nodes(self):
    #     self.assertEqual(True, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_not_dictionary(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_message_missing(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_message_with_extra_field(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_message_not_dictionary(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_query_graph_missing(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_query_graph_with_extra_field(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_query_graph_not_dictionary(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_edges_or_nodes_missing(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_edges_not_list(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_nodes_not_list(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_edge_not_dictionary(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_disease_node_not_dictionary(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_gene_node_not_dictionary(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_nominal_is_valid(self):
        self.assertEqual(True, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_user_request_body_bad_schema_not_valid(self):
        self.assertEqual(False, clsQuery().userRequestBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    # def test_user_request_body_nominal_is_supported(self):
    #     self.assertEqual(True, clsQuery().userRequestBodyIsSupported(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_node_disease_not_supported(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsSupported(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_edge_type_not_supported(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsSupported(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_disease_ids_mismatch_not_supported(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsSupported(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_edge_id_blank_not_supported(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsSupported(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_edge_subject_id_null_not_supported(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsSupported(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_edge_subject_id_blank_not_supported(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsSupported(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_edge_object_id_null_not_supported(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsSupported(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_edge_object_id_blank_not_supported(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsSupported(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_edges_length_not_equal_1_not_supported(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsSupported(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_nodes_length_not_equal_2_not_supported(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsSupported(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_gene_ids_mismatch_not_supported(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsSupported(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_node_keys_not_supported(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsSupported(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_user_request_body_edge_keys_not_supported(self):
    #     self.assertEqual(False, clsQuery().userRequestBodyIsSupported(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_knowledge_provider_response_body_nominal_is_valid(self):
        self.assertEqual(True, clsQuery().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))

    def test_knowledge_provider_response_body_bad_schema_not_valid(self):
        self.assertEqual(False, clsQuery().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))


    # def test_knowledge_provider_response_body_nominal(self):
    #     self.assertEqual(True, clsQuery().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_knowledge_provider_response_body_not_dictionary(self):
    #     self.assertEqual(False, clsQuery().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_knowledge_provider_response_body_knowledge_graph_with_extra_field(self):
    #     self.assertEqual(False, clsQuery().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_knowledge_provider_response_body_knowledge_graph_missing(self):
    #     self.assertEqual(False, clsQuery().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_knowledge_provider_response_body_edges_or_nodes_missing(self):
    #     self.assertEqual(False, clsQuery().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_knowledge_provider_response_body_edge_keys_invalid(self):
    #     self.assertEqual(False, clsQuery().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_knowledge_provider_response_body_edge_not_dictionary(self):
    #     self.assertEqual(False, clsQuery().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_knowledge_provider_response_body_node_keys_invalid(self):
    #     self.assertEqual(False, clsQuery().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_knowledge_provider_response_body_node_not_dictionary(self):
    #     self.assertEqual(False, clsQuery().knowledgeProviderResponseBodyIsValid(self.loadJsonFromFile(stack()[0][3] + ".json")))
    #
    # def test_results_body_nominal(self):
    #     expectedBody = self.loadJsonFromFile(stack()[0][3] + ".json")
    #     query = clsQuery()
    #     query.query_graph = expectedBody['query_graph']
    #     query.knowledge_graph = expectedBody['knowledge_graph']
    #     query.generateResults()
    #     self.assertEqual(expectedBody['results'], query.results)


if __name__ == '__main__':
    unittest.main()
