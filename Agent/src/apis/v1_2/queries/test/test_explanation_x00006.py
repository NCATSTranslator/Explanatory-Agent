import unittest
from apis.v1_2.queries.clsExplanationX00006 import ExplanationX00006
from collections import namedtuple, OrderedDict


class TestExplanationX00006(unittest.TestCase):
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
                            "attribute_type_id": "biolink:aggregator_knowledge_source",
                            "value": [
                                "infores:translator-biothings-explorer"
                            ],
                            "value_type_id": "biolink:InformationResource"
                        },
                        {
                            "attribute_type_id": "biolink:aggregator_knowledge_source",
                            "value": [
                                "infores:biothings-multiomics-clinical-risk"
                            ],
                            "value_type_id": "biolink:InformationResource"
                        },
                        {
                            "attribute_type_id": "auc_roc",
                            "value": 0.8639
                        },
                        {
                            "attribute_type_id": "classifier",
                            "value": "Logistic Regression"
                        },
                    ]
                }
            }
        }
        CaseSolutionMock = namedtuple('CaseSolutionMock', ['query_graph', 'knowledge_graph'])
        case_solution = CaseSolutionMock(query_graph, knowledge_graph)

        x = ExplanationX00006("auc_roc", "test_kp")
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
            'score': 0.8639,
            'attributes': [
                {
                    "original_attribute_name": "Explanation Rationale",
                    "attribute_type_id": "biolink:description",
                    "value": "The score was obtained based on the average accuracy given by the area under the curve informed by the Clinical Risk KP.",
                    "description": "Describes to user the Rationale for explaining the ranking"
                },
                {
                    "original_attribute_name": "Explanation Text",
                    "attribute_type_id": "biolink:has_evidence",
                    "value": 0.8639,
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
                            "attribute_type_id": "biolink:aggregator_knowledge_source",
                            "value": [
                                "infores:translator-biothings-explorer"
                            ],
                            "value_type_id": "biolink:InformationResource"
                        },
                        {
                            "attribute_type_id": "biolink:aggregator_knowledge_source",
                            "value": [
                                "infores:biothings-multiomics-clinical-risk"
                            ],
                            "value_type_id": "biolink:InformationResource"
                        },
                        {
                            "attribute_type_id": "classifier",
                            "value": "Logistic Regression"
                        },
                    ]
                }
            }
        }

        x = ExplanationX00006("auc_roc", "test_kp")
        self.assertEqual(x.edgeAttributeValidate(knowledge_graph["edges"]["knowledge_graph_edge1"]), False)
