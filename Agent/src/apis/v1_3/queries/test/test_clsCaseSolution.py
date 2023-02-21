import unittest
from apis.v1_3.queries.clsCaseSolution import clsCaseSolution
from apis.v1_3.queries.clsQueryGraph import clsTriplet, clsNode, clsPredicate
from apis.v1_3.queries.clsCaseSolutionPath import clsCaseSolutionPath
from apis.v1_3.queries.clsKnowledgeProvider import clsKnowledgeProvider
import requests_mock
from apis.v1_3.queries.clsExplanationX00014 import ExplanationX00014
import random


class TestDerivedCaseSolution(unittest.TestCase):
    maxDiff = None

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

    def test_generateQueryGraphForOnePath_with_qualifier_constraint(self):
        solution = clsCaseSolution(-1, "")
        path = clsCaseSolutionPath()
        path.subject = "biolink:Gene"
        path.predicate = "biolink:related_to"
        path.object = "biolink:SmallMolecule"

        solution.paths = [path]
        solution.predicate_query_graph_edge_id = "e00"
        solution.subject_query_graph_node_id = "n00"
        solution.object_query_graph_node_id = "n01"
        solution.subjectCurieIds = ["NCBIGene:26160"]
        solution.edgeQualifierConstraints = [
            {
                "qualifier_set": [
                    {
                        "qualifier_type_id": "biolink:object_direction_qualifier",
                        "qualifier_value": "decreased"
                    }
                ]
            }
        ]
        solution.generateQueryGraphForOnePath()

        expected_query_graph = {
            "nodes": {
                "n00": {
                    "ids": ["NCBIGene:26160"],
                    "categories": ["biolink:Gene"]
                },
                "n01": {
                    "categories": ["biolink:SmallMolecule"]
                }
            },
            "edges": {
                "e00": {
                    "predicates": ["biolink:related_to"],
                    "subject": "n00",
                    "object": "n01",
                    "qualifier_constraints": [
                        {
                            "qualifier_set": [
                                {
                                    "qualifier_type_id": "biolink:object_direction_qualifier",
                                    "qualifier_value": "decreased"
                                }
                            ]
                        }
                    ]
                }
            }
        }

        self.assertEqual(expected_query_graph, solution.query_graph)

    def test_generateKnowledgeGraphForOnePath_with_qualifiers(self):
        """
        Ensures qualifiers are included in the knowledge graph
        :return:
        """
        import random
        random.seed(1234)

        solution = clsCaseSolution(-1, "")
        path = clsCaseSolutionPath()
        path.subject = "biolink:Gene"
        path.predicate = "biolink:related_to"
        path.object = "biolink:SmallMolecule"

        from unittest.mock import patch, PropertyMock

        class clsKPMock:
            def __init__(self, *args, **kwargs):
                self.responseBody = None

            def execute(self):
                self.responseBody = {
                        "message": {
                            "knowledge_graph": {
                                "edges": {
                                    "e0": {
                                        "subject": "gene1",
                                        "object": "disease1",
                                        "predicate": "affects",
                                        "attributes": [
                                            {"attribute1": "property"}
                                        ],
                                        "qualifiers": [
                                            {"qualifier1": "qprop"}
                                        ]
                                    }
                                }
                            }
                        }
                }

        with patch('apis.v1_3.queries.clsKnowledgeProvider.clsKnowledgeProvider', new=lambda *args, **kwargs: clsKPMock()):
            path.knowledgeProvider = clsKPMock("testKP", "testkp.com")
            solution.paths = [path]

            solution.generateKnowledgeGraphForOnePath()

        expected_knowledge_graph = {
                                "edges": {
                                    "e0-yodaczsbvw": {
                                        "subject": "gene1",
                                        "object": "disease1",
                                        "predicate": "affects",
                                        "attributes": [
                                            {"attribute1": "property"},
                                            solution.explanatory_agent_provenance_attribute
                                        ],
                                        "qualifiers": [
                                            {"qualifier1": "qprop"}
                                        ]
                                    }
                                }
                            }

        self.assertEqual(expected_knowledge_graph, solution.knowledge_graph)
