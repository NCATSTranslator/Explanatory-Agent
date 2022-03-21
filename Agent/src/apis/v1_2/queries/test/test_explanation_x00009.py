import unittest
from apis.v1_2.queries.clsExplanationX00009 import ExplanationX00009
from collections import namedtuple, OrderedDict


class TestExplanationX00009(unittest.TestCase):
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

    def test_nominal(self):
        query_graph = {
            "edges": {
                "e01": {
                    "object": "n0",
                    "subject": "n1"
                },
            },
            "nodes": {
                "n0": {"categories": ["biolink:Gene"]},
                "n1": {"categories": ["biolink:Gene"]}
            }
        }
        knowledge_graph = {
            "edges": {
                "knowledge_graph_edge1": {
                    "subject": "n1",
                    "object": "n2",
                    "attributes": [
                        {
                            "attribute_type_id": "biolink:original_knowledge_source",
                            "value": "infores:ctd",
                            "value_type_id": "biolink:InformationResource",
                            "original_attribute_name": "biolink:original_knowledge_source",
                            "value_url": None,
                            "attribute_source": None,
                            "description": None,
                            "attributes": None
                        },
                        {
                            "attribute_type_id": "biolink:relation",
                            "value": "CTD:therapeutic",
                            "value_type_id": "EDAM:data_0006",
                            "original_attribute_name": "relation",
                            "value_url": None,
                            "attribute_source": None,
                            "description": None,
                            "attributes": None
                        },
                        {
                            "attribute_type_id": "biolink:publications",
                            "value": [
                                "PMID:19583683"
                            ],
                            "value_type_id": "EDAM:data_0006",
                            "original_attribute_name": "publications",
                            "value_url": None,
                            "attribute_source": None,
                            "description": None,
                            "attributes": None
                        },
                        {
                            "attribute_type_id": "biolink:aggregator_knowledge_source",
                            "value": "infores:automat-robokop",
                            "value_type_id": "biolink:InformationResource",
                            "original_attribute_name": "biolink:aggregator_knowledge_source",
                            "value_url": None,
                            "attribute_source": None,
                            "description": None,
                            "attributes": None
                        },
                    ]
                }
            }
        }
        CaseSolutionMock = namedtuple('CaseSolutionMock', ['query_graph', 'knowledge_graph'])
        case_solution = CaseSolutionMock(query_graph, knowledge_graph)

        x = ExplanationX00009("test_kp")
        self.assertEqual(x.edgeAttributeValidate(knowledge_graph["edges"]["knowledge_graph_edge1"]), True)

        results = x.create_results_and_explain(case_solution)
        expected = OrderedDict({
            'edge_bindings': {
                'e01': [{'id': 'knowledge_graph_edge1'}]
            },
            'node_bindings': {
                'n0': [{'id': 'n1'}],
                'n1': [{'id': 'n2'}]
            },
            'score': 1.0,
            'attributes': [
                {
                    "original_attribute_name": "Explanation Rationale",
                    "attribute_type_id": "biolink:description",
                    "value": "The score was obtained based on the existence of publications as informed by Automat CTD",
                    "description": "Describes to user the Rationale for explaining the ranking"
                },
                {
                    "attribute_type_id": "biolink:has_evidence",
                    "value": "This result was given a score of 1 because the Automat CTD knowledge provider producing this result has indicated a publication in its support",
                    "original_attribute_name": "Explanation Text",
                    "description": "Describes the reason this specific edge receives a score w.r.t Rationale"
                }
            ]
        })
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], expected)

    def test_invalid(self):
        knowledge_graph = {
            "edges": {
                "knowledge_graph_edge1": {
                    "subject": "n1",
                    "object": "n2",
                    "attributes": [
                        {
                            "attribute_type_id": "biolink:original_knowledge_source",
                            "value": "infores:ctd",
                            "value_type_id": "biolink:InformationResource",
                            "original_attribute_name": "biolink:original_knowledge_source",
                            "value_url": None,
                            "attribute_source": None,
                            "description": None,
                            "attributes": None
                        },
                        {
                            "attribute_type_id": "biolink:relation",
                            "value": "CTD:therapeutic",
                            "value_type_id": "EDAM:data_0006",
                            "original_attribute_name": "relation",
                            "value_url": None,
                            "attribute_source": None,
                            "description": None,
                            "attributes": None
                        },
                        {
                            "attribute_type_id": "biolink:aggregator_knowledge_source",
                            "value": "infores:automat-robokop",
                            "value_type_id": "biolink:InformationResource",
                            "original_attribute_name": "biolink:aggregator_knowledge_source",
                            "value_url": None,
                            "attribute_source": None,
                            "description": None,
                            "attributes": None
                        },
                    ]
                }
            }
        }

        x = ExplanationX00009("test_kp")
        self.assertEqual(x.edgeAttributeValidate(knowledge_graph["edges"]["knowledge_graph_edge1"]), False)
