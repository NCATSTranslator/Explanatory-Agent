import unittest
from ..modTextUtils import isNullOrWhiteSpace


class test_modTextUtils(unittest.TestCase):

    def test_isNullOrWhiteSpace_with_None(self):
        self.assertEqual(True, isNullOrWhiteSpace(None))

    def test_isNullOrWhiteSpace_with_white_space(self):
        self.assertEqual(True, isNullOrWhiteSpace(" "))

    def test_isNullOrWhiteSpace_with_any_string(self):
        self.assertEqual(False, isNullOrWhiteSpace("any"))

    def test_isNullOrWhiteSpace_with_number(self):
        self.assertEqual(False, isNullOrWhiteSpace(5))


if __name__ == '__main__':
    unittest.main()