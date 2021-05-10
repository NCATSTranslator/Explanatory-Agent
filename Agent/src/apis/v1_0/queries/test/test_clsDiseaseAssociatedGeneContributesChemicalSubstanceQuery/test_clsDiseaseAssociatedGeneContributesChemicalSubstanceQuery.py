import unittest
import json
import os
import requests_mock
import requests
from modApp import appFactory
from ...clsDiseaseAssociatedGeneContributesChemicalSubstanceQuery import clsDiseaseAssociatedGeneContributesChemicalSubstanceQuery
from ....knowledgeProviders.clsGeneticsKnowledgeProvider import clsGeneticsKnowledgeProvider
from ....knowledgeProviders.clsMultiomicsKnowledgeProvider import clsMultiomicsKnowledgeProvider
from .... import version


class test_clsDiseaseAssociatedGeneContributesChemicalSubstanceQuery(unittest.TestCase):

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
        query = clsDiseaseAssociatedGeneContributesChemicalSubstanceQuery(userRequestBody=self.loadJsonFromFile("test_user_request_body_nominal.json"))
        result = query.userRequestBodyIsSupported()
        self.assertEqual(True, result)

    def test_user_request_body_not_supported(self):
        query = clsDiseaseAssociatedGeneContributesChemicalSubstanceQuery(userRequestBody=self.loadJsonFromFile("test_user_request_body_not_supported.json", directoryAlias="common"))
        result = query.userRequestBodyIsSupported()
        self.assertEqual(False, result)

    def test_query_view_user_request_body_nominal(self):
        userRequestBody = self.loadJsonFromFile("test_user_request_body_nominal.json")
        geneticsKnowledgeProviderResponseBody = self.loadJsonFromFile("test_genetics_knowledge_provider_response_body_nominal.json")
        multiomicsKnowledgeProviderResponseBody = self.loadJsonFromFile("test_multiomics_knowledge_provider_response_body_nominal.json")
        userResponseBody = self.loadJsonFromFile("test_user_response_body_nominal.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', clsGeneticsKnowledgeProvider.url, json=geneticsKnowledgeProviderResponseBody)
            mocker.register_uri('POST', clsMultiomicsKnowledgeProvider.url, json=multiomicsKnowledgeProviderResponseBody)
            response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(userResponseBody, response.json)

    def test_query_view_no_genetics_provider_results(self):
        userRequestBody = self.loadJsonFromFile("test_user_request_body_nominal.json")
        geneticsKnowledgeProviderResponseBody = self.loadJsonFromFile("test_genetics_knowledge_provider_response_body_no_results.json")
        multiomicsKnowledgeProviderResponseBody = self.loadJsonFromFile("test_multiomics_knowledge_provider_response_body_no_results.json")
        userResponseBody = self.loadJsonFromFile("test_user_response_body_genetics_knowledge_provider_no_results.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', clsGeneticsKnowledgeProvider.url, json=geneticsKnowledgeProviderResponseBody)
            mocker.register_uri('POST', clsMultiomicsKnowledgeProvider.url, json=multiomicsKnowledgeProviderResponseBody)
            response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(userResponseBody, response.json)

    def test_query_view_no_multiomics_provider_results(self):
        userRequestBody = self.loadJsonFromFile("test_user_request_body_nominal.json")
        geneticsKnowledgeProviderResponseBody = self.loadJsonFromFile("test_genetics_knowledge_provider_response_body_nominal.json")
        multiomicsKnowledgeProviderResponseBody = self.loadJsonFromFile("test_multiomics_knowledge_provider_response_body_no_results.json")
        userResponseBody = self.loadJsonFromFile("test_user_response_body_multiomics_knowledge_provider_no_results.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', clsGeneticsKnowledgeProvider.url, json=geneticsKnowledgeProviderResponseBody)
            mocker.register_uri('POST', clsMultiomicsKnowledgeProvider.url, json=multiomicsKnowledgeProviderResponseBody)
            response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(userResponseBody, response.json)

    def test_query_view_knowledge_provider_response_body_unknown_internal_server_error(self):
        userRequestBody = self.loadJsonFromFile("test_user_request_body_nominal.json")
        geneticsKnowledgeProviderResponseBody = "garbage"
        multiomicsKnowledgeProviderResponseBody = "garbage"
        userResponseBody = self.loadJsonFromFile("test_user_response_body_unknown_internal_server_error_from_knowledge_provider.json", directoryAlias="common")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', clsGeneticsKnowledgeProvider.url, json=geneticsKnowledgeProviderResponseBody)
            mocker.register_uri('POST', clsMultiomicsKnowledgeProvider.url, json=multiomicsKnowledgeProviderResponseBody)
            response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)
        self.assertEqual(500, response.status_code)
        self.assertEqual(userResponseBody, response.json)

    def test_query_view_knowledge_provider_http_error(self):
        userRequestBody = self.loadJsonFromFile("test_user_request_body_nominal.json")
        userResponseBody = self.loadJsonFromFile("test_user_response_body_http_error_from_knowledge_provider.json", directoryAlias="common")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', clsGeneticsKnowledgeProvider.url, exc=requests.exceptions.HTTPError("Bad request"))
            mocker.register_uri('POST', clsMultiomicsKnowledgeProvider.url, exc=requests.exceptions.HTTPError("Bad request"))
            response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)
        self.assertEqual(500, response.status_code)
        self.assertEqual(userResponseBody, response.json)


if __name__ == '__main__':
    unittest.main()
