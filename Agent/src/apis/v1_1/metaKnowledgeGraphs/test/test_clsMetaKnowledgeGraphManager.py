import unittest
from ..clsMetaKnowledgeGraphManager import clsMetaKnowledgeGraphManager


class test_clsMetaKnowledgeGraphManager(unittest.TestCase):

    def test_meta_knowledge_graph_values(self):

        metaKnowledgeGraphManager = clsMetaKnowledgeGraphManager()
        metaKnowledgeGraphManager.generateUserResponseMetaKnowledgeGraph()

        actual = metaKnowledgeGraphManager.userResponseMetaKnowledgeGraph
        expected = {}  # todo
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
