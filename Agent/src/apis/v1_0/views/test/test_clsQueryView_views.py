import unittest
import json
import os
from modApp import app
import requests_mock
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

    def test_disease_associated_gene_user_request_body_nominal(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("DiseaseAssociatedGene/test_user_request_body_nominal.json"))
        knowledgeProviderResponseBody = json.dumps(self.loadJsonFromFile(
            "DiseaseAssociatedGene/test_knowledge_provider_response_body_nominal.json"))
        queryResponseBody = self.loadJsonFromFile("DiseaseAssociatedGene/test_query_response_body_nominal.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', GeneticsProvider.url, text=knowledgeProviderResponseBody)
            response = self.app.post('/v1.0/query', data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(queryResponseBody, response.json)

    def test_gene_associated_disease_user_request_body_nominal(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("GeneAssociatedDisease/test_user_request_body_nominal.json"))
        knowledgeProviderResponseBody = json.dumps(self.loadJsonFromFile(
            "GeneAssociatedDisease/test_knowledge_provider_response_body_nominal.json"))
        queryResponseBody = self.loadJsonFromFile("GeneAssociatedDisease/test_query_response_body_nominal.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', ConnectionsHypothesisProvider.url, text=knowledgeProviderResponseBody)
            response = self.app.post('/v1.0/query', data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual.__self__.maxDiff = None
        self.assertEqual(queryResponseBody, response.json)

    def test_drug_associated_disease_user_request_body_nominal(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("DrugAssociatedDisease/test_user_request_body_nominal.json"))
        knowledgeProviderResponseBody = json.dumps(self.loadJsonFromFile(
            "DrugAssociatedDisease/test_knowledge_provider_response_body_nominal.json"))
        queryResponseBody = self.loadJsonFromFile("DrugAssociatedDisease/test_query_response_body_nominal.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', ConnectionsHypothesisProvider.url, text=knowledgeProviderResponseBody)
            response = self.app.post('/v1.0/query', data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(queryResponseBody, response.json)

    def test_disease_associated_gene_contributes_chemical_user_request_body_nominal(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("DiseaseAssociatedGeneContributesChemicalSubstanceView/test_user_request_body_nominal.json"))
        geneticsResponseBody = json.dumps(self.loadJsonFromFile("DiseaseAssociatedGeneContributesChemicalSubstanceView/test_genetics_provider_response_body_nominal.json"))
        multiomicsResponseBody = json.dumps(self.loadJsonFromFile("DiseaseAssociatedGeneContributesChemicalSubstanceView/test_multiomics_provider_response_body_nominal.json"))
        queryResponseBody = self.loadJsonFromFile("DiseaseAssociatedGeneContributesChemicalSubstanceView/test_query_response_body_nominal.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', GeneticsProvider.url, text=geneticsResponseBody)
            mocker.register_uri('POST', MultiomicsProvider.url, text=multiomicsResponseBody)
            response = self.app.post('/v1.0/query', data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(queryResponseBody, response.json)

    def test_disease_associated_gene_contributes_chemical_user_request_body_no_genetics_provider_results(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("DiseaseAssociatedGeneContributesChemicalSubstanceView/test_user_request_body_nominal.json"))
        geneticsResponseBody = json.dumps(self.loadJsonFromFile("DiseaseAssociatedGeneContributesChemicalSubstanceView/test_genetics_provider_response_body_no_results.json"))
        multiomicsResponseBody = json.dumps(self.loadJsonFromFile("DiseaseAssociatedGeneContributesChemicalSubstanceView/test_multiomics_provider_response_body_no_results.json"))
        queryResponseBody = self.loadJsonFromFile("DiseaseAssociatedGeneContributesChemicalSubstanceView/test_query_response_body_genetics_provider_no_results.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', GeneticsProvider.url, text=geneticsResponseBody)
            mocker.register_uri('POST', MultiomicsProvider.url, text=multiomicsResponseBody)
            response = self.app.post('/v1.0/query', data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(queryResponseBody, response.json)

    def test_disease_associated_gene_contributes_chemical_user_request_body_no_multiomics_provider_results(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("DiseaseAssociatedGeneContributesChemicalSubstanceView/test_user_request_body_nominal.json"))
        geneticsResponseBody = json.dumps(self.loadJsonFromFile("DiseaseAssociatedGeneContributesChemicalSubstanceView/test_genetics_provider_response_body_nominal.json"))
        multiomicsResponseBody = json.dumps(self.loadJsonFromFile("DiseaseAssociatedGeneContributesChemicalSubstanceView/test_multiomics_provider_response_body_no_results.json"))
        queryResponseBody = self.loadJsonFromFile("DiseaseAssociatedGeneContributesChemicalSubstanceView/test_query_response_body_multiomics_provider_no_results.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', GeneticsProvider.url, text=geneticsResponseBody)
            mocker.register_uri('POST', MultiomicsProvider.url, text=multiomicsResponseBody)
            response = self.app.post('/v1.0/query', data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(queryResponseBody, response.json)
        
    def test_disease_to_chemical_user_request_body_nominal(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("DiseaseToChemicalView/test_user_request_body_nominal.json"))
        knowledgeProviderResponseBody = json.dumps(self.loadJsonFromFile("DiseaseToChemicalView/test_molepro_response_body_nominal.json"))
        queryResponseBody = self.loadJsonFromFile("DiseaseToChemicalView/test_query_response_body_nominal.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', MolecularDataProvider.url, text=knowledgeProviderResponseBody)
            response = self.app.post('/v1.0/query', data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(queryResponseBody, response.json)

    # def test_live(self):
    #     userRequestBody = json.dumps(self.loadJsonFromFile("DrugAssociatedDisease/test_user_request_body_nominal.json"))
    #     queryResponseBody = self.loadJsonFromFile("DiseaseAssociatedGeneContributesChemicalSubstanceView/test_query_response_body_nominal.json")
    #     response = self.app.post('/v1.0/query', data=userRequestBody, follow_redirects=True)
    #     self.assertEqual(200, response.status_code)
    #     self.assertEqual(queryResponseBody, response.json)


if __name__ == '__main__':
    unittest.main()
