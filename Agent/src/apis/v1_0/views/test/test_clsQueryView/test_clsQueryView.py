import unittest
import json
import os
from modApp import appFactory
import requests_mock
import requests
from .... import version


class test_clsQueryView(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = appFactory().test_client()
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        cls.client = None

    @staticmethod
    def loadJsonFromFile(fileName):
        fullPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), fileName)
        with open(fullPath) as file:
            return json.load(file)

    def test_user_request_body_works_with_json_header(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("test_user_request_body_not_supported.json"))
        userResponseBody = self.loadJsonFromFile("test_user_response_body_not_supported.json")
        response = self.client.post(f'/{version}/query', headers={"Content-Type": "application/json"}, data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(userResponseBody, response.json)

    def test_user_request_body_works_with_text_header(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("test_user_request_body_not_supported.json"))
        userResponseBody = self.loadJsonFromFile("test_user_response_body_not_supported.json")
        response = self.client.post(f'/{version}/query', headers={"Content-Type": "text/json"}, data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(userResponseBody, response.json)

    def test_user_request_body_works_without_header(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("test_user_request_body_not_supported.json"))
        userResponseBody = self.loadJsonFromFile("test_user_response_body_not_supported.json")
        response = self.client.post(f'/{version}/query', data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(userResponseBody, response.json)

    def test_user_request_body_not_supported(self):
        userRequestBody = self.loadJsonFromFile("test_user_request_body_not_supported.json")
        userResponseBody = self.loadJsonFromFile("test_user_response_body_not_supported.json")
        response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(userResponseBody, response.json)

    def test_user_request_body_not_json(self):
        userRequestBody = 'garbage'
        userResponseBody = {"message": "Request contains invalid JSON."}
        response = self.client.post(f'/{version}/query', data=userRequestBody, follow_redirects=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual(userResponseBody, response.json)

    def test_user_request_body_not_valid_trapi(self):
        userRequestBody = self.loadJsonFromFile("test_user_request_body_invalid_trapi.json")
        userResponseBody = self.loadJsonFromFile("test_user_response_body_invalid_trapi.json")
        response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual(userResponseBody, response.json)

    # def test_knowledge_provider_response_body_unknown_internal_server_error(self):
    #     userRequestBody = json.dumps(self.loadJsonFromFile("DiseaseAssociatedGene/test_user_request_body_nominal.json"))
    #     knowledgeProviderResponseBody = "garbage"
    #     queryResponseBody = self.loadJsonFromFile("General/test_query_response_body_unknown_internal_server_error.json")
    #     with requests_mock.Mocker() as mocker:
    #         mocker.register_uri('POST', clsGeneticsKnowledgeProvider.url, text=knowledgeProviderResponseBody)
    #         response = self.app.post(f'/{version}/query', headers={"Content-Type": "application/json"}, data=userRequestBody, follow_redirects=True)
    #     self.assertEqual(500, response.status_code)
    #     self.assertEqual(queryResponseBody, response.json)

    # def test_knowledge_provider_http_error(self):
    #     userRequestBody = json.dumps(self.loadJsonFromFile("DiseaseAssociatedGene/test_user_request_body_nominal.json"))
    #     expected_message = {"message": clsQueryView.KP_ERROR_RESPONSE}
    #     with requests_mock.Mocker() as mocker:
    #         mocker.register_uri('POST', clsGeneticsKnowledgeProvider.url, exc=requests.exceptions.HTTPError("Bad request"))
    #         response = self.app.post(f'/{version}/query', headers={"Content-Type": "application/json"}, data=userRequestBody, follow_redirects=True)
    #     self.assertEqual(500, response.status_code)
    #     self.assertEqual(expected_message, response.json)


    # def test_knowledge_provider_live(self):
    #     """
    #     Tests if the knowledge provider can be requested and is returning results.
    #     DOES NOT CHECK FOR CONTENT! If we did this test would fail every time their database was updated.
    #     """
    #     userRequestBody = self.loadJsonFromFile("test_user_request_body_nominal.json")
    #     response = requests.post(url=knowledgeProviderUrl, json=userRequestBody)
    #     self.assertEqual(200, response.status_code)

    # def test_disease_associated_gene_real(self):
    #     userRequestBody = json.dumps(self.loadJsonFromFile("test_user_request_body_nominal.json"))
    #     queryResponseBody = {"message": "Knowledge Provider response body does not conform, have they changed their API?"}
    #     response = self.app.post(f'/{version}/query', headers={"Content-Type": "application/json"}, data=userRequestBody, follow_redirects=True)
    #     self.assertEqual(500, response.status_code)
    #     self.assertEqual(queryResponseBody, response.json)

    # def test_gene_associated_disease_real(self):
    #     userRequestBody = json.dumps(self.loadJsonFromFile("GeneAssociatedDisease/test_user_request_body_nominal.json"))
    #     queryResponseBody = {"message": "Knowledge Provider response body does not conform, have they changed their API?"}
    #     response = self.app.post(f'/{version}/query', headers={"Content-Type": "application/json"}, data=userRequestBody, follow_redirects=True)
    #     self.assertEqual(500, response.status_code)
    #     self.assertEqual(queryResponseBody, response.json)

    # def test_disease_associated_gene_contributes_chemical_user_request_body_nominal_live(self):
    #     userRequestBody = json.dumps(self.loadJsonFromFile("clsDiseaseAssociatedGeneContributesChemicalSubstanceWorkflow/test_user_request_body_nominal.json"))
    #     queryResponseBody = self.loadJsonFromFile("clsDiseaseAssociatedGeneContributesChemicalSubstanceWorkflow/test_query_response_body_nominal.json")
    #     response = self.app.post(f'/{version}/query', data=userRequestBody, follow_redirects=True)
    #     self.assertEqual(200, response.status_code)
    #     self.assertEqual(queryResponseBody, response.json)


if __name__ == '__main__':
    unittest.main()
