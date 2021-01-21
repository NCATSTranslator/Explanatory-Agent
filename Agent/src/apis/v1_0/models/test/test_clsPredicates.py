import unittest
from apis.v1_0.models.clsPredicates import clsPredicates


class test_clsPredicates(unittest.TestCase):

    def test_predicate_values(self):
        actual = vars(clsPredicates())
        expected = {
                "disease": {
                    "gene": [
                        "associated"
                    ],
                }
            }

        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
