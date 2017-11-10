import unittest
from getdata import GetData

class GetDataTest(unittest.TestCase):

    def setUp(self):
        self.getdata = GetData()

    def test_returned_values(self):
        data = self.getdata.return_data()
        self.assertEqual(0.0113, data[-1])

    def test_order_qty(self):
        qty = 0.35723895723985789325798327 #an amount longer than required
        qty = round(qty, 8)
        self.assertEqual(0.35723896, qty)
