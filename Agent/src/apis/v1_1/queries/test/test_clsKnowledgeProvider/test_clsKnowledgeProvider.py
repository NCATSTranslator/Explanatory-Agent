import unittest
import time_machine
from ...clsKnowledgeProvider import clsKnowledgeProvider
import requests_mock
from jsonschema import ValidationError
from requests.exceptions import InvalidSchema, HTTPError
from datetime import datetime


class test_clsKnowledgeProvider(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None
        cls.name = "TestKP"
        cls.url = "http://www.fakewebsite.com/some_endpoint"

    @classmethod
    def tearDownClass(cls):
        cls.name = None
        cls.url = None

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_malformed_request_should_raise(self):
        knowledgeProvider = clsKnowledgeProvider(name=self.name, url=self.url)
        knowledgeProvider.logs = []
        knowledgeProvider.requestBody = None

        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', knowledgeProvider.url)
            with self.assertRaises(ValidationError):
                knowledgeProvider.execute()
        expectedLogs = []
        self.assertEqual(knowledgeProvider.logs, expectedLogs)

    @time_machine.travel(datetime.utcfromtimestamp(0))
    def test_nominal_request_failed_response_should_raise(self):
        knowledgeProvider = clsKnowledgeProvider(name=self.name, url=self.url)
        knowledgeProvider.logs = []
        knowledgeProvider.requestBody = {
            "message": {
                "query_graph": {
                    "edges": {},
                    "nodes": {}
                }
            }
        }

        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', knowledgeProvider.url, status_code=400)
            with self.assertRaises(HTTPError):
                knowledgeProvider.execute()

        expectedLogs = [{
            "timestamp": '1970-01-01T00:00:00',
            "level": "ERROR",
            "code": "KPNotAvailable",
            "message": f"Knowledge Provider {self.url} returned HTTP error code 400"
        }]
        self.assertEqual(knowledgeProvider.logs, expectedLogs)

    @time_machine.travel(datetime.utcfromtimestamp(0))
    def test_nominal_request_malformed_response_should_raise(self):
        knowledgeProvider = clsKnowledgeProvider(name=self.name, url=self.url)
        knowledgeProvider.logs = []
        knowledgeProvider.requestBody = {
            "message": {
                "query_graph": {
                    "edges": {},
                    "nodes": {}
                }
            }
        }
        expectedResponseBody = {}

        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', knowledgeProvider.url, json=expectedResponseBody)
            with self.assertRaises(InvalidSchema):
                knowledgeProvider.execute()

        expectedLogs = [{
            "timestamp": '1970-01-01T00:00:00',
            "level": "ERROR",
            "code": "KPMalformedResponse",
            "message": f"Knowledge Provider {self.url} did not return a valid TRAPI v1.1 response"
        }]
        self.assertEqual(knowledgeProvider.logs, expectedLogs)

    @time_machine.travel(datetime.utcfromtimestamp(0))
    def test_empty_response_should_log_warning(self):
        knowledgeProvider = clsKnowledgeProvider(name=self.name, url=self.url)
        knowledgeProvider.logs = []
        knowledgeProvider.requestBody = {
            "message": {
                "query_graph": {
                    "edges": {},
                    "nodes": {}
                }
            }
        }
        expectedResponseBody = {
            "message": {
                "knowledge_graph": {
                    "edges": {},
                    "nodes": {}
                },
                "query_graph": {
                    "edges": {},
                    "nodes": {}
                },
                "results": []
            }
        }

        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', knowledgeProvider.url, json=expectedResponseBody)
            knowledgeProvider.execute()
        self.assertEqual(knowledgeProvider.responseBody, expectedResponseBody)

        expectedLogs = [{
            "timestamp": '1970-01-01T00:00:00',
            "level": "WARNING",
            "code": "KPEmptyResponse",
            "message": f"Knowledge Provider {self.url} returned an empty knowledge graph"
        }]
        self.assertEqual(knowledgeProvider.logs, expectedLogs)

    def test_nominal_request_nominal_response_is_ok(self):
        knowledgeProvider = clsKnowledgeProvider(name=self.name, url=self.url)
        knowledgeProvider.logs = []
        knowledgeProvider.requestBody = {
            "message": {
                "query_graph": {
                    "edges": {},
                    "nodes": {}
                }
            }
        }
        expectedResponseBody = {
            "message": {
                "knowledge_graph": {
                    "edges": {
                        "eXX": {
                            "object": "some object",
                            "predicate": "biolink:some_predicate",
                            "subject": "some subject"
                        }
                    },
                    "nodes": {
                        "nXX": {
                            "categories": [
                                "biolink:SomeCategory"
                            ],
                            "name": "some name"
                        }
                    }
                },
                "query_graph": {
                    "edges": {},
                    "nodes": {}
                },
                "results": []
            }
        }

        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', knowledgeProvider.url, json=expectedResponseBody)
            knowledgeProvider.execute()
        self.assertEqual(knowledgeProvider.responseBody, expectedResponseBody)
        self.assertEqual(knowledgeProvider.logs, [])


if __name__ == '__main__':
    unittest.main()
