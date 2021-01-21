import unittest
from modApp import app
from apis.v1_0.models.clsPredicates import clsPredicates


class test_clsPredicatesView(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        self.app = None

    def test_predicate_response(self):
        response = self.app.get('/v1.0/predicates', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(clsPredicates.return_accepted(), response.json)


if __name__ == '__main__':
    unittest.main()
