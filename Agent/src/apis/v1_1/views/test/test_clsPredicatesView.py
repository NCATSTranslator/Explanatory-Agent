import unittest
from unittest.mock import MagicMock
from mockito import when, unstub
from modApp import appFactory
from ... import version
from modDatabase import db
from ...predicates.clsPredicateManager import clsPredicateManager


class test_clsPredicatesView(unittest.TestCase):

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

        sql = clsPredicateManager.sqlGenerateUserResponsePredicates

        results = [
            {"Subject": "aa", "Object": "bb", "Predicate": "cc"},
            {"Subject": "a", "Object": "b", "Predicate": "c"},
        ]

        when(db).create_scoped_session().thenReturn(MagicMock())  # mocked session
        when(db.session).execute(statement=sql).thenReturn(MagicMock())  # mock cursor
        when(db.session.execute(statement=sql)).fetchall().thenReturn(results)  # mock results

        expectedResponse = {
            "a": {
                "b": [
                    "c"
                ]
            },
            "aa": {
                "bb": [
                    "cc"
                ]
            }
        }

        response = self.client.get(f'/{version}/predicates', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(expectedResponse, response.json)

    def test_meta_knowledge_graph_response_empty(self):

        sql = clsPredicateManager.sqlGenerateUserResponsePredicates

        results = []

        when(db).create_scoped_session().thenReturn(MagicMock())  # mocked session
        when(db.session).execute(statement=sql).thenReturn(MagicMock())  # mock cursor
        when(db.session.execute(statement=sql)).fetchall().thenReturn(results)  # mock results

        expectedResponse = {}

        response = self.client.get(f'/{version}/predicates', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(expectedResponse, response.json)


if __name__ == '__main__':
    unittest.main()
