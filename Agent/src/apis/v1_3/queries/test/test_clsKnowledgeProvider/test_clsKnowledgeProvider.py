import unittest
from unittest.mock import patch
import time_machine
from ...clsKnowledgeProvider import clsKnowledgeProvider
import requests_mock
from jsonschema import ValidationError
from requests.exceptions import InvalidSchema, HTTPError
from datetime import datetime
from utils.clsLog import clsLogEvent
import json


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

    @patch.object(clsKnowledgeProvider, "timeoutSeconds", new=None)
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

    @patch.object(clsKnowledgeProvider, "timeoutSeconds", new=None)
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

        expectedLogs = [
            clsLogEvent("TestKP", "DEBUG", "", f"Sending request to Knowledge Provider {self.url}..."),
            clsLogEvent("TestKP", "ERROR", "KPNotAvailable", f"Knowledge Provider {self.url} returned HTTP error code 400 for message: {knowledgeProvider.requestBody}"),
        ]

        self.assertEqual(knowledgeProvider.logs, expectedLogs)

    @patch.object(clsKnowledgeProvider, "timeoutSeconds", new=None)
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

        expectedLogs = [
            clsLogEvent("TestKP", "DEBUG", "", f"Sending request to Knowledge Provider {self.url}..."),
            clsLogEvent("TestKP", "DEBUG", "", f"KP 200 response in 0:00:00.000471. Content size: 118."),
            clsLogEvent("TestKP", "ERROR", "KPMalformedResponse", f"Knowledge Provider {self.url} did not return a valid TRAPI v1.3.0 response for message: {knowledgeProvider.requestBody}"),
        ]

        self.assertEqual(len(knowledgeProvider.logs), len(expectedLogs))
        self.assertEqual(knowledgeProvider.logs[0], expectedLogs[0])
        # skipping log [1], due to the message including a timing string that varies
        self.assertEqual(knowledgeProvider.logs[2], expectedLogs[2])

    @patch.object(clsKnowledgeProvider, "timeoutSeconds", new=None)
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

        with requests_mock.Mocker(real_http=True) as mocker:
            mocker.register_uri('POST', knowledgeProvider.url, json=expectedResponseBody)
            knowledgeProvider.execute()
        self.assertEqual(knowledgeProvider.responseBody, expectedResponseBody)

        expectedLogs = [
            clsLogEvent("TestKP", "DEBUG", "", f"Sending request to Knowledge Provider {self.url}..."),
            clsLogEvent("TestKP", "DEBUG", "", f"KP 200 response in 0:00:00.000471. Content size: 118."),
            clsLogEvent("TestKP", "WARNING", "KPEmptyResponse", f"Knowledge Provider {self.url} returned an empty knowledge graph for message: {knowledgeProvider.requestBody}"),
        ]

        self.assertEqual(len(knowledgeProvider.logs), len(expectedLogs))
        self.assertEqual(knowledgeProvider.logs[0], expectedLogs[0])
        # skipping log [1], due to the message including a timing string that varies
        self.assertEqual(knowledgeProvider.logs[2], expectedLogs[2])

    @patch.object(clsKnowledgeProvider, "timeoutSeconds", new=None)
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

        expectedLogs = [
            clsLogEvent("TestKP", "DEBUG", "", f"Sending request to Knowledge Provider {self.url}..."),
            clsLogEvent("TestKP", "DEBUG", "", f"KP 200 response in 0:00:00.000471. Content size: 118."),
        ]

        self.assertEqual(knowledgeProvider.responseBody, expectedResponseBody)

        self.assertEqual(len(knowledgeProvider.logs), len(expectedLogs))
        self.assertEqual(knowledgeProvider.logs[0], expectedLogs[0])
        # skipping log [1], due to the message including a timing string that varies


if __name__ == '__main__':
    unittest.main()
