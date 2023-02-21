import unittest
# from ..clsQueryPath import clsQueryPath
from apis.v1_3.queries.clsQueryPath import clsQueryPath
from apis.v1_3.queries.clsQueryGraph import clsNode, clsPredicate, clsTriplet, clsQualifier, clsQualifierConstraint
from apis.v1_3.queries.clsQueryManager import clsQueryManager


class test_clsQueryManager(unittest.TestCase):

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

    def test_derive_query_paths_simple(self):
        user_request_body = {
            "message": {
                "query_graph": {
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
                            "object": "n01"
                        }
                    }
                }
            }
        }
        query_manager = clsQueryManager()
        query_manager.userRequestBody = user_request_body
        query_manager.deriveQueryPaths()

        expected_bath_query_graphs = [
            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:related_to'],
                               'object': 'n01'}},
             'nodes': {'n00': {'ids': ['NCBIGene:26160'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:SmallMolecule']}}}
        ]
        self.assertEqual(query_manager.batch_query_graphs, expected_bath_query_graphs)

    def test_derive_query_paths_multiple_node_ids(self):
        user_request_body = {
            "message": {
                "query_graph": {
                    "nodes": {
                        "n00": {
                            "ids": ["NCBIGene:26160", "NCBIGene:26161"],
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
                            "object": "n01"
                        }
                    }
                }
            }
        }
        query_manager = clsQueryManager()
        query_manager.userRequestBody = user_request_body
        query_manager.deriveQueryPaths()

        expected_bath_query_graphs = [
            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:related_to'],
                               'object': 'n01'}},
             'nodes': {'n00': {'ids': ['NCBIGene:26160'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:SmallMolecule']}}},
            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:related_to'],
                               'object': 'n01'}},
             'nodes': {'n00': {'ids': ['NCBIGene:26161'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:SmallMolecule']}}}
        ]
        self.assertEqual(query_manager.batch_query_graphs, expected_bath_query_graphs)

    def test_derive_query_paths_multiple_node_categories(self):
        user_request_body = {
            "message": {
                "query_graph": {
                    "nodes": {
                        "n00": {
                            "ids": ["NCBIGene:26160"],
                            "categories": ["biolink:Gene"]
                        },
                        "n01": {
                            "categories": ["biolink:SmallMolecule", "biolink:BigMolecule"]
                        }
                    },
                    "edges": {
                        "e00": {
                            "predicates": ["biolink:related_to"],
                            "subject": "n00",
                            "object": "n01"
                        }
                    }
                }
            }
        }
        query_manager = clsQueryManager()
        query_manager.userRequestBody = user_request_body
        query_manager.deriveQueryPaths()

        expected_bath_query_graphs = [
            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:related_to'],
                               'object': 'n01'}},
             'nodes': {'n00': {'ids': ['NCBIGene:26160'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:SmallMolecule']}}},
            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:related_to'],
                               'object': 'n01'}},
             'nodes': {'n00': {'ids': ['NCBIGene:26160'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:BigMolecule']}}}
        ]
        self.assertEqual(query_manager.batch_query_graphs, expected_bath_query_graphs)

    def test_derive_query_paths_multiple_node_ids_categories(self):
        user_request_body = {
            "message": {
                "query_graph": {
                    "nodes": {
                        "n00": {
                            "ids": ["NCBIGene:26160", "NCBIGene:26161"],
                            "categories": ["biolink:Gene"]
                        },
                        "n01": {
                            "categories": ["biolink:SmallMolecule", "biolink:BigMolecule"]
                        }
                    },
                    "edges": {
                        "e00": {
                            "predicates": ["biolink:related_to"],
                            "subject": "n00",
                            "object": "n01"
                        }
                    }
                }
            }
        }
        query_manager = clsQueryManager()
        query_manager.userRequestBody = user_request_body
        query_manager.deriveQueryPaths()

        expected_bath_query_graphs = [
            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:related_to'],
                               'object': 'n01'}},
             'nodes': {'n00': {'ids': ['NCBIGene:26160'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:SmallMolecule']}}},
            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:related_to'],
                               'object': 'n01'}},
             'nodes': {'n00': {'ids': ['NCBIGene:26160'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:BigMolecule']}}},
            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:related_to'],
                               'object': 'n01'}},
             'nodes': {'n00': {'ids': ['NCBIGene:26161'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:SmallMolecule']}}},
            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:related_to'],
                               'object': 'n01'}},
             'nodes': {'n00': {'ids': ['NCBIGene:26161'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:BigMolecule']}}},
        ]
        self.assertEqual(query_manager.batch_query_graphs, expected_bath_query_graphs)

    def test_derive_query_paths_multiple_predicates(self):
        user_request_body = {
            "message": {
                "query_graph": {
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
                            "predicates": ["biolink:related_to", "biolink:really_related_to"],
                            "subject": "n00",
                            "object": "n01"
                        }
                    }
                }
            }
        }
        query_manager = clsQueryManager()
        query_manager.userRequestBody = user_request_body
        query_manager.deriveQueryPaths()

        expected_bath_query_graphs = [
            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:related_to'],
                               'object': 'n01'}},
             'nodes': {'n00': {'ids': ['NCBIGene:26160'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:SmallMolecule']}}},
            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:really_related_to'],
                               'object': 'n01'}},
             'nodes': {'n00': {'ids': ['NCBIGene:26160'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:SmallMolecule']}}}
        ]
        self.assertEqual(query_manager.batch_query_graphs, expected_bath_query_graphs)

    def test_derive_query_paths_qualifier_constraint(self):
        user_request_body = {
            "message": {
                "query_graph": {
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
            }
        }
        query_manager = clsQueryManager()
        query_manager.userRequestBody = user_request_body
        query_manager.deriveQueryPaths()

        expected_bath_query_graphs = [
            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:related_to'],
                               'object': 'n01',
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
                               }},
             'nodes': {'n00': {'ids': ['NCBIGene:26160'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:SmallMolecule']}}},
        ]
        self.assertEqual(query_manager.batch_query_graphs, expected_bath_query_graphs)

    def test_derive_query_paths_multiple_qualifier_constraints(self):
        user_request_body = {
            "message": {
                "query_graph": {
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
                                },
                                {
                                    "qualifier_set": [
                                        {
                                            "qualifier_type_id": "biolink:object_quantity_qualifier",
                                            "qualifier_value": "many"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        }
        query_manager = clsQueryManager()
        query_manager.userRequestBody = user_request_body
        query_manager.deriveQueryPaths()

        expected_bath_query_graphs = [
            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:related_to'],
                               'object': 'n01',
                               "qualifier_constraints": [
                                   {
                                       "qualifier_set": [
                                           {
                                               "qualifier_type_id": "biolink:object_direction_qualifier",
                                               "qualifier_value": "decreased"
                                           }
                                       ]
                                   }
                               ]}},
             'nodes': {'n00': {'ids': ['NCBIGene:26160'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:SmallMolecule']}}},
            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:related_to'],
                               'object': 'n01',
                               "qualifier_constraints": [
                                   {
                                       "qualifier_set": [
                                           {
                                               "qualifier_type_id": "biolink:object_quantity_qualifier",
                                               "qualifier_value": "many"
                                           }
                                       ]
                                   }
                               ]}},
             'nodes': {'n00': {'ids': ['NCBIGene:26160'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:SmallMolecule']}}}
        ]
        self.assertEqual(query_manager.batch_query_graphs, expected_bath_query_graphs)

    def test_derive_query_paths_multiple_predicates_qualifier_constraints(self):
        user_request_body = {
            "message": {
                "query_graph": {
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
                            "predicates": ["biolink:related_to", 'biolink:really_related_to'],
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
                                },
                                {
                                    "qualifier_set": [
                                        {
                                            "qualifier_type_id": "biolink:object_quantity_qualifier",
                                            "qualifier_value": "many"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        }
        query_manager = clsQueryManager()
        query_manager.userRequestBody = user_request_body
        query_manager.deriveQueryPaths()

        expected_bath_query_graphs = [
            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:related_to'],
                               'object': 'n01',
                               "qualifier_constraints": [
                                   {
                                       "qualifier_set": [
                                           {
                                               "qualifier_type_id": "biolink:object_direction_qualifier",
                                               "qualifier_value": "decreased"
                                           }
                                       ]
                                   }
                               ]}},
             'nodes': {'n00': {'ids': ['NCBIGene:26160'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:SmallMolecule']}}},
            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:related_to'],
                               'object': 'n01',
                               "qualifier_constraints": [
                                   {
                                       "qualifier_set": [
                                           {
                                               "qualifier_type_id": "biolink:object_quantity_qualifier",
                                               "qualifier_value": "many"
                                           }
                                       ]
                                   }
                               ]}},
             'nodes': {'n00': {'ids': ['NCBIGene:26160'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:SmallMolecule']}}},

            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:really_related_to'],
                               'object': 'n01',
                               "qualifier_constraints": [
                                   {
                                       "qualifier_set": [
                                           {
                                               "qualifier_type_id": "biolink:object_direction_qualifier",
                                               "qualifier_value": "decreased"
                                           }
                                       ]
                                   }
                               ]}},
             'nodes': {'n00': {'ids': ['NCBIGene:26160'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:SmallMolecule']}}},
            {'edges': {'e00': {'subject': 'n00',
                               'predicates': ['biolink:really_related_to'],
                               'object': 'n01',
                               "qualifier_constraints": [
                                   {
                                       "qualifier_set": [
                                           {
                                               "qualifier_type_id": "biolink:object_quantity_qualifier",
                                               "qualifier_value": "many"
                                           }
                                       ]
                                   }
                               ]}},
             'nodes': {'n00': {'ids': ['NCBIGene:26160'], 'categories': ['biolink:Gene']},
                       'n01': {'categories': ['biolink:SmallMolecule']}}}

        ]
        self.assertEqual(query_manager.batch_query_graphs, expected_bath_query_graphs)

    def test_merge_overlapping_results(self):
        """
        Tests merging of multiple subject predicate object triplets into a single response object as described in Step 3 of Sol P 2
        :return:
        """
        query_manager = clsQueryManager()
        query_manager.results = [
            {
                'edge_bindings': {
                    "e00": [
                        {
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
                        }
                    ],
                },
                'node_bindings': {
                    "n00": [{"id": "gene1"}],
                    "n01": [{"id": "disease1"}],
                },
                "score": 0.11
            },
            {
                'edge_bindings': {
                    "e00": [{"id": "cs1-edge2"}]
                },
                'node_bindings': {
                    "n00": [{"id": "gene2"}],
                    "n01": [{"id": "disease2"}],
                },
                'score': 0.12
            },
            {
                'edge_bindings': {
                    "e00": [
                        {
                            "id": "cs2-edge1",
                            "attributes": [
                                {
                                    'attribute_type_id': 'solution2_result1_attr1_prop1_value',
                                    'value': 'solution2_result1_attr1_prop2_value',
                                }
                            ],
                        }
                    ],
                },
                'node_bindings': {
                    "n00": [{"id": "gene1"}],
                    "n01": [{"id": "disease1"}],
                },
                "score": 0.21
            }
        ]
        query_manager.merge_overlapping_results()

        expected_results = [
            {
                'edge_bindings': {
                    "e00": [
                        {
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
                        },
                        {
                            "id": "cs2-edge1",
                            "attributes": [
                                {
                                    'attribute_type_id': 'solution2_result1_attr1_prop1_value',
                                    'value': 'solution2_result1_attr1_prop2_value',
                                }
                            ],
                        }
                    ],
                },
                'node_bindings': {
                    "n00": [{"id": "gene1"}],
                    "n01": [{"id": "disease1"}],
                },
                "score": ((0.11 + 0.2) + (0.21 + 0.2)) / 2
            },
            {
                'edge_bindings': {
                    "e00": [{"id": "cs1-edge2"}]
                },
                'node_bindings': {
                    "n00": [{"id": "gene2"}],
                    "n01": [{"id": "disease2"}],
                },
                'score': 0.12,
            }
        ]

        import reasoner_validator
        for result in expected_results:
            reasoner_validator.validate(result, "Result", "1.3.0")

        self.assertEqual(query_manager.results, expected_results)

    def test_merge_overlapping_results_two_hop(self):
        """
        Tests merging of a two-hop query n0 -> n1 -> n2 results
        :return:
        """
        query_manager = clsQueryManager()
        query_manager.results = [
            {
                'edge_bindings': {
                    "e00": [
                        {
                            "id": "cs1-edge00-1",
                            "attributes": [
                                {
                                    'attribute_type_id': 'solution1_result1_edge1_attr1_prop1_value',
                                    'value': 'solution1_result1_attr1_prop2_value',
                                },
                                {
                                    'attribute_type_id': 'solution1_result1_edge1_attr2_prop1_value',
                                    'value': 'solution1_result1_attr2_prop2_value',
                                }
                            ],
                        }
                    ],
                    "e01": [
                        {
                            "id": "cs1-edge01-1",
                            "attributes": [
                                {
                                    'attribute_type_id': 'solution1_result1_edge2_attr1_prop1_value',
                                    'value': 'solution1_result1_attr1_prop2_value',
                                },
                                {
                                    'attribute_type_id': 'solution1_result1_edge2_attr2_prop1_value',
                                    'value': 'solution1_result1_attr2_prop2_value',
                                }
                            ],
                        }
                    ]
                },
                'node_bindings': {
                    "n00": [{"id": "gene1"}],
                    "n01": [{"id": "disease1"}],
                    "n02": [{"id": "drug1"}],
                },
                "score": 0.9
            },
            {
                'edge_bindings': {
                    "e00": [{"id": "cs1-edge00-2"}],
                    "e01": [{"id": "cs1-edge01-2"}],
                },
                'node_bindings': {
                    "n00": [{"id": "gene1"}],
                    "n01": [{"id": "disease1"}],
                    "n02": [{"id": "drug1"}],
                },
                'score': 0.1
            },
        ]
        query_manager.merge_overlapping_results()

        expected_results = [
            {
                'edge_bindings': {
                    "e00": [
                        {
                            "id": "cs1-edge00-1",
                            "attributes": [
                                {
                                    'attribute_type_id': 'solution1_result1_edge1_attr1_prop1_value',
                                    'value': 'solution1_result1_attr1_prop2_value',
                                },
                                {
                                    'attribute_type_id': 'solution1_result1_edge1_attr2_prop1_value',
                                    'value': 'solution1_result1_attr2_prop2_value',
                                }
                            ],
                        },
                        {"id": "cs1-edge00-2"}
                    ],
                    "e01": [
                        {
                            "id": "cs1-edge01-1",
                            "attributes": [
                                {
                                    'attribute_type_id': 'solution1_result1_edge2_attr1_prop1_value',
                                    'value': 'solution1_result1_attr1_prop2_value',
                                },
                                {
                                    'attribute_type_id': 'solution1_result1_edge2_attr2_prop1_value',
                                    'value': 'solution1_result1_attr2_prop2_value',
                                }
                            ],
                        },
                        {"id": "cs1-edge01-2"}
                    ],
                },
                'node_bindings': {
                    "n00": [{"id": "gene1"}],
                    "n01": [{"id": "disease1"}],
                    "n02": [{"id": "drug1"}],
                },
                "score": (1.0 + (0.1 + 0.2)) / 2
            },
        ]

        import reasoner_validator
        for result in expected_results:
            reasoner_validator.validate(result, "Result", "1.3.0")

        self.assertEqual(query_manager.results, expected_results)

    @staticmethod
    def loadJsonFromFile(fileName):
        import json
        import os

        fullPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), fileName)
        with open(fullPath) as file:
            return json.load(file)

    def test_send_to_aes(self):
        """
        Tests AES response returns valid trapi message
        :return:
        """
        response = self.loadJsonFromFile("trapi_disease2phenotype.json")
        query_manager = clsQueryManager()
        query_manager.query_graph = response["message"]["query_graph"]
        query_manager.knowledge_graph = response["message"]["knowledge_graph"]
        query_manager.results = response["message"]["results"]

        query_manager.send_to_aes()
        query_manager.generateSuccessUserResponseBody()
        response = query_manager.userResponseBody

        import reasoner_validator
        reasoner_validator.validate(response, "Response", "1.3.0")

        aes_attribute_found = False
        for result in response["message"]["results"]:
            for edge_binding_id, edge_bindings in result["edge_bindings"].items():
                for edge_binding in edge_bindings:
                    if "attributes" in edge_binding:
                        for attribute in edge_binding["attributes"]:
                            if attribute["attribute_type_id"] == "biolink:aes_evidence_score":
                                aes_attribute_found = True

        assert aes_attribute_found is True
