import unittest
import requests_mock
import requests
from ..requests_extension import request_with_global_timeout


class test_requests_extension(unittest.TestCase):

    def test_request_with_global_timeout_raises_timeout(self):

        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', "http://www.fakewebsite.com/some_endpoint", status_code=418)  # some crash
            with self.assertRaises(requests.exceptions.Timeout):
                response = request_with_global_timeout("POST", "http://www.fakewebsite.com/some_endpoint", global_timeout=0.001)

    # todo, how to register Mocker() for inside multiprocessing.Process()
    # def test_request_with_global_timeout_does_not_raise_timeout(self):
    #
    #     with requests_mock.Mocker() as mocker:
    #         mocker.register_uri('POST', "http://www.fakewebsite.com/some_endpoint", status_code=418)  # some crash
    #         response = request_with_global_timeout("POST", "http://www.fakewebsite.com/some_endpoint", global_timeout=10)
    #         with self.assertRaises(requests.exceptions.HTTPError):
    #             response.raise_for_status()

    def test_request_with_global_timeout_does_not_raise_timeout_with_no_global_timeout(self):

        with requests_mock.Mocker() as mocker:
            mocker.register_uri('POST', "http://www.fakewebsite.com/some_endpoint", status_code=418)  # some crash
            response = request_with_global_timeout("POST", "http://www.fakewebsite.com/some_endpoint", global_timeout=None)
            with self.assertRaises(requests.exceptions.HTTPError):
                response.raise_for_status()


if __name__ == '__main__':
    unittest.main()
