import unittest
from apis.v1_3.queries.clsMultiHop import clsMultiHop
from apis.v1_3.queries.clsCaseSolution import clsCaseSolution
from collections import OrderedDict


class test_clsMultiHop(unittest.TestCase):

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

    def test_merge_results(self):
        case_solution_1 = clsCaseSolution(1, "case1")
        case_solution_1.query_graph = {
            "nodes": {
                "n00": {
                    "ids": ["n00id"],
                    "categories": ["gene"]
                },
                "n01": {
                    "categories": ["disease"]
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
        case_solution_1.results = [
            OrderedDict({
                'edge_bindings': {
                    "e00": [{"id": "cs1-edge1"}]
                },
                'node_bindings': {
                    "n00": [{"id": "gene1"}],
                    "n01": [{"id": "disease1"}],
                },
                'score': 0.11,
                'attributes': [
                    {
                        'attribute_type_id': 'solution1_result1_attr1_prop1_value',
                        'value': 'solution1_result1_attr1_prop2_value',
                    },
                    {
                        'attribute_type_id': 'solution1_result1_attr2_prop1_value',
                        'value': 'solution1_result1_attr2_prop2_value',
                    }
                ]
            }),
            OrderedDict({
                'edge_bindings': {
                    "e00": [{"id": "cs1-edge2"}]
                },
                'node_bindings': {
                    "n00": [{"id": "gene2"}],
                    "n01": [{"id": "disease2"}],
                },
                'score': 0.12,
                'attributes': [
                    {
                        'attribute_type_id': 'solution1_result2_attr1_prop1_value',
                        'value': 'solution1_result2_attr1_prop2_value',
                    }
                ]
            })
        ]

        case_solution_2 = clsCaseSolution(2, "case2")
        case_solution_2.query_graph = {
            "nodes": {
                "n01": {
                    "ids": ["n01id"],
                    "categories": ["disease"]
                },
                "n02": {
                    "categories": ["drug"]
                },
            },
            "edges": {
                "e01": {
                    "predicates": [],
                    "subject": "n01",
                    "object": "n02"
                }
            }
        }
        case_solution_2.results = [
            OrderedDict({
                'edge_bindings': {
                    "e01": [{"id": "cs2-edge1"}]
                },
                'node_bindings': {
                    "n01": [{"id": "disease1"}],
                    "n02": [{"id": "drug1"}],
                },
                'score': 0.21,
                'attributes': [
                    {
                        'attribute_type_id': 'solution2_result1_attr1_prop1_value',
                        'value': 'solution2_result1_attr1_prop2_value',
                    },
                    {
                        'attribute_type_id': 'solution2_result1_attr2_prop1_value',
                        'value': 'solution2_result1_attr2_prop2_value',
                    },
                    {
                        'attribute_type_id': 'solution2_result1_attr3_prop1_value',
                        'value': 'solution2_result1_attr3_prop2_value',
                    }
                ]
            })
        ]

        multihop = clsMultiHop(3, "multihop", [case_solution_1, case_solution_2])
        multihop.merge_results()

        expected_results = [
            {
                'edge_bindings': {
                    "e00": [{
                        "id": "cs1-edge1",
                        "attributes": [
                            {
                                'attribute_type_id': 'solution1_result1_attr1_prop1_value',
                                'value': 'solution1_result1_attr1_prop2_value',
                            },
                            {
                                'attribute_type_id': 'solution1_result1_attr2_prop1_value',
                                'value': 'solution1_result1_attr2_prop2_value',
                            }
                        ],
                        "score": 0.11
                    }],
                    "e01": [{
                        "id": "cs2-edge1",
                        "attributes": [
                            {
                                'attribute_type_id': 'solution2_result1_attr1_prop1_value',
                                'value': 'solution2_result1_attr1_prop2_value',
                            },
                            {
                                'attribute_type_id': 'solution2_result1_attr2_prop1_value',
                                'value': 'solution2_result1_attr2_prop2_value',
                            },
                            {
                                'attribute_type_id': 'solution2_result1_attr3_prop1_value',
                                'value': 'solution2_result1_attr3_prop2_value',
                            }
                        ],
                        "score": 0.21
                    }],
                },
                'node_bindings': {
                    "n00": [{"id": "gene1"}],
                    "n01": [{"id": "disease1"}],
                    "n02": [{"id": "drug1"}],
                },
                "score": 0.16
            },
        ]

        import reasoner_validator
        reasoner_validator.validate(expected_results[0], "Result", "1.3.0")

        self.assertEqual(multihop.results, expected_results)
