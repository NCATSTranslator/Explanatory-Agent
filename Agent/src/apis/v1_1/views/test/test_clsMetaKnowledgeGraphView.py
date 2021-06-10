import unittest
from unittest.mock import MagicMock
from mockito import when, unstub
from modApp import appFactory
from ... import version
from modDatabase import db
from ...metaKnowledgeGraphs.clsMetaKnowledgeGraphManager import clsMetaKnowledgeGraphManager


class test_clsMetaKnowledgeGraphView(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = appFactory().test_client()
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        cls.client = None

    def setUp(self):
        unstub()

    def tearDown(self):
        unstub()

    def test_meta_knowledge_graph_response_nominal(self):

        sql = clsMetaKnowledgeGraphManager.sqlGenerateUserResponseMetaKnowledgeGraph

        results = [
            {"Subject": "aa", "Object": "bb", "Predicate": "cc"},
            {"Subject": "a", "Object": "b", "Predicate": "c"},
        ]

        when(db).create_scoped_session().thenReturn(MagicMock())  # mocked session
        when(db.session).execute(statement=sql).thenReturn(MagicMock())  # mock cursor
        when(db.session.execute(statement=sql)).fetchall().thenReturn(results)  # mock results

        expectedResponse = {
            "nodes": {
                "a": {
                    "id_prefixes": ["ALL"]
                },
                "aa": {
                    "id_prefixes": ["ALL"]
                },
                "b": {
                    "id_prefixes": ["ALL"]
                },
                "bb": {
                    "id_prefixes": ["ALL"]
                }
            },
            "edges": [
                {
                    "subject": "aa",
                    "predicate": "cc",
                    "object": "bb",
                    "relations": None
                },
                {
                    "subject": "a",
                    "predicate": "c",
                    "object": "b",
                    "relations": None
                }
            ]
        }

        response = self.client.get(f'/{version}/meta_knowledge_graph', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(expectedResponse, response.json)

    def test_meta_knowledge_graph_response_empty(self):

        sql = clsMetaKnowledgeGraphManager.sqlGenerateUserResponseMetaKnowledgeGraph

        results = []

        when(db).create_scoped_session().thenReturn(MagicMock())  # mocked session
        when(db.session).execute(statement=sql).thenReturn(MagicMock())  # mock cursor
        when(db.session.execute(statement=sql)).fetchall().thenReturn(results)  # mock results

        expectedResponse = {"nodes": {}, "edges": []}

        response = self.client.get(f'/{version}/meta_knowledge_graph', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(expectedResponse, response.json)


if __name__ == '__main__':
    unittest.main()
