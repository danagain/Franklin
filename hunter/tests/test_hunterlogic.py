import unittest
from getdata import GetData

class GetDataTest(unittest.TestCase):

    def setUp(self):
        self.getdata = GetData()

    def test_returned_values(self):
        data = self.getdata.return_data()
        self.assertEqual(0.0113, data[-1])
