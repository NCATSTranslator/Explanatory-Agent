import unittest
from apis.v1_3.queries.clsExplanationX00014 import ExplanationX00014
from modConfig import ZERO_RESULT_SCORE
from collections import namedtuple, OrderedDict
import requests_mock
import re


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
                    "subject": "n0",
                    "object": "n1",
                },
            },
            "nodes": {
                "n0": {"categories": ["biolink:Gene"]},
                "n1": {"categories": ["biolink:Gene"]}
            }
        }
        knowledge_graph = {
            "nodes": {
                "CURIE:000001": {
                    "name": "PTGS2",
                },
                "CURIE:000002": {
                    "name": "acetaminophen",
                },
            },
            "edges": {
                "knowledge_graph_edge1": {
                    "subject": "CURIE:000001",
                    "object": "CURIE:000002",
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
            },
        }
        CaseSolutionMock = namedtuple('CaseSolutionMock', ['query_graph', 'knowledge_graph'])
        case_solution = CaseSolutionMock(query_graph, knowledge_graph)

        x = ExplanationX00014("test_kp")

        with requests_mock.Mocker() as mocker:
            mock_name_resolution_response = {
                "CURIE:000001": ["PTGS2"],
                "CURIE:000002": ["acetaminophen"],
            }
            mock_re = re.compile('name-resolution-sri.renci.org/')
            mocker.register_uri('POST', mock_re, json=mock_name_resolution_response)

            mock_arax_response = {
                "response_code": "OK",
                "value": 0.55
            }
            mock_re = re.compile('arax.ncats.io/api/arax/v1.2/PubmedMeshNgd/')
            mocker.register_uri('GET', mock_re, json=mock_arax_response)

            results = x.create_results_and_explain(case_solution)

        expected = OrderedDict({
            'edge_bindings': {
                'e01': [{'id': 'knowledge_graph_edge1'}]
            },
            'node_bindings': {
                'n0': [{'id': 'CURIE:000001'}],
                'n1': [{'id': 'CURIE:000002'}]
            },
            'attributes': [
                {
                    "original_attribute_name": "Explanation Rationale",
                    "attribute_type_id": "biolink:description",
                    "value": "Score assigned based on Normalized Google Distance (NGD) computed between the two terms using the ARAX SmartAPI endpoint.",
                    "description": "Describes to user the Rationale for explaining the ranking"
                },
                {
                    "original_attribute_name": "Explanation Text",
                    "attribute_type_id": "biolink:has_evidence",
                    "value": "This result was given a score corresponding to the Normalized Google Distance (NGD) between the terms.",
                    "description": "Describes to user the reason this specific edge receives a score w.r.t Rationale."
                }
            ],
            'score': 0.55,
        })
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], expected)

    def test_no_names(self):
        """
        Tests that if the NGD can't find a term provided an appropriate response will still be returned.
        """

        query_graph = {
            "edges": {
                "e01": {
                    "subject": "n0",
                    "object": "n1",
                },
            },
            "nodes": {
                "n0": {"categories": ["biolink:Gene"]},
                "n1": {"categories": ["biolink:Gene"]}
            }
        }
        knowledge_graph = {
            "nodes": {
                "CURIE:000001": {},
                "CURIE:000002": {},
            },
            "edges": {
                "knowledge_graph_edge1": {
                    "subject": "CURIE:000001",
                    "object": "CURIE:000002",
                    "attributes": []
                }
            },
        }
        CaseSolutionMock = namedtuple('CaseSolutionMock', ['query_graph', 'knowledge_graph'])
        case_solution = CaseSolutionMock(query_graph, knowledge_graph)

        x = ExplanationX00014("test_kp")

        with requests_mock.Mocker() as mocker:
            mock_name_resolution_response = {
                "CURIE:000001": ["PTGS2"],
                "CURIE:000002": [],
            }
            mock_re = re.compile('name-resolution-sri.renci.org/')
            mocker.register_uri('POST', mock_re, json=mock_name_resolution_response)

            mock_arax_response = {
                "message": "Term 2 'CURIE:000002' not found in MeSH",
                "response_code": "TermNotFound"
            }
            mock_re = re.compile('arax.ncats.io/api/arax/v1.2/PubmedMeshNgd/')
            mocker.register_uri('GET', mock_re, json=mock_arax_response)

            results = x.create_results_and_explain(case_solution)

        expected = OrderedDict({
            'edge_bindings': {
                'e01': [{'id': 'knowledge_graph_edge1'}]
            },
            'node_bindings': {
                'n0': [{'id': 'CURIE:000001'}],
                'n1': [{'id': 'CURIE:000002'}]
            },
            'attributes': [
                {
                    "original_attribute_name": "Explanation Rationale",
                    "attribute_type_id": "biolink:description",
                    "value": "No explanation as this edge is not scored.",
                    "description": "Describes to user the Rationale for explaining the ranking"
                },
                {
                    "original_attribute_name": "Explanation Text",
                    "attribute_type_id": "biolink:has_evidence",
                    "value": "Explanatory Agent is unable to confirm the quality of this result due to a lack of response from the NGD service hosted on the ARAX SmartAPI endpoint.",
                    "description": "Describes to user the reason this specific edge receives a score w.r.t Rationale."
                }
            ],
            'score': ZERO_RESULT_SCORE
        })
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], expected)

    def test_get_ngd_nominal(self):
        """
        Tests that a list of subject and object synonyms will be iterated through to find a valid NGD service response.
        :return:
        """
        x = ExplanationX00014("test_kp")

        subject_synonyms = ["No Subject Result 1", "No Subject Result 2", "SubjectResult3"]
        object_synonyms = ["No Object Result 1", "No Object Result 2", "ObjectResult3"]

        with requests_mock.Mocker() as mocker:
            mock_arax_response = {
                "message": "Not found in MeSH",
                "response_code": "TermNotFound"
            }
            mock_re = re.compile(r'arax.ncats.io/api/arax/v1.2/PubmedMeshNgd/.*No.*')
            mocker.register_uri('GET', mock_re, json=mock_arax_response)

            mock_arax_response = {
                "value": 1.0,
                "response_code": "OK"
            }
            mock_re = re.compile(r'arax.ncats.io/api/arax/v1.2/PubmedMeshNgd/SubjectResult3/ObjectResult3')
            mocker.register_uri('GET', mock_re, json=mock_arax_response)

            results = x.get_ngd(subject_synonyms, object_synonyms)

        expected = 1.0
        self.assertEqual(results, expected)

    def test_get_ngd_not_found(self):
        """
        Tests that a list of subject and object synonyms will be iterated through and return a None response when no results can be found
        :return:
        """
        x = ExplanationX00014("test_kp")

        subject_synonyms = ["No Subject Result 1", "No Subject Result 2", "No Subject Result 3"]
        object_synonyms = ["No Object Result 1", "No Object Result 2", "No Object Result 3"]

        with requests_mock.Mocker() as mocker:
            mock_arax_response = {
                "message": "Not found in MeSH",
                "response_code": "TermNotFound"
            }
            mock_re = re.compile(r'arax.ncats.io/api/arax/v1.2/PubmedMeshNgd/.*No.*')
            mocker.register_uri('GET', mock_re, json=mock_arax_response)

            results = x.get_ngd(subject_synonyms, object_synonyms)

        expected = None
        self.assertEqual(results, expected)
