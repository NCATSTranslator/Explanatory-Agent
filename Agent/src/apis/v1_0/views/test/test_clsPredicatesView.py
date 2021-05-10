import unittest
from modApp import appFactory
from ...predicates.clsPredicateManager import clsPredicateManager
from ... import version


class test_clsPredicatesView(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = appFactory().test_client()
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        cls.client = None

    def test_predicate_response(self):
        predicateManager = clsPredicateManager()
        predicateManager.generateUserResponsePredicates()
        response = self.client.get(f'/{version}/predicates', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(predicateManager.userResponsePredicates, response.json)


if __name__ == '__main__':
    unittest.main()
