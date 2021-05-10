import unittest
import json
import os
import requests_mock
import requests
from modApp import appFactory
from ...clsGeneAssociatedDiseaseQuery import clsGeneAssociatedDiseaseQuery
from ....knowledgeProviders.clsConnectionsHypothesisKnowledgeProvider import clsConnectionsHypothesisKnowledgeProvider
from .... import version


class test_clsGeneAssociatedDiseaseQuery(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = appFactory().test_client()
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        cls.client = None

    @staticmethod
    def loadJsonFromFile(fileName, directoryAlias="this"):
        if directoryAlias == "this":
            fullPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), fileName)
        elif directoryAlias == "common":
            fullPath = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "test_clsQuery", fileName)
        else:
            raise AttributeError("'directoryAlias' must be 'this' or 'common'")
        with open(fullPath) as file:
            return json.load(file)

    def test_user_request_body_is_supported(self):
        query = clsGeneAssociatedDiseaseQuery(userRequestBody=self.loadJsonFromFile("test_user_request_body_nominal.json"))
        result = query.userRequestBodyIsSupported()
        self.assertEqual(True, result)

    def test_user_request_body_not_supported(self):
        query = clsGeneAssociatedDiseaseQuery(userRequestBody=self.loadJsonFromFile("test_user_request_body_not_supported.json", directoryAlias="common"))
        result = query.userRequestBodyIsSupported()
        self.assertEqual(False, result)

    def test_query_view(self):
        userRequestBody = self.loadJsonFromFile("test_user_request_body_nominal.json")
        knowledgeProviderResponseBody = self.loadJsonFromFile("test_knowledge_provider_response_body_nominal.json")
        queryResponseBody = self.loadJsonFromFile("test_user_response_body_nominal.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', clsConnectionsHypothesisKnowledgeProvider.url, json=knowledgeProviderResponseBody)
            response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(queryResponseBody, response.json)

    def test_query_view_knowledge_provider_response_body_unknown_internal_server_error(self):
        userRequestBody = self.loadJsonFromFile("test_user_request_body_nominal.json")
        knowledgeProviderResponseBody = "garbage"
        userResponseBody = self.loadJsonFromFile("test_user_response_body_unknown_internal_server_error_from_knowledge_provider.json", directoryAlias="common")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', clsConnectionsHypothesisKnowledgeProvider.url, json=knowledgeProviderResponseBody)
            response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)
        self.assertEqual(500, response.status_code)
        self.assertEqual(userResponseBody, response.json)

    def test_query_view_knowledge_provider_http_error(self):
        userRequestBody = self.loadJsonFromFile("test_user_request_body_nominal.json")
        userResponseBody = self.loadJsonFromFile("test_user_response_body_http_error_from_knowledge_provider.json", directoryAlias="common")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', clsConnectionsHypothesisKnowledgeProvider.url, exc=requests.exceptions.HTTPError("Bad request"))
            response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)
        self.assertEqual(500, response.status_code)
        self.assertEqual(userResponseBody, response.json)


if __name__ == '__main__':
    unittest.main()
