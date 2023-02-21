import unittest
from apis.v1_3.queries.clsCaseSolutionManager import clsCaseSolutionManager


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

    def test_filter_case_solutions(self):
        """
        Ensures the filter_case_solutions call works as intended. Keeps all derived, and returns the most specific of duplicate KP queries.
        :return:
        """
        class MockRow:
            def __init__(self, identifier, data):
                self.id = identifier
                self.data = data

            def __getitem__(self, key):
                return self.data[key]

            def __hash__(self):
                return self.id

        solutions = [
            MockRow(identifier=1, data={
                "SOLUTION_ID": 40206,
                "CASE_ID": 'Q054047',
                "KP_PATH1": 'Service Provider',
                "NODE1_PATH1_CATEGORY": 'biolink:SmallMolecule',
                "NODE2_PATH1_CATEGORY": "biolink:Disease'",
                "EDGE1_PATH1_PREDICATE": 'biolink:associated_with',
                "KP_PATH2": 'Automat Robokop KG',
                "NODE1_PATH2_CATEGORY": "biolink:Disease",
                "NODE2_PATH2_CATEGORY": "biolink:Disease",
                "EDGE1_PATH2_PREDICATE": "biolink:associated_with"
            }),
            MockRow(identifier=2, data={
                "SOLUTION_ID": 40207,
                "CASE_ID": 'Q054047',
                "KP_PATH1": 'Service Provider',
                "NODE1_PATH1_CATEGORY": 'biolink:SmallMolecule',
                "NODE2_PATH1_CATEGORY": "biolink:Disease'",
                "EDGE1_PATH1_PREDICATE": 'biolink:associated_with',
                "KP_PATH2": 'Service Provider',
                "NODE1_PATH2_CATEGORY": "biolink:Disease",
                "NODE2_PATH2_CATEGORY": "biolink:Disease",
                "EDGE1_PATH2_PREDICATE": "biolink:associated_with"
            }),

            MockRow(identifier=3, data={
                "SOLUTION_ID": 1,
                "CASE_ID": 'Q00001',
                "KP_PATH1": 'Same KP',
                "NODE1_PATH1_CATEGORY": 'biolink:SmallMolecule',
                "NODE2_PATH1_CATEGORY": "biolink:Disease'",
                "EDGE1_PATH1_PREDICATE": 'biolink:associated_with',
                "KP_PATH2": None,
                "NODE1_PATH2_CATEGORY": None,
                "NODE2_PATH2_CATEGORY": None,
                "EDGE1_PATH2_PREDICATE": None
            }),
            MockRow(identifier=4, data={
                "SOLUTION_ID": 2,
                "CASE_ID": 'Q00001',
                "KP_PATH1": 'Same KP',
                "NODE1_PATH1_CATEGORY": 'biolink:ChemicalEntity',
                "NODE2_PATH1_CATEGORY": "biolink:Disease'",
                "EDGE1_PATH1_PREDICATE": 'biolink:associated_with',
                "KP_PATH2": None,
                "NODE1_PATH2_CATEGORY": None,
                "NODE2_PATH2_CATEGORY": None,
                "EDGE1_PATH2_PREDICATE": None
            }),
            MockRow(identifier=5, data={
                "SOLUTION_ID": 3,
                "CASE_ID": 'Q00002',
                "KP_PATH1": 'Same KP',
                "NODE1_PATH1_CATEGORY": 'biolink:OtherThing',
                "NODE2_PATH1_CATEGORY": "biolink:Disease'",
                "EDGE1_PATH1_PREDICATE": 'biolink:associated_with',
                "KP_PATH2": None,
                "NODE1_PATH2_CATEGORY": None,
                "NODE2_PATH2_CATEGORY": None,
                "EDGE1_PATH2_PREDICATE": None
            }),
            MockRow(identifier=6, data={
                "SOLUTION_ID": 4,
                "CASE_ID": 'Q00002',
                "KP_PATH1": 'Different KP',
                "NODE1_PATH1_CATEGORY": 'biolink:OtherThing',
                "NODE2_PATH1_CATEGORY": "biolink:Disease'",
                "EDGE1_PATH1_PREDICATE": 'biolink:associated_with',
                "KP_PATH2": None,
                "NODE1_PATH2_CATEGORY": None,
                "NODE2_PATH2_CATEGORY": None,
                "EDGE1_PATH2_PREDICATE": None
            }),
        ]

        manager = clsCaseSolutionManager(-1, {"nodes": {}, "edges": {}}, {}, None)
        results = manager.filter_case_solutions(solutions)

        expected = [
            solutions[0],
            solutions[1],
            solutions[2],
            solutions[4],
            solutions[5],
        ]

        self.assertEqual(expected, results)
