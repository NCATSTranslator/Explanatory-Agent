import unittest
# from ..clsQueryManager import clsQueryManager
from apis.v1_2.queries.clsQueryManager import clsQueryManager
from apis.v1_2.queries.clsQueryGraph import clsNode, clsPredicate, clsTriplet


class test_deriveQueryPaths(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_one_hop(self):
        query_graph = {
            "nodes": {
                "n0": {
                    "ids": ["n0id"],
                    "categories": ["n0category1", "n0category2"]
                },
                "n1": {
                    "categories": ["n1category1", "n1category2"]
                },
            },
            "edges": {
                "e00": {
                    "predicates": [],
                    "subject": "n00",
                    "object": "n01"
                }
            }
        }

        qm = clsQueryManager()
        qm.userRequestBody = {"message": {"query_graph": query_graph}}
        qm.deriveQueryPaths()

        expected_query_graphs = [
            {
                "nodes": {
                    "n0": {"ids": ["n0id"], "categories": ["n0category1"]},
                    "n1": {"categories": ["n1category1"]},
                },
                "edges": {"e00": {"predicates": ["ANY"], "subject": "n00", "object": "n01"}}
            },
            {
                "nodes": {
                    "n0": {"ids": ["n0id"], "categories": ["n0category1"]},
                    "n1": {"categories": ["n1category2"]},
                },
                "edges": {"e00": {"predicates": ["ANY"], "subject": "n00", "object": "n01"}}
            },
            {
                "nodes": {
                    "n0": {"ids": ["n0id"], "categories": ["n0category2"]},
                    "n1": {"categories": ["n1category1"]},
                },
                "edges": {"e00": {"predicates": ["ANY"], "subject": "n00", "object": "n01"}}
            },
            {
                "nodes": {
                    "n0": {"ids": ["n0id"], "categories": ["n0category2"]},
                    "n1": {"categories": ["n1category2"]},
                },
                "edges": {"e00": {"predicates": ["ANY"], "subject": "n00", "object": "n01"}}
            },
        ]
        self.assertEqual(qm.batch_query_graphs, expected_query_graphs)
