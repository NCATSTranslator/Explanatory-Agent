import unittest
from apis.v1_3.queries.clsCaseSolution import clsCaseSolution
from apis.v1_3.queries.clsCaseSolutionPath import clsCaseSolutionPath
from apis.v1_3.queries.clsKnowledgeProvider import clsKnowledgeProvider
import requests_mock
from apis.v1_3.queries.clsExplanationX00014 import ExplanationX00014
import random


class TestDerivedCaseSolution(unittest.TestCase):
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
        caseSolution = clsCaseSolution(1, "")
        caseSolution.logs = []
        # caseSolution.logs = self.logs  # enables shared log across all objects by passing by reference. Don't want currently.
        caseSolution.id = 1234
        caseSolution.caseId = "Qtest"

        caseSolution.subject_query_graph_node_id = "n0"
        caseSolution.object_query_graph_node_id = "n1"
        caseSolution.predicate_query_graph_edge_id = "e0"

        caseSolution.similarSubject = "biolink:Gene"
        caseSolution.similarObject = "biolink:Disease"
        caseSolution.similarPredicate = "biolink:related_to"
        caseSolution.subjectCurieIds = ["GENE:0001"]
        caseSolution.objectCurieIds = None
        caseSolution.subjectConstraints = None
        caseSolution.objectConstraints = None
        caseSolution.explanation_similarity = 1.0
        caseSolution.explanation_solution_finder = unittest.mock.MagicMock()
        caseSolution.explanation_solution_finder.search = lambda *args, **kwargs: ExplanationX00014("test")

        caseSolutionPath1 = clsCaseSolutionPath()
        caseSolutionPath1.logs = []
        caseSolutionPath1.subject = "biolink:Gene"
        caseSolutionPath1.object = "biolink:Protein"
        caseSolutionPath1.predicate = "biolink:creates"
        caseSolutionPath1.knowledgeProvider = clsKnowledgeProvider(
            name="KP1",
            url="https://www.kp1.com/query"
        )
        caseSolutionPath1.knowledgeProvider.logs = caseSolutionPath1.logs

        caseSolutionPath2 = clsCaseSolutionPath()
        caseSolutionPath2.logs = []
        caseSolutionPath2.subject = "biolink:Protein"
        caseSolutionPath2.object = "biolink:Disease"
        caseSolutionPath2.predicate = "biolink:influences"
        caseSolutionPath2.knowledgeProvider = clsKnowledgeProvider(
            name="KP2",
            url="https://www.kp2.com/query"
        )
        caseSolutionPath2.knowledgeProvider.logs = caseSolutionPath2.logs

        caseSolution.paths = [caseSolutionPath1, caseSolutionPath2]

        kp1_response = {
            "message": {
                'query_graph': {
                    'edges': {
                        'e00': {
                            'subject': 'n00',
                            'predicates': ['biolink:creates'],
                            'object': 'n01'
                        }
                    },
                    'nodes': {
                        'n00': {'categories': ['biolink:Gene'], 'ids': ['GENE:0001']},
                        'n01': {'categories': ['biolink:Protein']}
                    }
                },
                "knowledge_graph": {
                    "nodes": {
                        "GENE:0001": {"categories": ["biolink:Gene"]},
                        "PROTEIN:0002": {"categories": ["biolink:Protein"]},
                    },
                    "edges": {
                        "KP1E1": {
                            "attributes": [],
                            "subject": "GENE:0001",
                            "predicate": "biolink:creates",
                            "object": "PROTEIN:0002"
                        },
                    }
                },
                "results": [
                    {
                        "edge_bindings": {"e00": [{"id": "KP1E1"}]},
                        "node_bindings": {
                            "n00": [{"id": "GENE:0001"}],
                            "n01": [{"id": "PROTEIN:0002"}]
                        },
                        "score": 1.0
                    },
                ]
            }
        }

        kp2_response = {
            "message": {
                'query_graph': {
                    'edges': {
                        'e01': {
                            'subject': 'n01',
                            'predicates': ['biolink:influences'],
                            'object': 'n02'
                        }
                    },
                    'nodes': {
                        'n01': {'categories': ['biolink:Protein'], 'ids': ['PROTEIN:0002']},
                        'n02': {'categories': ['biolink:Disease']}
                    }
                },
                "knowledge_graph": {
                    "nodes": {
                        "PROTEIN:0002": {"categories": ["biolink:Protein"]},
                        "DISEASE:0003": {"categories": ["biolink:Disease"]},
                    },
                    "edges": {
                        "KP2E1": {
                            "attributes": [],
                            "subject": "PROTEIN:0002",
                            "predicate": "biolink:influences",
                            "object": "DISEASE:0003"
                        },
                    }
                },
                "results": [
                    {
                        "edge_bindings": {"e01": [{"id": "KP2E1"}]},
                        "node_bindings": {
                            "n01": [{"id": "PROTEIN:0002"}],
                            "n02": [{"id": "DISEASE:0003"}]
                        },
                        "score": 1.0
                    },
                ]
            }
        }

        with requests_mock.Mocker(real_http=True) as mocker:
            mocker.register_uri('POST', "https://www.kp1.com/query", json=kp1_response)
            mocker.register_uri('POST', "https://www.kp2.com/query", json=kp2_response)
            random.seed(1234)
            caseSolution.execute()
            caseSolution.generate_results()
            pass

        expected = {
            "message": {
                'query_graph': {
                    'edges': {
                        'e00': {
                            'subject': 'n00',
                            'predicates': ['biolink:creates'],
                            'object': 'n01'
                        },
                        'e01': {
                            'subject': 'n01',
                            'predicates': ['biolink:influences'],
                            'object': 'n02'
                        }
                    },
                    'nodes': {
                        'n00': {'categories': ['biolink:Gene'], 'ids': ['GENE:0001']},
                        'n01': {'categories': ['biolink:Protein']},
                        'n02': {'categories': ['biolink:Disease']}
                    }
                },
                "knowledge_graph": {
                    "nodes": {
                        "GENE:0001": {"categories": ["biolink:Gene"]},
                        "PROTEIN:0002": {"categories": ["biolink:Protein"]},
                        "DISEASE:0003": {"categories": ["biolink:Disease"]},
                    },
                    "edges": {
                        "KP1E1-yodaczsbvw": {
                            'attributes': [{
                                'attribute_type_id': 'biolink:aggregator_knowledge_source',
                                'value': 'infores:explanatory-agent',
                                'value_type_id': 'biolink:InformationResource',
                                'value_url': 'https://explanatory-agent.azurewebsites.net/v1.2',
                                'description': 'The eXplanatory Autonomous Relay Agent (xARA) utilizes a case-based reasoning approach to execute ARS queries by obtaining results from multiple knowledge providers (KPs) and utilizes various methods such as natural language understanding models that traverse biomedical literature to score and explain its scores.',
                                'attribute_source': 'infores:explanatory-agent'
                            }],
                            "subject": "GENE:0001",
                            "predicate": "biolink:creates",
                            "object": "PROTEIN:0002"
                        },
                        "KP2E1-cdylhaazal": {
                            'attributes': [{
                                'attribute_type_id': 'biolink:aggregator_knowledge_source',
                                'value': 'infores:explanatory-agent',
                                'value_type_id': 'biolink:InformationResource',
                                'value_url': 'https://explanatory-agent.azurewebsites.net/v1.2',
                                'description': 'The eXplanatory Autonomous Relay Agent (xARA) utilizes a case-based reasoning approach to execute ARS queries by obtaining results from multiple knowledge providers (KPs) and utilizes various methods such as natural language understanding models that traverse biomedical literature to score and explain its scores.',
                                'attribute_source': 'infores:explanatory-agent'
                            }],
                            "subject": "PROTEIN:0002",
                            "predicate": "biolink:influences",
                            "object": "DISEASE:0003"
                        },
                    }
                },
                "results": [
                    {
                        "edge_bindings": {
                            "e00": [{
                                "id": "KP1E1-yodaczsbvw",
                                'score': 0.0001,
                                'attributes': [{'attribute_type_id': 'biolink:description',
                                                 'description': 'Describes to user the Rationale for explaining the ranking',
                                                 'original_attribute_name': 'Explanation Rationale',
                                                 'value': 'Score assigned was zero because no evidence, provenance, or confidence information was available to compute a score.'},
                                               {'attribute_type_id': 'biolink:has_evidence',
                                                'description': 'Describes to user the reason this specific edge receives a score w.r.t Rationale.',
                                                'original_attribute_name': 'Explanation Text',
                                                'value': 'No explanation as this edge is not scored'}],
                            }],
                            "e01": [{
                                "id": "KP2E1-cdylhaazal",
                                'score': 0.0001,
                                'attributes': [{'attribute_type_id': 'biolink:description',
                                                'description': 'Describes to user the Rationale for explaining the ranking',
                                                'original_attribute_name': 'Explanation Rationale',
                                                'value': 'Score assigned was zero because no evidence, provenance, or confidence information was available to compute a score.'},
                                               {'attribute_type_id': 'biolink:has_evidence',
                                                'description': 'Describes to user the reason this specific edge receives a score w.r.t Rationale.',
                                                'original_attribute_name': 'Explanation Text',
                                                'value': 'No explanation as this edge is not scored'}],
                            }],
                        },
                        "node_bindings": {
                            "n00": [{"id": "GENE:0001"}],
                            "n01": [{"id": "PROTEIN:0002"}],
                            "n02": [{"id": "DISEASE:0003"}]
                        },
                        "score": 0.0001
                    },
                ]
            }
        }

        self.assertEqual(expected['message']['query_graph'], caseSolution.query_graph)
        self.assertEqual(expected['message']['knowledge_graph'], caseSolution.knowledge_graph)
        self.assertEqual(expected['message']['results'], caseSolution.results)

    def test_kp1_no_kg(self):
        caseSolution = clsCaseSolution(1, "")
        caseSolution.logs = []
        # caseSolution.logs = self.logs  # enables shared log across all objects by passing by reference. Don't want currently.
        caseSolution.id = 1234
        caseSolution.caseId = "Qtest"

        caseSolution.subject_query_graph_node_id = "n0"
        caseSolution.object_query_graph_node_id = "n1"
        caseSolution.predicate_query_graph_edge_id = "e0"

        caseSolution.similarSubject = "biolink:Gene"
        caseSolution.similarObject = "biolink:Disease"
        caseSolution.similarPredicate = "biolink:related_to"
        caseSolution.subjectCurieIds = ["GENE:0001"]
        caseSolution.objectCurieIds = None
        caseSolution.subjectConstraints = None
        caseSolution.objectConstraints = None
        caseSolution.explanation_similarity = 1.0
        caseSolution.explanation_solution_finder = unittest.mock.MagicMock()
        caseSolution.explanation_solution_finder.search = lambda *args, **kwargs: ExplanationX00014("test")

        caseSolutionPath1 = clsCaseSolutionPath()
        caseSolutionPath1.logs = []
        caseSolutionPath1.subject = "biolink:Gene"
        caseSolutionPath1.object = "biolink:Protein"
        caseSolutionPath1.predicate = "biolink:creates"
        caseSolutionPath1.knowledgeProvider = clsKnowledgeProvider(
            name="KP1",
            url="https://www.kp1.com/query"
        )
        caseSolutionPath1.knowledgeProvider.logs = caseSolutionPath1.logs

        caseSolutionPath2 = clsCaseSolutionPath()
        caseSolutionPath2.logs = []
        caseSolutionPath2.subject = "biolink:Protein"
        caseSolutionPath2.object = "biolink:Disease"
        caseSolutionPath2.predicate = "biolink:influences"
        caseSolutionPath2.knowledgeProvider = clsKnowledgeProvider(
            name="KP2",
            url="https://www.kp2.com/query"
        )
        caseSolutionPath2.knowledgeProvider.logs = caseSolutionPath2.logs

        caseSolution.paths = [caseSolutionPath1, caseSolutionPath2]

        kp1_response = {
            "message": {
                'query_graph': {
                    'edges': {
                        'e00': {
                            'subject': 'n00',
                            'predicates': ['biolink:creates'],
                            'object': 'n01'
                        }
                    },
                    'nodes': {
                        'n00': {'categories': ['biolink:Gene'], 'ids': ['GENE:0001']},
                        'n01': {'categories': ['biolink:Protein']}
                    }
                },
                "knowledge_graph": {
                    "nodes": {},
                    "edges": {}
                },
                "results": []
            }
        }

        kp2_response = {
            "message": {
                'query_graph': {
                    'edges': {
                        'e01': {
                            'subject': 'n01',
                            'predicates': ['biolink:influences'],
                            'object': 'n02'
                        }
                    },
                    'nodes': {
                        'n01': {'categories': ['biolink:Protein']},
                        'n02': {'categories': ['biolink:Disease']}
                    }
                },
                "knowledge_graph": None,
                "results": None
            }
        }

        with requests_mock.Mocker(real_http=True) as mocker:
            mocker.register_uri('POST', "https://www.kp1.com/query", json=kp1_response)
            mocker.register_uri('POST', "https://www.kp2.com/query", json=kp2_response)
            random.seed(1234)
            caseSolution.execute()
            caseSolution.generate_results()
            pass

        expected = {
            "message": {
                'query_graph': {
                    'edges': {
                        'e00': {
                            'subject': 'n00',
                            'predicates': ['biolink:creates'],
                            'object': 'n01'
                        },
                        'e01': {
                            'subject': 'n01',
                            'predicates': ['biolink:influences'],
                            'object': 'n02'
                        }
                    },
                    'nodes': {
                        'n00': {'categories': ['biolink:Gene'], 'ids': ['GENE:0001']},
                        'n01': {'categories': ['biolink:Protein']},
                        'n02': {'categories': ['biolink:Disease']}
                    }
                },
                "knowledge_graph": {
                    "nodes": {},
                    "edges": {}
                },
                "results": []
            }
        }

        self.assertEqual(expected['message']['query_graph'], caseSolution.query_graph)
        self.assertEqual(expected['message']['knowledge_graph'], caseSolution.knowledge_graph)
        self.assertEqual(expected['message']['results'], caseSolution.results)
