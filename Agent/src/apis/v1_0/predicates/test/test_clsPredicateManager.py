import unittest
from ..clsPredicateManager import clsPredicateManager


class test_clsPredicateManager(unittest.TestCase):

    def test_predicate_values(self):

        predicateManager = clsPredicateManager()
        predicateManager.generateUserResponsePredicates()

        actual = predicateManager.userResponsePredicates
        expected = {
            "biolink:Drug": {
                "biolink:Disease": [
                    "biolink:treats"
                ]
            },
            "biolink:Disease": {
                "biolink:Gene": [
                    "biolink:condition_associated_with_gene",
                    "biolink:gene_associated_with_condition"
                ]
            },
            "biolink:Gene": {
                "biolink:Disease": [
                    "biolink:gene_associated_with_condition"
                ],
                "biolink:ChemicalSubstance": [
                    "biolink:gene_has_variant_that_contributes_to_drug_response_association"
                ]
            }
        }

        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
