import unittest
import json
import os
from modApp import app
import requests_mock
from apis.v0_9.views.clsQueryView import knowledgeProviderUrl


class test_clsQueryView(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        self.app = None

    @staticmethod
    def loadJsonFromFile(fileName):
        fullPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), fileName)
        with open(fullPath) as file:
            return json.load(file)

    def test_user_request_body_works_with_json_header(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("test_user_request_body_nominal.json"))
        knowledgeProviderResponseBody = json.dumps(self.loadJsonFromFile(
            "test_knowledge_provider_response_body_nominal.json"))
        queryResponseBody = self.loadJsonFromFile("test_query_response_body_nominal.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', knowledgeProviderUrl, text=knowledgeProviderResponseBody)
            response = self.app.post('/v0.9.2/query', headers={"Content-Type": "application/json"}, data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(queryResponseBody, response.json)

    def test_user_request_body_works_with_text_header(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("test_user_request_body_nominal.json"))
        knowledgeProviderResponseBody = json.dumps(self.loadJsonFromFile(
            "test_knowledge_provider_response_body_nominal.json"))
        queryResponseBody = self.loadJsonFromFile("test_query_response_body_nominal.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', knowledgeProviderUrl, text=knowledgeProviderResponseBody)
            response = self.app.post('/v0.9.2/query', headers={"Content-Type": "text/json"}, data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(queryResponseBody, response.json)

    def test_user_request_body_works_without_header(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("test_user_request_body_nominal.json"))
        knowledgeProviderResponseBody = json.dumps(self.loadJsonFromFile(
            "test_knowledge_provider_response_body_nominal.json"))
        queryResponseBody = self.loadJsonFromFile("test_query_response_body_nominal.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', knowledgeProviderUrl, text=knowledgeProviderResponseBody)
            response = self.app.post('/v0.9.2/query', data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(queryResponseBody, response.json)

    def test_user_request_body_not_supported(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("test_user_request_body_not_supported.json"))
        knowledgeProviderResponseBody = 'garbage'
        queryResponseBody = self.loadJsonFromFile("test_query_response_body_empty.json")
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', knowledgeProviderUrl, text=knowledgeProviderResponseBody)
            response = self.app.post('/v0.9.2/query', headers={"Content-Type": "application/json"}, data=userRequestBody, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(queryResponseBody, response.json)

    def test_user_request_body_bad_request(self):
        userRequestBody = 'garbage'
        knowledgeProviderResponseBody = 'also garbage'
        queryResponseBody = {"message": "Supplied request body does not conform"}
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', knowledgeProviderUrl, text=knowledgeProviderResponseBody)
            response = self.app.post('/v0.9.2/query', data=userRequestBody, follow_redirects=True)
        self.assertEqual(400, response.status_code)
        self.assertEqual(queryResponseBody, response.json)

    def test_knowledge_provider_response_body_unknown_internal_server_error(self):
        userRequestBody = json.dumps(self.loadJsonFromFile("test_user_request_body_nominal.json"))
        knowledgeProviderResponseBody = "garbage"
        queryResponseBody = {"message": "Knowledge Provider response body does not conform, have they changed their API?"}
        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', knowledgeProviderUrl, text=knowledgeProviderResponseBody)
            response = self.app.post('/v0.9.2/query', headers={"Content-Type": "application/json"}, data=userRequestBody, follow_redirects=True)
        self.assertEqual(500, response.status_code)
        self.assertEqual(queryResponseBody, response.json)


if __name__ == '__main__':
    unittest.main()
