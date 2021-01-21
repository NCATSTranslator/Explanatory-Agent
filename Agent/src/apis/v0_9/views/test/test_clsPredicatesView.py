import unittest
from modApp import app
from apis.v0_9.models.clsPredicates import clsPredicates


class test_clsPredicatesView(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        self.app = None

    def test_predicate_response(self):
        response = self.app.get('/v0.9.2/predicates', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(vars(clsPredicates()), response.json)


if __name__ == '__main__':
    unittest.main()
