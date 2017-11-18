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
        
    def test_get_summary(self):
        summary = {"success":True,"message":"","result":[{"MarketName":"BTC-NEO","High":0.0063,"Low":0.00440027,"Volume":4473629.32713295,"Last":0.005872,"BaseVolume":23954.60058103,"TimeStamp":"2017-11-18T20:05:51.62","Bid":0.00585955,"Ask":0.005872,"OpenBuyOrders":10299,"OpenSellOrders":20766,"PrevDay":0.0046,"Created":"2016-10-26T01:28:31.96"}]}
        result = summary['result'][0]
        self.assertEqual(result['Bid'], 0.00585955)
