import unittest
from apis.v1_3.queries.clsExplanationX00005 import ExplanationX00005
from collections import namedtuple, OrderedDict


class TestExplanationX00005(unittest.TestCase):
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
                            "attribute_source": "infores:cohd",
                            "attribute_type_id": "biolink:original_knowledge_source",
                            "value": "infores:cohd",
                            "value_type_id": "biolink:InformationResource",
                            "value_url": "http://cohd.io/api/query"
                        },
                        {
                            "attribute_source": "infores:cohd",
                            "attribute_type_id": "biolink:has_evidence",
                            "description": "Relative frequency, relative to the subject node. http://cohd.io/about.html",
                            "original_attribute_name": "relative_frequency_subject",
                            "value": 0.006286266924564797,
                            "value_type_id": "EDAM:data_1772"
                        },
                        {"attribute_type_id": "biolink:has_evidence", "value": 3, "attribute_source": "", "original_attribute_name": "ln_ratio"},
                        {"attribute_type_id": "biolink:has_evidence", "value": 4, "attribute_source": "", "original_attribute_name": "ln_ratio"},
                        {"attribute_type_id": "biolink:has_evidence", "value": 5, "attribute_source": "", "original_attribute_name": "ln_ratio"},
                        {
                            "attribute_source": "infores:cohd",
                            "attribute_type_id": "biolink:has_evidence",
                            "description": "Observed-expected frequency ratio. http://cohd.io/about.html",
                            "original_attribute_name": "ln_ratio",
                            "value": 4.147823023620047,
                            "value_type_id": "EDAM:data_1772"
                        },
                    ]
                }
            }
        }
        CaseSolutionMock = namedtuple('CaseSolutionMock', ['query_graph', 'knowledge_graph'])
        case_solution = CaseSolutionMock(query_graph, knowledge_graph)

        x = ExplanationX00005("ln_ratio", "test_kp")
        self.assertEqual(x.edgeAttributeValidate(knowledge_graph["edges"]["knowledge_graph_edge1"]), True)

        results = x.create_results_and_explain(case_solution)
        expected = OrderedDict({
            'edge_bindings': {
                'e01': [{'id': 'knowledge_graph_edge1'}]
            },
            'node_bindings': {
                'n0': [{'id': 'n2'}],
                'n1': [{'id': 'n1'}]
            },
            'score': 0.8295646047240094,
            'attributes': [
                {
                    'original_attribute_name': 'Explanation Rationale',
                    'attribute_type_id': 'biolink:description',
                    'value': 'The score was obtained based on averaging the confidence level of the subject and object nodes as informed by COHD.',
                    'description': 'Describes to user the Rationale for explaining the ranking'
                },
                {
                    'original_attribute_name': 'Explanation Text',
                    'attribute_type_id': 'biolink:has_evidence',
                    'value': 'This result was given a score of 0.8295646047240094 based on the range (i.e, 3 to 5) observed in the current set of results for the attribute ln_ratio supplied by test_kp.',
                    'description': 'Describes the reason this specific edge receives a score w.r.t Rationale'
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
                            "attribute_source": "infores:cohd",
                            "attribute_type_id": "biolink:original_knowledge_source",
                            "value": "infores:cohd",
                            "value_type_id": "biolink:InformationResource",
                            "value_url": "http://cohd.io/api/query"
                        },
                        {
                            "attribute_source": "infores:cohd",
                            "attribute_type_id": "biolink:has_evidence",
                            "description": "Relative frequency, relative to the subject node. http://cohd.io/about.html",
                            "original_attribute_name": "relative_frequency_subject",
                            "value": 0.006286266924564797,
                            "value_type_id": "EDAM:data_1772"
                        }
                    ]
                }
            }
        }

        x = ExplanationX00005("ln_ratio", "test_kp")
        self.assertEqual(x.edgeAttributeValidate(knowledge_graph["edges"]["knowledge_graph_edge1"]), False)
