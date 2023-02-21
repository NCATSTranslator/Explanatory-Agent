import unittest
from apis.v1_3.queries.clsMeshNormalizedGoogleDistanceProvider import clsMeshNormalizedGoogleDistanceProvider
import requests_mock


class test_clsMeshNormalizedGoogleDistanceProvider(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_nominal(self):
        subject_name = "acetaminophen"
        object_name = "acetaminophen"
        with requests_mock.Mocker() as mocker:
            mock_arax_response = {
                "value": 1.0,
                "response_code": "OK",
            }
            mocker.register_uri('GET', 'https://arax.ncats.io/api/arax/v1.3/PubmedMeshNgd/acetaminophen/acetaminophen', json=mock_arax_response)
            provider = clsMeshNormalizedGoogleDistanceProvider(subject_name, object_name)
            provider.get_value()
        self.assertEqual(1.0, provider.value)

    def test_not_found(self):
        subject_name = "TBX3"
        object_name = "acetaminophen"
        with requests_mock.Mocker() as mocker:
            mock_arax_response = {
                "message": "Term 1 'TBX3' not found in MeSH",
                "response_code": "TermNotFound",
            }
            mocker.register_uri('GET', 'https://arax.ncats.io/api/arax/v1.3/PubmedMeshNgd/TBX3/acetaminophen', json=mock_arax_response)
            provider = clsMeshNormalizedGoogleDistanceProvider(subject_name, object_name)
            provider.get_value()
        self.assertEqual(None, provider.value)
        self.assertEqual("TermNotFound", provider.response_code)

    def test_failure(self):
        subject_name = "Subject"
        object_name = "Object"
        with requests_mock.Mocker() as mocker:
            mock_arax_response = {
                "response_code": "OK",
                "value": 0.55
            }
            mocker.register_uri('GET', 'https://arax.ncats.io/api/arax/v1.3/PubmedMeshNgd/Subject/Object', status_code=500, reason="Internal error", json=mock_arax_response)
            provider = clsMeshNormalizedGoogleDistanceProvider(subject_name, object_name)
            provider.get_value()
        self.assertEqual(None, provider.value)
        self.assertEqual(None, provider.response_code)
        self.assertEqual(None, provider.error_message)
        self.assertEqual(False, provider.response.ok)

    def test_failure_no_json(self):
        subject_name = "Subject"
        object_name = "Object"
        with requests_mock.Mocker() as mocker:
            mock_arax_response = "Not JSON"
            mocker.register_uri('GET', 'https://arax.ncats.io/api/arax/v1.3/PubmedMeshNgd/Subject/Object', status_code=500, reason="Internal error", text=mock_arax_response)
            provider = clsMeshNormalizedGoogleDistanceProvider(subject_name, object_name)
            provider.get_value()
        self.assertEqual(None, provider.value)
        self.assertEqual(None, provider.response_code)
        self.assertEqual(None, provider.error_message)
        self.assertEqual(False, provider.response.ok)
