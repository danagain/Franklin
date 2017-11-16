import unittest
from getdata import GetData
from bittrex import Bittrex





class GetDataTest(unittest.TestCase):

    def setUp(self):
        self.getdata = GetData()
        self.bittrex = Bittrex("BTC-ETH")

    def test_returned_values(self):
        data = self.getdata.return_data()
        self.assertEqual(0.0113, data[-1])

    def test_order_qty(self):
        qty = 0.35723895723985789325798327 #an amount longer than required
        qty = round(qty, 8)
        self.assertEqual(0.35723896, qty)

    def test_string_split(self):
        market = 'BTC-ETH'
        coin = market.split('-')
        self.assertEqual(coin[-1], 'ETH')

    def test_get_uuid(self):
        get_uuid = {"success":True,"message":"","result":[{"Uuid":None,"OrderUuid":"2ae79492-8cf9-4e0f-9546-22d6bc9f160f","Exchange":"BTC-ETH","OrderType":"LIMIT_SELL","Quantity":0.0276776,"QuantityRemaining":0.0276776,"Limit":0.04358533,"CommissionPaid":0,"Price":0,"PricePerUnit":None,"Opened":"2017-11-16T09:09:37.907","Closed":None,"CancelInitiated":False,"ImmediateOrCancel":False,"IsConditional":False,"Condition":"NONE","ConditionTarget":None}]}
        result_return = get_uuid['result'] #get the uuid from the returned request
        uuid = {'Coin':result_return[0]['OrderUuid']} #store into a dictionary
        self.assertEqual(uuid['Coin'], "2ae79492-8cf9-4e0f-9546-22d6bc9f160f")
