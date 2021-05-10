# import unittest
# from unittest.mock import MagicMock
# from mockito import when, unstub
# from modApp import appFactory
# from ... import version
# from modDatabase import db
#
#
# class test_clsDummyView(unittest.TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         cls.client = appFactory().test_client()
#         cls.maxDiff = None
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.client = None
#
#     def setUp(self):
#         unstub()
#
#     def tearDown(self):
#         unstub()
#
#     def test_dummy_response(self):
#
#         sql = "select current_timestamp"
#         results = ("some time on the server",)
#
#         when(db).create_scoped_session().thenReturn(MagicMock())  # mocked session
#         when(db.session).execute(sql).thenReturn(MagicMock())  # mock cursor
#         when(db.session.execute(sql)).fetchone().thenReturn(results)  # mock results
#
#         response = self.client.get(f'/{version}/dummy', follow_redirects=True)
#         self.assertEqual(200, response.status_code)
#         self.assertEqual({"message": "some time on the server"}, response.json)
#
#
# if __name__ == '__main__':
#     unittest.main()
