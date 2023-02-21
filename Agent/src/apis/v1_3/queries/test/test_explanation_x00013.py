import unittest
from apis.v1_3.queries.clsExplanationX00013 import ExplanationX00013
from collections import namedtuple, OrderedDict


class TestExplanationX00013(unittest.TestCase):
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
                            "attribute_source": "infores:chembl",
                            "attribute_type_id": "biolink:FDA_approval_status",
                            "attributes": [],
                            "original_attribute_name": "max phase for indication",
                            "value": "FDA Clinical Research Phase 3",
                            "value_type_id": "biolink:FDA_approval_status_enum"
                        },
                        {
                            "attribute_source": "infores:chembl",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "ClinicalTrials",
                            "value": "NCT03162432",
                            "value_type_id": "string",
                            "value_url": "https://clinicaltrials.gov/search?id=%22NCT03162432%22"
                        },
                        {
                            "attribute_source": "infores:chembl",
                            "attribute_type_id": "biolink:primary_knowledge_source",
                            "attributes": [],
                            "description": "MolePro's ChEMBL indication transformer",
                            "original_attribute_name": "biolink:primary_knowledge_source",
                            "value": "infores:chembl",
                            "value_type_id": "biolink:InformationResource"
                        },
                    ]
                }
            }
        }
        CaseSolutionMock = namedtuple('CaseSolutionMock', ['query_graph', 'knowledge_graph'])
        case_solution = CaseSolutionMock(query_graph, knowledge_graph)

        x = ExplanationX00013("test_kp")
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
            'score': 1.0,
            'attributes': [
                {
                    "original_attribute_name": "Explanation Rationale",
                    "attribute_type_id": "biolink:description",
                    "value": "The score was obtained based on the identification of a clinical trial obtained in CHEMBL.",
                    "description": "Describes to user the Rationale for explaining the ranking"
                },
                {
                    "attribute_type_id": "biolink:has_evidence",
                    "value": "This result was given a score of 1 because the knowledge provider producing this result has identified a clinical trial (obtained via CHEMBL) in its support.",
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
                            "attribute_source": "infores:chembl",
                            "attribute_type_id": "biolink:FDA_approval_status",
                            "attributes": [],
                            "original_attribute_name": "max phase for indication",
                            "value": "FDA Clinical Research Phase 3",
                            "value_type_id": "biolink:FDA_approval_status_enum"
                        },
                        {
                            "attribute_source": "infores:chembl",
                            "attribute_type_id": "biolink:primary_knowledge_source",
                            "attributes": [],
                            "description": "MolePro's ChEMBL indication transformer",
                            "original_attribute_name": "biolink:primary_knowledge_source",
                            "value": "infores:chembl",
                            "value_type_id": "biolink:InformationResource"
                        },
                    ]
                }
            }
        }

        x = ExplanationX00013("test_kp")
        self.assertEqual(x.edgeAttributeValidate(knowledge_graph["edges"]["knowledge_graph_edge1"]), False)
