import unittest
from apis.v1_2.queries.clsExplanationX00010 import ExplanationX00010
from collections import namedtuple, OrderedDict


class TestExplanationX00010(unittest.TestCase):
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
                            "attribute_type_id": "biolink:Attribute",
                            "value": 1.4468699374203414e-34,
                            "value_type_id": "EDAM:data_0006",
                            "original_attribute_name": "enrichment_p",
                            "value_url": None,
                            "attribute_source": None,
                            "description": None,
                            "attributes": None
                        },
                        {
                            "attribute_type_id": "biolink:Attribute",
                            "value": 0.882247458771776,
                            "value_type_id": "EDAM:data_0006",
                            "original_attribute_name": "num_publications",
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

        x = ExplanationX00010("enrichment_p", "test_kp")
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
                    "value": "The score was obtained based on the Enrichment_p value informed by the knowledge source.",
                    "description": "Describes to user the Rationale for explaining the ranking"
                },
                {
                    "original_attribute_name": "Explanation Text",
                    "attribute_type_id": "biolink:has_evidence",
                    "value": f"This result was given a score of 1.0 based on the range (i.e, 1.4468699374203414e-34 to 1.4468699374203414e-34) observed in the current set of results for the attribute enrichment_p supplied by test_kp.",
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
                            "attribute_type_id": "biolink:Attribute",
                            "value": 0.882247458771776,
                            "value_type_id": "EDAM:data_0006",
                            "original_attribute_name": "num_publications",
                            "value_url": None,
                            "attribute_source": None,
                            "description": None,
                            "attributes": None
                        },
                    ]
                }
            }
        }

        x = ExplanationX00010("enrichment_p", "test_kp")
        self.assertEqual(x.edgeAttributeValidate(knowledge_graph["edges"]["knowledge_graph_edge1"]), False)
