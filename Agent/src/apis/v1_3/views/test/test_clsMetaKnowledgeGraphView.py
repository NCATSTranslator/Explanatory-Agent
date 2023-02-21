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

        class HashableDict(dict):
            def __key(self):
                return tuple((k, self[k]) for k in sorted(self))

            def __hash__(self):
                return hash(self.__key())

            def __eq__(self, other):
                return self.__key() == other.__key()

        results = [
            HashableDict({"Subject": "biolink:Aa", "Object": "biolink:Bb", "Predicate": "biolink:cc"}),
            HashableDict({"Subject": "biolink:Aaa", "Object": "biolink:Bbb", "Predicate": "biolink:ccc"}),
        ]

        when(db).create_scoped_session().thenReturn(MagicMock())  # mocked session
        when(db.session).execute(statement=sql).thenReturn(MagicMock())  # mock cursor
        when(db.session.execute(statement=sql)).fetchall().thenReturn(results)  # mock results

        expectedResponse = {'edges': [{'attributes': [{'attribute_type_id': 'ALL'}],
                                       'knowledge_types': ['lookup'],
                                       'object': 'biolink:Bb',
                                       'predicate': 'biolink:cc',
                                       'subject': 'biolink:Aa'},
                                      {'attributes': [{'attribute_type_id': 'ALL'}],
                                       'knowledge_types': ['lookup'],
                                       'object': 'biolink:Bbb',
                                       'predicate': 'biolink:ccc',
                                       'subject': 'biolink:Aaa'}],
                            'nodes': {'biolink:Aa': {'attributes': [{'attribute_type_id': 'ALL'}],
                                                     'id_prefixes': ['ALL']},
                                      'biolink:Aaa': {'attributes': [{'attribute_type_id': 'ALL'}],
                                                      'id_prefixes': ['ALL']},
                                      'biolink:Bb': {'attributes': [{'attribute_type_id': 'ALL'}],
                                                     'id_prefixes': ['ALL']},
                                      'biolink:Bbb': {'attributes': [{'attribute_type_id': 'ALL'}],
                                                      'id_prefixes': ['ALL']}}}

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
