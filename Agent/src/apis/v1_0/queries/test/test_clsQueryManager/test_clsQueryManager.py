import unittest
from ...clsQueryManager import clsQueryManager
import json
import os
from inspect import stack


class test_clsQueryManager(unittest.TestCase):

    @staticmethod
    def loadJsonFromFile(fileName):
        fullPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), fileName)
        with open(fullPath) as file:
            return json.load(file)

    def test_user_request_body_nominal_is_valid(self):
        self.assertEqual(True, clsQueryManager(self.loadJsonFromFile(stack()[0][3] + ".json")).userRequestBodyValidation()['isValid'])

    def test_user_request_body_bad_schema_not_valid(self):
        self.assertEqual(False, clsQueryManager(self.loadJsonFromFile(stack()[0][3] + ".json")).userRequestBodyValidation()['isValid'])


if __name__ == '__main__':
    unittest.main()
