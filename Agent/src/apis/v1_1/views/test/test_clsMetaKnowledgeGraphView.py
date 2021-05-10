import unittest
from modApp import appFactory
from ...metaKnowledgeGraphs.clsMetaKnowledgeGraphManager import clsMetaKnowledgeGraphManager
from ... import version


class test_clsMetaKnowledgeGraphView(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = appFactory().test_client()
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        cls.client = None

    def test_predicate_response(self):
        metaKnowledgeGraphManager = clsMetaKnowledgeGraphManager()
        metaKnowledgeGraphManager.generateUserResponseMetaKnowledgeGraph()
        response = self.client.get(f'/{version}/meta_knowledge_graph', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(metaKnowledgeGraphManager.userResponseMetaKnowledgeGraph, response.json)


if __name__ == '__main__':
    unittest.main()
