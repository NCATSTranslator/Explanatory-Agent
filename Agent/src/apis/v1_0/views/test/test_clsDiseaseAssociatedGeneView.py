import unittest
import json
import os
from modApp import app
import requests_mock
from apis.v1_0.views.clsDiseaseAssociatedGeneView import DiseaseAssociatedGeneView
from apis.v1_0.models.clsQuery import clsQuery
import requests


class test_clsQueryView(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        self.app = None

    @staticmethod
    def loadJsonFromFile(fileName):
        fullPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), fileName)
        with open(fullPath) as file:
            return json.load(file)

    @staticmethod
    def createQueryFromFile(fileName):
        fullPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), fileName)
        with open(fullPath) as file:
            query = clsQuery()
            query.query_graph = json.load(file)
            return query

    def test_supports_query_nominal(self):
        query = self.createQueryFromFile("DiseaseAssociatedGene/test_user_request_body_nominal.json")
        view = DiseaseAssociatedGeneView(query)
        result = view.supports_query(query.query_graph)
        self.assertEqual(True, result)

    def test_supports_query_not_supported(self):
        query = self.createQueryFromFile("General/test_user_request_body_not_supported.json")
        view = DiseaseAssociatedGeneView(query)
        result = view.supports_query(query.query_graph)
        self.assertEqual(False, result)


if __name__ == '__main__':
    unittest.main()
