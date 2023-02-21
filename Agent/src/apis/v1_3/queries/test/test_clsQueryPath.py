import unittest
# from ..clsQueryPath import clsQueryPath
from apis.v1_3.queries.clsQueryPath import clsQueryPath
from apis.v1_3.queries.clsQueryGraph import clsNode, clsPredicate, clsTriplet, clsQualifier, clsQualifierConstraint


class test_clsQueryPath(unittest.TestCase):

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

    def test_one_hop(self):
        query_graph = {
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
        query_path = clsQueryPath(query_graph)
        query_path.create_plan()

        plan = [
            clsTriplet(
                clsNode("n00", {
                  "ids": ["NCBIGene:26160"],
                  "categories": ["biolink:Gene"]
                }),
                clsPredicate("e00", {
                    "predicates": ["biolink:related_to"],
                    "subject": "n00",
                    "object": "n01",
                    "__id": "e00",
                }),
                clsNode("n01", {
                    "categories": ["biolink:SmallMolecule"]
                })
            )
        ]
        self.assertEqual(query_path.triplets, plan)
        self.assertEqual(query_path.unassigned_nodes, [])

    def test_two_hop(self):
        query_graph = {
            "edges": {
                "e00": {
                    "subject": "n00",
                    "object": "n01",
                    "predicates": [
                        "biolink:entity_regulates_entity",
                        "biolink:genetically_interacts_with"
                    ]
                },
                "e01": {
                    "subject": "n01",
                    "object": "n02",
                    "predicates": ["biolink:related_to"]
                }
            },
            "nodes": {
                "n00": {
                    "ids": ["NCBIGene:23221"],
                    "categories": ["biolink:Gene"]
                },
                "n01": {
                    "categories": ["biolink:Gene"]
                },
                "n02": {
                    "categories": ["biolink:SmallMolecule"]
                }
            }
        }
        query_path = clsQueryPath(query_graph)
        query_path.create_plan()

        expected_triplets = [
            clsTriplet(
                clsNode("n00", {"ids": ["NCBIGene:23221"], "categories": ["biolink:Gene"]}),
                clsPredicate("e00", {
                    "predicates": ["biolink:entity_regulates_entity", "biolink:genetically_interacts_with"],
                    "subject": "n00", "object": "n01", "__id": "e00",
                }),
                clsNode("n01", {"categories": ["biolink:Gene"]})
            ),
            clsTriplet(
                clsNode("n01", {"categories": ["biolink:Gene"]}),
                clsPredicate("e01", {
                    "predicates": ["biolink:related_to"],
                    "subject": "n01", "object": "n02", "__id": "e01",
                }),
                clsNode("n02", {"categories": ["biolink:SmallMolecule"]})
            ),
        ]

        self.assertEqual(expected_triplets, query_path.triplets)

    def test_two_hop_A_2_RHOBTB2_twohop(self):
        query_graph = {
            "edges": {
                "e01": {
                    "object": "n0",
                    "subject": "n1",
                    "predicates": ["biolink:entity_regulates_entity"]
                },
                "e02": {
                    "object": "n1",
                    "subject": "n2",
                    "predicates": ["biolink:related_to"]
                }
            },
            "nodes": {
                "n0": {
                    "ids": ["NCBIGene:23221"],
                    "categories": ["biolink:Gene"]
                },
                "n1": {
                    "categories": ["biolink:Gene"]
                },
                "n2": {
                    "categories": ["biolink:SmallMolecule"]
                }
            }
        }
        query_path = clsQueryPath(query_graph)
        query_path.create_plan()

        expected_triplets = [
            clsTriplet(
                clsNode("n1", {"categories": ["biolink:Gene"]}),
                clsPredicate("e01", {
                    "predicates": ["biolink:entity_regulates_entity"],
                    "subject": "n1", "object": "n0", "__id": "e01",
                }),
                clsNode("n0", {"ids": ["NCBIGene:23221"], "categories": ["biolink:Gene"]})
            ),
            clsTriplet(
                clsNode("n2", {"categories": ["biolink:SmallMolecule"]}),
                clsPredicate("e02", {
                    "predicates": ["biolink:related_to"],
                    "subject": "n2", "object": "n1", "__id": "e02",
                }),
                clsNode("n1", {"categories": ["biolink:Gene"]})
            ),
        ]

        self.assertEqual(expected_triplets, query_path.triplets)

    def test_one_hop_with_qualifier_constraints(self):
        query_graph = {
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
        query_path = clsQueryPath(query_graph)
        query_path.create_plan()

        plan = [
            clsTriplet(
                clsNode("n00", {
                  "ids": ["NCBIGene:26160"],
                  "categories": ["biolink:Gene"]
                }),
                clsPredicate("e00", {
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
                    ],
                    "__id": "e00",
                }),
                clsNode("n01", {
                    "categories": ["biolink:SmallMolecule"]
                })
            )
        ]
        self.assertEqual(query_path.triplets, plan)
        self.assertEqual(query_path.unassigned_nodes, [])

    def test_one_hop_multi_qualifier_set(self):
        query_graph = {
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
                                },
                                {
                                    "qualifier_type_id": "biolink:object_quantity_qualifier",
                                    "qualifier_value": "very"
                                }
                            ]
                        }
                    ]
                }
            }
        }
        query_path = clsQueryPath(query_graph)
        query_path.create_plan()

        plan = [
            clsTriplet(
                clsNode("n00", {
                  "ids": ["NCBIGene:26160"],
                  "categories": ["biolink:Gene"]
                }),
                clsPredicate("e00", {
                    "predicates": ["biolink:related_to"],
                    "subject": "n00",
                    "object": "n01",
                    "qualifier_constraints": [
                        {
                            "qualifier_set": [
                                {
                                    "qualifier_type_id": "biolink:object_direction_qualifier",
                                    "qualifier_value": "decreased"
                                },
                                {
                                    "qualifier_type_id": "biolink:object_quantity_qualifier",
                                    "qualifier_value": "very"
                                }
                            ]
                        }
                    ],
                    "__id": "e00",
                }),
                clsNode("n01", {
                    "categories": ["biolink:SmallMolecule"]
                })
            )
        ]
        self.assertEqual(query_path.triplets, plan)
        self.assertEqual(query_path.unassigned_nodes, [])

    def test_two_hop_with_qualifier_constraints(self):
        query_graph = {
            "edges": {
                "e00": {
                    "subject": "n00",
                    "object": "n01",
                    "predicates": [
                        "biolink:entity_regulates_entity",
                        "biolink:genetically_interacts_with"
                    ],
                    "qualifier_constraints": [
                        {
                            "qualifier_set": [
                                {
                                    "qualifier_type_id": "biolink:object_direction_qualifier",
                                    "qualifier_value": "decreased"
                                }
                            ]
                        }
                    ],
                },
                "e01": {
                    "subject": "n01",
                    "object": "n02",
                    "predicates": ["biolink:related_to"],
                    "qualifier_constraints": [
                        {
                            "qualifier_set": [
                                {
                                    "qualifier_type_id": "biolink:object_quantity_qualifier",
                                    "qualifier_value": "lots"
                                }
                            ]
                        }
                    ],
                }
            },
            "nodes": {
                "n00": {
                    "ids": ["NCBIGene:23221"],
                    "categories": ["biolink:Gene"]
                },
                "n01": {
                    "categories": ["biolink:Gene"]
                },
                "n02": {
                    "categories": ["biolink:SmallMolecule"]
                }
            }
        }
        query_path = clsQueryPath(query_graph)
        query_path.create_plan()

        expected_triplets = [
            clsTriplet(
                clsNode("n00", {"ids": ["NCBIGene:23221"], "categories": ["biolink:Gene"]}),
                clsPredicate("e00", {
                    "predicates": ["biolink:entity_regulates_entity", "biolink:genetically_interacts_with"],
                    "subject": "n00", "object": "n01", "__id": "e00",
                    "qualifier_constraints": [
                        {
                            "qualifier_set": [
                                {
                                    "qualifier_type_id": "biolink:object_direction_qualifier",
                                    "qualifier_value": "decreased"
                                }
                            ]
                        }
                    ],
                }),
                clsNode("n01", {"categories": ["biolink:Gene"]})
            ),
            clsTriplet(
                clsNode("n01", {"categories": ["biolink:Gene"]}),
                clsPredicate("e01", {
                    "predicates": ["biolink:related_to"],
                    "subject": "n01", "object": "n02", "__id": "e01",
                    "qualifier_constraints": [
                        {
                            "qualifier_set": [
                                {
                                    "qualifier_type_id": "biolink:object_quantity_qualifier",
                                    "qualifier_value": "lots"
                                }
                            ]
                        }
                    ],
                }),
                clsNode("n02", {"categories": ["biolink:SmallMolecule"]})
            ),
        ]

        self.assertEqual(expected_triplets, query_path.triplets)
