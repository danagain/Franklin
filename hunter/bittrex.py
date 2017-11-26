"""
This module is responsible for handling all of the bittrex
functionality necessary. This involves buying, selling, canceling of orders
and checking current balances.
"""
from apicall import ApiCall
import time
import requests
import json
import pandas as pd

class Bittrex:
    """
    Class constructor, initalising the market and coin name relevant to each
    thread
    """
    def __init__(self, market):
        self.market = market
        split_market_string = market.split('-')
        self.coin = {"Coin": split_market_string[-1]}#dict for our http_request function
        self.apicall = ApiCall()#create instance of the ApiCall class

    def get_balance(self):
        """
        Get the current balance for a given market
        @param coin: The stock/market
        """
        balance_return = self.apicall.http_request('Balance', self.coin, 'Get')
        while type(balance_return) is not dict:
            balance_return = self.apicall.http_request('Balance', self.coin, 'Get')
            time.sleep(5)
        result_return = balance_return['result']
        current_balance = result_return['Balance']
        return current_balance

    def get_latest_summary(self):
        #wrapping the market in a dict for the http func
        market = {'Coin': self.market}
        summary = self.apicall.http_request("summary", market, 'Get')
        while summary == None or isinstance(summary, dict) == False :
            summary = self.apicall.http_request("summary", market, 'Get')
            time.sleep(1)

        return summary['result'][0]

    def place_buy_order(self, qty, price):
        """
        Place a buy order, check every 20 seconds for 1 minuite if order has
        been executed. If order is executed then call place_sell_order, else we
        need to cancel this order and try to buy again at the next buy oppourtunity
        """
        #Dictionary of purchase order params for WEB-API to send to bittrex
        purchase_dict = {'Coin': self.market, 'OrderType':'LIMIT',\
            'Quantity': qty, 'Rate':price,\
            'TimeInEffect':'GOOD_TIL_CANCELLED', \
            'ConditionType': 'NONE', 'Target': 0}
        #Sending the purchase request to our web-api
        self.apicall.http_request("buy", purchase_dict, 'Post')
        #Lets wait 1 minuite, checking 3 times on the state of our purchase order
        for i in range(3):
            time.sleep(60)
            #Getting the current balance of our coin
            current_balance = self.get_balance()
            #If the balance of our coin is greater than zero, then our order has
            #been filled and we can exit our loop
            if current_balance > 0:
                return "TrendingUp"
        #At this point our loop is finished and it's been 1 min without our order filling
        self.cancel_order() #cancel the order
        return "NoBuy"

    def place_sell_order(self, price):
        """
        Place a sell order
        """
        #make sure we have the right qty
        qty = self.get_balance()
        if (qty * price) < 0.00060000:
            return "NoBuy"
        #Dictionary of sell order params for WEB-API to send to bittrex
        sell_dict = {'Coin': self.market, 'OrderType':'LIMIT',\
            'Quantity': qty, 'Rate':price,\
            'TimeInEffect':'GOOD_TIL_CANCELLED', \
            'ConditionType': 'NONE', 'Target': 0}
        #Sending the purchase request to our web-api
        self.apicall.http_request("sell", sell_dict, 'Post')
        time.sleep(4)
        return "SellPlaced"

    def cancel_order(self):
        """
        Cancel a currently active order on bittrex
        @param coin: The stock/market
        """
        #First let's get the current uuid of the active order by calling the web-api
        market_dict = {'Coin': self.market}
        get_uuid = self.apicall.http_request('orders', market_dict, 'Get')
        while get_uuid == None or isinstance(get_uuid, dict) == False:
            get_uuid = self.apicall.http_request('orders', market_dict, 'Get')
            time.sleep(2)


        result_return = get_uuid['result'] #get the uuid from the returned request
        uuid = {'Coin':result_return[0]['OrderUuid']} #store into a dictionary
        self.apicall.http_request('cancel', uuid, 'Get') #call api again

    def calculate_sma(self, period, interval):
        """
        calculates the simple moving average of the market
        @param period: The period of time for which the mea will be calculated over
        @param interval: The desired tick interval
        """
        closing_avg = sum(self.apicall.get_historical(self.market, period, interval))
        return (closing_avg / period)


    def calculate_mea(self, period, interval):
        """
        This function calcualtes our moving exponential averages that are used
        to determine our buy and sell signals.
        @param period: The period of time for which the mea will be calculated over
        @param interval: The desired tick interval
        """
        last_closing_price = self.apicall.get_historical(self.market, period, interval)
        while last_closing_price == None:
            last_closing_price = self.apicall.get_historical(self.market, period, interval)
            time.sleep(1)

        #seed = self.calculate_sma(period, interval)
        #EMA [today] = (Price [today] x K) + (EMA [yesterday] x (1 – K))
        #K = 2 ÷(N + 1)
        #N = the length of the EMA
        #Price [today] = the current closing price
        #EMA [yesterday] = the previous EMA value
        #EMA [yesterday] = the previous EMA value
        K = (2/(period + 1))
        N = period
        #Seeding the first EMA to the closing price 10 days ago
        #EMA_yesterday = last_closing_price[0]
        """
        EMA_yesterday = last_closing_price[0]
        counter = 0
        for i in range(len(last_closing_price)-1):
            if counter % 2 == 0:
                EMA_today = (last_closing_price[i + 1] * K) + (EMA_yesterday * (1 - K))
                EMA_yesterday = EMA_today
            counter += 1
            """
        EMA_yesterday = last_closing_price[0]
        for i in range(len(last_closing_price)-1):
            EMA_today = (last_closing_price[i + 1] * K) + (EMA_yesterday * (1 - K))
            EMA_yesterday = EMA_today
        return EMA_today


    def mea_pandas(self, period, interval):
        last_closing_price = self.apicall.get_historical(self.market, period, interval)
        df = pd.DataFrame(last_closing_price)
        ema = df.ewm(span=period,min_periods=0,adjust=True,ignore_na=False).mean()
        test = ema.get_values()
        return test[0][0]

    def last_closing(self, period, interval):
        last_closing_price = self.apicall.get_historical(self.market, period, interval)
        while last_closing_price == None:
            last_closing_price = self.apicall.get_historical(self.market, period, interval)
        return last_closing_price[-1]
