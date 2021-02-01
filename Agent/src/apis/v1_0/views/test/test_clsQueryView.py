import unittest
import json
import os
from modApp import app
import requests_mock
from apis.v1_0.views.clsQueryView import clsQueryView
from apis.v1_0.views.QueryHandlers.geneticsProvider import GeneticsProvider
from apis.v1_0.views.QueryHandlers.connectionsHypothesisProvider import ConnectionsHypothesisProvider
from apis.v1_0.views.QueryHandlers.multiomicsProvider import MultiomicsProvider
from apis.v1_0.views.QueryHandlers.molecularDataProvider import MolecularDataProvider
import requests


class test_clsQueryView(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.assertEqual.__self__.maxDiff = None

    def tearDown(self):
        self.app = None

    @staticmethod
    def loadJsonFromFile(fileName):
        fullPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), fileName)
        with open(fullPath) as file:
            return json.load(file)

    def test_user_request_body_not_supported(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("General/test_user_request_body_not_supported.json"))
        knowledgeProviderResponseBody = 'garbage'
        queryResponseBody = self.loadJsonFromFile("General/test_query_response_body_not_supported.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', GeneticsProvider.url, text=knowledgeProviderResponseBody)
            response = self.app.post('/v1.0/query', headers={"Content-Type": "application/json"}, data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(queryResponseBody, response.json)

    def test_user_request_body_bad_request(self):
        userRequestBody = 'garbage'
        knowledgeProviderResponseBody = 'not needed'
        queryResponseBody = {"message": "Request contains invalid JSON."}
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', GeneticsProvider.url, text=knowledgeProviderResponseBody)
            response = self.app.post('/v1.0/query', data=userRequestBody, follow_redirects=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual(queryResponseBody, response.json)

    def test_user_request_body_invalid_trapi(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("General/test_user_request_body_invalid_trapi.json"))
        knowledgeProviderResponseBody = 'not needed'
        queryResponseBody = self.loadJsonFromFile("General/test_query_response_body_invalid_trapi.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', GeneticsProvider.url, text=knowledgeProviderResponseBody)
            response = self.app.post('/v1.0/query', data=userRequestBody, follow_redirects=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual(queryResponseBody, response.json)

    def test_knowledge_provider_response_body_unknown_internal_server_error(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("DiseaseAssociatedGene/test_user_request_body_nominal.json"))
        knowledgeProviderResponseBody = "garbage"
        queryResponseBody = self.loadJsonFromFile("General/test_query_response_body_unknown_internal_server_error.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', GeneticsProvider.url, text=knowledgeProviderResponseBody)
            response = self.app.post('/v1.0/query', headers={"Content-Type": "application/json"}, data=userRequestBody, follow_redirects=True)
        self.assertEqual(500, response.status_code)
        self.assertEqual(queryResponseBody, response.json)

    def test_knowledge_provider_http_error(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("DiseaseAssociatedGene/test_user_request_body_nominal.json"))
        expected_message = {"message": clsQueryView.KP_ERROR_RESPONSE}
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', GeneticsProvider.url, exc=requests.exceptions.HTTPError("Bad request"))
            response = self.app.post('/v1.0/query', headers={"Content-Type": "application/json"}, data=userRequestBody, follow_redirects=True)
        self.assertEqual(500, response.status_code)
        self.assertEqual(expected_message, response.json)


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
    #     response = self.app.post('/v1.0/query', headers={"Content-Type": "application/json"}, data=userRequestBody, follow_redirects=True)
    #     self.assertEqual(500, response.status_code)
    #     self.assertEqual(queryResponseBody, response.json)

    # def test_gene_associated_disease_real(self):
    #     userRequestBody = json.dumps(self.loadJsonFromFile("GeneAssociatedDisease/test_user_request_body_nominal.json"))
    #     queryResponseBody = {"message": "Knowledge Provider response body does not conform, have they changed their API?"}
    #     response = self.app.post('/v1.0/query', headers={"Content-Type": "application/json"}, data=userRequestBody, follow_redirects=True)
    #     self.assertEqual(500, response.status_code)
    #     self.assertEqual(queryResponseBody, response.json)

    # def test_disease_associated_gene_contributes_chemical_user_request_body_nominal_live(self):
    #     userRequestBody = json.dumps(self.loadJsonFromFile("DiseaseAssociatedGeneContributesChemicalSubstanceView/test_user_request_body_nominal.json"))
    #     queryResponseBody = self.loadJsonFromFile("DiseaseAssociatedGeneContributesChemicalSubstanceView/test_query_response_body_nominal.json")
    #     response = self.app.post('/v1.0/query', data=userRequestBody, follow_redirects=True)
    #     self.assertEqual(200, response.status_code)
    #     self.assertEqual(queryResponseBody, response.json)


if __name__ == '__main__':
    unittest.main()
