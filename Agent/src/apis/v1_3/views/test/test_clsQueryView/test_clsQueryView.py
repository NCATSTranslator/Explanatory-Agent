import unittest
from unittest.mock import MagicMock, patch
from mockito import when, unstub
import requests_mock
from modApp import appFactory
from .... import version
from modDatabase import db
import os
import json
from ....queries.clsCaseSolutionManager import clsCaseSolutionManager
from ....queries.clsCategoriesProvider import clsCategoriesProvider
from ....queries.clsCurieIdsProvider import clsCurieIdsProvider
from ....queries.clsKnowledgeProvider import clsKnowledgeProvider
import time_machine
from datetime import datetime


class test_clsQueryView(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = appFactory().test_client()
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        cls.client = None

    def setUp(self):
        unstub()
        when(db).create_scoped_session().thenReturn(MagicMock())  # mocked session

    def tearDown(self):
        unstub()

    @staticmethod
    def loadJsonFromFile(fileName):
        fullPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), fileName)
        with open(fullPath) as file:
            return json.load(file)

    def test_user_request_body_not_json(self):
        userRequestBody = 'garbage'
        expectedUserResponseBody = self.loadJsonFromFile("test_user_response_body_bad_json.json")
        response = self.client.post(f'/{version}/query', data=userRequestBody, follow_redirects=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual(expectedUserResponseBody, response.json)

    def test_user_request_body_invalid_trapi(self):
        userRequestBody = self.loadJsonFromFile("test_user_request_body_bad_constraint_invalid_trapi.json")
        expectedUserResponseBody = self.loadJsonFromFile("test_user_response_body_bad_constraint_invalid_trapi.json")
        response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual(expectedUserResponseBody, response.json)

    def test_user_request_body_works_with_json_header(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("test_user_request_body_one_node_not_supported.json"))
        expectedUserResponseBody = self.loadJsonFromFile("test_user_response_body_one_node_not_supported.json")
        response = self.client.post(f'/{version}/query', headers={"Content-Type": "application/json"}, data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(expectedUserResponseBody, response.json)

    def test_user_request_body_works_with_text_header(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("test_user_request_body_one_node_not_supported.json"))
        expectedUserResponseBody = self.loadJsonFromFile("test_user_response_body_one_node_not_supported.json")
        response = self.client.post(f'/{version}/query', headers={"Content-Type": "text/json"}, data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(expectedUserResponseBody, response.json)

    def test_user_request_body_works_without_header(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("test_user_request_body_one_node_not_supported.json"))
        expectedUserResponseBody = self.loadJsonFromFile("test_user_response_body_one_node_not_supported.json")
        response = self.client.post(f'/{version}/query', data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(expectedUserResponseBody, response.json)

    def test_user_request_body_not_supported(self):
        userRequestBody = self.loadJsonFromFile("test_user_request_body_one_node_not_supported.json")
        expectedUserResponseBody = self.loadJsonFromFile("test_user_response_body_one_node_not_supported.json")
        response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(expectedUserResponseBody, response.json)

    def test_user_request_body_nominal_case_id_not_found_not_supported(self):

        userRequestBody = self.loadJsonFromFile("path1/test_user_request_body_nominal.json")

        # findMostSimilarCases
        sqlFindMostSimilarCases = clsCaseSolutionManager.sqlFindMostSimilarCases
        paramsFindMostSimilarCases = {
            "similarSubjectsVar": tuple(userRequestBody['message']['query_graph']['nodes']['n00']['categories']),
            "similarObjectsVar": tuple(userRequestBody['message']['query_graph']['nodes']['n01']['categories']),
            "similarPredicatesVar": tuple(userRequestBody['message']['query_graph']['edges']['e00']['predicates'])
        }
        resultsFindMostSimilarCases = []

        when(db.session).\
            execute(statement=sqlFindMostSimilarCases, params=paramsFindMostSimilarCases).\
            thenReturn(MagicMock())  # mock cursor
        when(db.session.execute(statement=sqlFindMostSimilarCases, params=paramsFindMostSimilarCases)).\
            fetchall().\
            thenReturn(resultsFindMostSimilarCases)  # mock results

        response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)

        expectedUserResponseBody = self.loadJsonFromFile("test_user_response_body_case_id_not_found_not_supported.json")

        self.assertEqual(200, response.status_code)
        self.assertEqual(expectedUserResponseBody, response.json)

    @patch.object(clsKnowledgeProvider, "timeoutSeconds", new=None)
    @time_machine.travel(datetime.utcfromtimestamp(0))
    def test_user_request_body_nominal_knowledge_provider_crash(self):

        userRequestBody = self.loadJsonFromFile("path1/test_user_request_body_nominal.json")

        # findMostSimilarCases
        sqlFindMostSimilarCases = clsCaseSolutionManager.sqlFindMostSimilarCases
        paramsFindMostSimilarCases = {
            "similarSubjectsVar": tuple(userRequestBody['message']['query_graph']['nodes']['n00']['categories']),
            "similarObjectsVar": tuple(userRequestBody['message']['query_graph']['nodes']['n01']['categories']),
            "similarPredicatesVar": tuple(userRequestBody['message']['query_graph']['edges']['e00']['predicates'])
        }
        resultsFindMostSimilarCases = [{
            "CaseId": "Q000019"
        }]
        when(db.session).\
            execute(statement=sqlFindMostSimilarCases, params=paramsFindMostSimilarCases).\
            thenReturn(MagicMock())  # mock cursor
        when(db.session.execute(statement=sqlFindMostSimilarCases, params=paramsFindMostSimilarCases)).\
            fetchall().\
            thenReturn(resultsFindMostSimilarCases)  # mock results

        # findCaseSolutions
        sqlFindCaseSolutions = clsCaseSolutionManager.sqlFindCaseSolutions
        paramsFindCaseSolutions = {
            "caseIdVar": "Q000019"
        }
        resultsFindCaseSolutions = [{
            "Id": 1271,
            "CaseId": "Q000019",
            "KnowledgeProviderPathCount": 1,
            "Node1Path1Category": "biolink:ChemicalSubstance",
            "Node2Path1Category": "biolink:Gene",
            "Edge1Path1Predicate": "biolink:correlated_with",
            "KnowledgeProviderPath1Name": "MolePro",
            "KnowledgeProviderPath1Url": "https://translator.broadinstitute.org/molepro/trapi/v1.1/query"
        }]
        when(db.session).\
            execute(statement=sqlFindCaseSolutions, params=paramsFindCaseSolutions).\
            thenReturn(MagicMock())  # mock cursor
        when(db.session.execute(statement=sqlFindCaseSolutions, params=paramsFindCaseSolutions)).\
            fetchall().\
            thenReturn(resultsFindCaseSolutions)  # mock results

        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', "https://translator.broadinstitute.org/molepro/trapi/v1.1/query", status_code=418)  # some crash
            response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)

        expectedUserResponseBody = self.loadJsonFromFile("test_user_response_body_knowledge_provider_crash.json")

        self.assertEqual(500, response.status_code)
        self.assertEqual(expectedUserResponseBody, response.json)

    @patch.object(clsCurieIdsProvider, "timeoutSeconds", new=None)
    def test_user_request_body_curie_ids_lookup_crash(self):

        userRequestBody = self.loadJsonFromFile("lookups/test_user_request_body_curie_ids_lookup.json")

        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', clsCurieIdsProvider.url, status_code=418)  # some crash
            response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)

        expectedUserResponseBody = self.loadJsonFromFile("test_user_response_body_curie_ids_provider_crash.json")

        self.assertEqual(500, response.status_code)
        self.assertEqual(expectedUserResponseBody, response.json)

    @patch.object(clsCurieIdsProvider, "timeoutSeconds", new=None)
    @patch.object(clsCategoriesProvider, "timeoutSeconds", new=None)
    @patch.object(clsKnowledgeProvider, "timeoutSeconds", new=None)
    def test_user_request_body_curie_ids_lookup_path_1_works(self):

        userRequestBody = self.loadJsonFromFile("lookups/test_user_request_body_curie_ids_lookup.json")

        # findMostSimilarCases
        sqlFindMostSimilarCases = clsCaseSolutionManager.sqlFindMostSimilarCases
        paramsFindMostSimilarCases = {
            "similarSubjectsVar": tuple(["biolink:ChemicalSubstance"]),
            "similarObjectsVar": tuple(userRequestBody['message']['query_graph']['nodes']['n01']['categories']),
            "similarPredicatesVar": tuple(userRequestBody['message']['query_graph']['edges']['e00']['predicates'])
        }
        resultsFindMostSimilarCases = [{
            "CaseId": "Q000019",
        }]
        when(db.session).\
            execute(statement=sqlFindMostSimilarCases, params=paramsFindMostSimilarCases).\
            thenReturn(MagicMock())  # mock cursor
        when(db.session.execute(statement=sqlFindMostSimilarCases, params=paramsFindMostSimilarCases)).\
            fetchall().\
            thenReturn(resultsFindMostSimilarCases)  # mock results

        # findCaseSolutions
        sqlFindCaseSolutions = clsCaseSolutionManager.sqlFindCaseSolutions
        paramsFindCaseSolutions = {
            "caseIdVar": "Q000019"
        }
        resultsFindCaseSolutions = [{
            "Id": 1271,
            "CaseId": "Q000019",
            "KnowledgeProviderPathCount": 1,
            "Node1Path1Category": "biolink:ChemicalSubstance",
            "Node2Path1Category": "biolink:Gene",
            "Edge1Path1Predicate": "biolink:correlated_with",
            "KnowledgeProviderPath1Name": "MolePro",
            "KnowledgeProviderPath1Url": "https://translator.broadinstitute.org/molepro/trapi/v1.1/query"
        }]
        when(db.session).\
            execute(statement=sqlFindCaseSolutions, params=paramsFindCaseSolutions).\
            thenReturn(MagicMock())  # mock cursor
        when(db.session.execute(statement=sqlFindCaseSolutions, params=paramsFindCaseSolutions)).\
            fetchall().\
            thenReturn(resultsFindCaseSolutions)  # mock results

        curieIdsProviderResponseBody = self.loadJsonFromFile("lookups/test_curie_ids_provider_response_body.json")
        categoriesProviderResponseBody = self.loadJsonFromFile("lookups/test_categories_provider_response_body.json")
        knowledgeProviderPath1ResponseBody = self.loadJsonFromFile("path1/test_knowledge_provider_response_body_path_1.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', clsCurieIdsProvider.url, json=curieIdsProviderResponseBody)
            mocker.register_uri('POST', clsCategoriesProvider.url, json=categoriesProviderResponseBody)
            mocker.register_uri('POST', "https://translator.broadinstitute.org/molepro/trapi/v1.1/query", json=knowledgeProviderPath1ResponseBody)
            response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)

        expectedUserResponseBody = self.loadJsonFromFile("path1/test_user_response_body_nominal.json")

        self.assertEqual(200, response.status_code)
        self.assertEqual(expectedUserResponseBody, response.json)

    @patch.object(clsCategoriesProvider, "timeoutSeconds", new=None)
    def test_user_request_body_categories_lookup_crash(self):

        userRequestBody = self.loadJsonFromFile("lookups/test_user_request_body_categories_lookup.json")

        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', clsCategoriesProvider.url, status_code=418)  # some crash
            response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)

        expectedUserResponseBody = self.loadJsonFromFile("test_user_response_body_categories_provider_crash.json")

        self.assertEqual(500, response.status_code)
        self.assertEqual(expectedUserResponseBody, response.json)

    @patch.object(clsCategoriesProvider, "timeoutSeconds", new=None)
    @patch.object(clsKnowledgeProvider, "timeoutSeconds", new=None)
    def test_user_request_body_categories_lookup_path_1_works(self):

        userRequestBody = self.loadJsonFromFile("lookups/test_user_request_body_categories_lookup.json")

        # findMostSimilarCases
        sqlFindMostSimilarCases = clsCaseSolutionManager.sqlFindMostSimilarCases
        paramsFindMostSimilarCases = {
            "similarSubjectsVar": tuple(["biolink:ChemicalSubstance"]),
            "similarObjectsVar": tuple(userRequestBody['message']['query_graph']['nodes']['n01']['categories']),
            "similarPredicatesVar": tuple(userRequestBody['message']['query_graph']['edges']['e00']['predicates'])
        }
        resultsFindMostSimilarCases = [{
            "CaseId": "Q000019",
        }]
        when(db.session).\
            execute(statement=sqlFindMostSimilarCases, params=paramsFindMostSimilarCases).\
            thenReturn(MagicMock())  # mock cursor
        when(db.session.execute(statement=sqlFindMostSimilarCases, params=paramsFindMostSimilarCases)).\
            fetchall().\
            thenReturn(resultsFindMostSimilarCases)  # mock results

        # findCaseSolutions
        sqlFindCaseSolutions = clsCaseSolutionManager.sqlFindCaseSolutions
        paramsFindCaseSolutions = {
            "caseIdVar": "Q000019"
        }
        resultsFindCaseSolutions = [{
            "Id": 1271,
            "CaseId": "Q000019",
            "KnowledgeProviderPathCount": 1,
            "Node1Path1Category": "biolink:ChemicalSubstance",
            "Node2Path1Category": "biolink:Gene",
            "Edge1Path1Predicate": "biolink:correlated_with",
            "KnowledgeProviderPath1Name": "MolePro",
            "KnowledgeProviderPath1Url": "https://translator.broadinstitute.org/molepro/trapi/v1.1/query"
        }]
        when(db.session).\
            execute(statement=sqlFindCaseSolutions, params=paramsFindCaseSolutions).\
            thenReturn(MagicMock())  # mock cursor
        when(db.session.execute(statement=sqlFindCaseSolutions, params=paramsFindCaseSolutions)).\
            fetchall().\
            thenReturn(resultsFindCaseSolutions)  # mock results

        categoriesProviderResponseBody = self.loadJsonFromFile("lookups/test_categories_provider_response_body.json")
        knowledgeProviderPath1ResponseBody = self.loadJsonFromFile("path1/test_knowledge_provider_response_body_path_1.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', clsCategoriesProvider.url, json=categoriesProviderResponseBody)
            mocker.register_uri('POST', "https://translator.broadinstitute.org/molepro/trapi/v1.1/query", json=knowledgeProviderPath1ResponseBody)
            response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)

        expectedUserResponseBody = self.loadJsonFromFile("path1/test_user_response_body_nominal.json")

        self.assertEqual(200, response.status_code)
        self.assertEqual(expectedUserResponseBody, response.json)

    @patch.object(clsKnowledgeProvider, "timeoutSeconds", new=None)
    def test_user_request_body_nominal_path_1_works(self):

        userRequestBody = self.loadJsonFromFile("path1/test_user_request_body_nominal.json")

        # findMostSimilarCases
        sqlFindMostSimilarCases = clsCaseSolutionManager.sqlFindMostSimilarCases
        paramsFindMostSimilarCases = {
            "similarSubjectsVar": tuple(userRequestBody['message']['query_graph']['nodes']['n00']['categories']),
            "similarObjectsVar": tuple(userRequestBody['message']['query_graph']['nodes']['n01']['categories']),
            "similarPredicatesVar": tuple(userRequestBody['message']['query_graph']['edges']['e00']['predicates'])
        }
        resultsFindMostSimilarCases = [{
            "CaseId": "Q000019",
        }]
        when(db.session).\
            execute(statement=sqlFindMostSimilarCases, params=paramsFindMostSimilarCases).\
            thenReturn(MagicMock())  # mock cursor
        when(db.session.execute(statement=sqlFindMostSimilarCases, params=paramsFindMostSimilarCases)).\
            fetchall().\
            thenReturn(resultsFindMostSimilarCases)  # mock results

        # findCaseSolutions
        sqlFindCaseSolutions = clsCaseSolutionManager.sqlFindCaseSolutions
        paramsFindCaseSolutions = {
            "caseIdVar": "Q000019"
        }
        resultsFindCaseSolutions = [{
            "Id": 1271,
            "CaseId": "Q000019",
            "KnowledgeProviderPathCount": 1,
            "Node1Path1Category": "biolink:ChemicalSubstance",
            "Node2Path1Category": "biolink:Gene",
            "Edge1Path1Predicate": "biolink:correlated_with",
            "KnowledgeProviderPath1Name": "MolePro",
            "KnowledgeProviderPath1Url": "https://translator.broadinstitute.org/molepro/trapi/v1.1/query"
        }]
        when(db.session).\
            execute(statement=sqlFindCaseSolutions, params=paramsFindCaseSolutions).\
            thenReturn(MagicMock())  # mock cursor
        when(db.session.execute(statement=sqlFindCaseSolutions, params=paramsFindCaseSolutions)).\
            fetchall().\
            thenReturn(resultsFindCaseSolutions)  # mock results

        knowledgeProviderPath1ResponseBody = self.loadJsonFromFile("path1/test_knowledge_provider_response_body_path_1.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', "https://translator.broadinstitute.org/molepro/trapi/v1.1/query", json=knowledgeProviderPath1ResponseBody)
            response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)

        expectedUserResponseBody = self.loadJsonFromFile("path1/test_user_response_body_nominal.json")

        self.assertEqual(200, response.status_code)
        self.assertEqual(expectedUserResponseBody, response.json)

    @patch.object(clsKnowledgeProvider, "timeoutSeconds", new=None)
    def test_user_request_body_nominal_path_2_works(self):

        userRequestBody = self.loadJsonFromFile("path2/test_user_request_body_nominal.json")

        # findMostSimilarCases
        sqlFindMostSimilarCases = clsCaseSolutionManager.sqlFindMostSimilarCases
        paramsFindMostSimilarCases = {
            "similarSubjectsVar": tuple(userRequestBody['message']['query_graph']['nodes']['n00']['categories']),
            "similarObjectsVar": tuple(userRequestBody['message']['query_graph']['nodes']['n01']['categories']),
            "similarPredicatesVar": tuple(userRequestBody['message']['query_graph']['edges']['e00']['predicates'])
        }
        resultsFindMostSimilarCases = [{
            "CaseId": "Q000094",
        }]
        when(db.session).\
            execute(statement=sqlFindMostSimilarCases, params=paramsFindMostSimilarCases).\
            thenReturn(MagicMock())  # mock cursor
        when(db.session.execute(statement=sqlFindMostSimilarCases, params=paramsFindMostSimilarCases)).\
            fetchall().\
            thenReturn(resultsFindMostSimilarCases)  # mock results

        # findCaseSolutions
        sqlFindCaseSolutions = clsCaseSolutionManager.sqlFindCaseSolutions
        paramsFindCaseSolutions = {
            "caseIdVar": "Q000094"
        }
        resultsFindCaseSolutions = [{
            "Id": 2,
            "CaseId": "Q000094",
            "KnowledgeProviderPathCount": 2,
            "Node1Path1Category": "biolink:ChemicalSubstance",
            "Node2Path1Category": "biolink:Gene",
            "Edge1Path1Predicate": "biolink:correlated_with",
            "KnowledgeProviderPath1Name": "MolePro",
            "KnowledgeProviderPath1Url": "https://translator.broadinstitute.org/molepro/trapi/v1.1/query",
            "Node1Path2Category": "biolink:Gene",
            "Node2Path2Category": "biolink:Disease",
            "Edge1Path2Predicate": "biolink:gene_associated_with_condition",
            "KnowledgeProviderPath2Name": "Genetics",
            "KnowledgeProviderPath2Url": "https://translator.broadinstitute.org/genetics_provider/trapi/v1.1/query"
        }]
        when(db.session).\
            execute(statement=sqlFindCaseSolutions, params=paramsFindCaseSolutions).\
            thenReturn(MagicMock())  # mock cursor
        when(db.session.execute(statement=sqlFindCaseSolutions, params=paramsFindCaseSolutions)).\
            fetchall().\
            thenReturn(resultsFindCaseSolutions)  # mock results

        knowledgeProviderPath1ResponseBody = self.loadJsonFromFile("path2/test_knowledge_provider_response_body_path_1.json")
        knowledgeProviderPath2ResponseBody = self.loadJsonFromFile("path2/test_knowledge_provider_response_body_path_2.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', "https://translator.broadinstitute.org/molepro/trapi/v1.1/query", json=knowledgeProviderPath1ResponseBody)
            mocker.register_uri('POST', "https://translator.broadinstitute.org/genetics_provider/trapi/v1.1/query", json=knowledgeProviderPath2ResponseBody)
            response = self.client.post(f'/{version}/query', json=userRequestBody, follow_redirects=True)

        expectedUserResponseBody = self.loadJsonFromFile("path2/test_user_response_body_nominal.json")

        self.assertEqual(200, response.status_code)
        self.assertEqual(expectedUserResponseBody, response.json)


if __name__ == '__main__':
    unittest.main()
