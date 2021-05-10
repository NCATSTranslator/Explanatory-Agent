import unittest
from ..modTextUtils import isNullOrWhiteSpace, resolveDefaultValue


class test_modTextUtils(unittest.TestCase):

    def test_isNullOrWhiteSpace_with_None(self):
        self.assertEqual(True, isNullOrWhiteSpace(None))

    def test_isNullOrWhiteSpace_with_white_space(self):
        self.assertEqual(True, isNullOrWhiteSpace(" "))

    def test_isNullOrWhiteSpace_with_blank_string(self):
        self.assertEqual(True, isNullOrWhiteSpace(""))

    def test_isNullOrWhiteSpace_with_any_string(self):
        self.assertEqual(False, isNullOrWhiteSpace("any"))

    def test_isNullOrWhiteSpace_with_number(self):
        self.assertEqual(False, isNullOrWhiteSpace(5))

    def test_resolveDefaultValue_with_None(self):
        self.assertEqual(5, resolveDefaultValue(value=None, default=5))

    def test_resolveDefaultValue_with_white_space(self):
        self.assertEqual(5, resolveDefaultValue(value=" ", default=5))

    def test_resolveDefaultValue_with_blank_string(self):
        self.assertEqual(5, resolveDefaultValue(value="", default=5))

    def test_resolveDefaultValue_with_any_string(self):
        self.assertEqual("any", resolveDefaultValue(value="any", default=5))

    def test_resolveDefaultValue_with_number(self):
        self.assertEqual(6, resolveDefaultValue(value=6, default=5))


if __name__ == '__main__':
    unittest.main()
