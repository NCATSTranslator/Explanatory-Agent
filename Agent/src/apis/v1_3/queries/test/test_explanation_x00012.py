import unittest
from apis.v1_3.queries.clsExplanationX00012 import ExplanationX00012
from collections import namedtuple, OrderedDict


class TestExplanationX00012(unittest.TestCase):
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
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:21059682",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:1740537",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:17269711",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:17314143",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:21761941",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:23516449",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:23867873",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:24811995",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:25598765",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:26806034",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:26848182",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:27609529",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": "PMID:28842642",
                            "value_type_id": "string"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:primary_knowledge_source",
                            "attributes": [],
                            "description": "MolePro's HMDB disorders transformer",
                            "original_attribute_name": "biolink:primary_knowledge_source",
                            "value": "infores:hmdb",
                            "value_type_id": "biolink:InformationResource"
                        },
                        {
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:aggregator_knowledge_source",
                            "attributes": [],
                            "description": "Molecular Data Provider",
                            "original_attribute_name": "biolink:aggregator_knowledge_source",
                            "value": "infores:molepro",
                            "value_type_id": "biolink:InformationResource"
                        },
                        {
                            "attribute_source": "infores:molepro",
                            "attribute_type_id": "biolink:aggregator_knowledge_source",
                            "description": "Molecular Data Provider",
                            "original_attribute_name": "biolink:aggregator_knowledge_source",
                            "value": "infores:molepro",
                            "value_type_id": "biolink:InformationResource"
                        },
                        {
                            "attribute_type_id": "biolink:aggregator_knowledge_source",
                            "value": "infores:explanatory-agent",
                            "value_type_id": "biolink:InformationResource",
                            "value_url": "https://explanatory-agent.azurewebsites.net/v1.2",
                            "description": "The eXplanatory Autonomous Relay Agent (xARA) utilizes a case-based reasoning approach to execute ARS queries by obtaining results from multiple knowledge providers (KPs) and utilizes various methods such as natural language understanding models that traverse biomedical literature to score and explain its scores.",
                            "attribute_source": "infores:explanatory-agent"
                        }
                    ]
                }
            }
        }
        CaseSolutionMock = namedtuple('CaseSolutionMock', ['query_graph', 'knowledge_graph'])
        case_solution = CaseSolutionMock(query_graph, knowledge_graph)

        x = ExplanationX00012("test_kp")
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
                    "value": "The score was obtained based on the existence of publications as informed by Automat HMDB.",
                    "description": "Describes to user the Rationale for explaining the ranking"
                },
                {
                    "attribute_type_id": "biolink:has_evidence",
                    "value": "This result was given a score of 1 because the Automat HMDB knowledge provider producing this result has indicated a publication in its support",
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
                            "attribute_source": "infores:hmdb",
                            "attribute_type_id": "biolink:Publication",
                            "attributes": [],
                            "original_attribute_name": "reference",
                            "value": None,
                            "value_type_id": "string"
                        },
                    ]
                }
            }
        }

        x = ExplanationX00012("test_kp")
        self.assertEqual(x.edgeAttributeValidate(knowledge_graph["edges"]["knowledge_graph_edge1"]), False)
