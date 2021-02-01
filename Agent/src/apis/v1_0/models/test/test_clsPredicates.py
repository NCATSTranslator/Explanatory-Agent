import unittest
from apis.v1_0.models.clsPredicates import clsPredicates


class test_clsPredicates(unittest.TestCase):

    def test_predicate_values(self):
        actual = clsPredicates().return_accepted()
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
