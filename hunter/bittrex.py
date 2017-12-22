"""
This module is responsible for handling all of the bittrex
functionality necessary. This involves buying, selling, canceling of orders
and checking current balances.
"""
from apicall import ApiCall
import time
import requests
import json

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
        """
        balance_return = self.apicall.http_request('Balance', self.coin, 'Get')
        while type(balance_return) is not dict:
            balance_return = self.apicall.http_request('Balance', self.coin, 'Get')
            time.sleep(2)
        result_return = balance_return['result']
        current_balance = result_return['Balance']
        return current_balance

    def get_btc_balance(self):
        """
        Get the current bitcoin balance of the account
        """
        coin_dict = {"Coin":"BTC"}
        balance_return = self.apicall.http_request('Balance', coin_dict, 'Get')
        while type(balance_return) is not dict:
            balance_return = self.apicall.http_request('Balance', coin_dict, 'Get')
            time.sleep(2)
        result_return = balance_return['result']
        current_balance = result_return['Balance']
        return current_balance

    def get_latest_summary(self):
        #wrapping the market in a dict for the http func
        market = {'Coin': self.market}
        summary = self.apicall.http_request("summary", market, 'Get')
        while summary == None or isinstance(summary, dict) == False :
            summary = self.apicall.http_request("summary", market, 'Get')
            time.sleep(2)

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
            time.sleep(2)
            #Getting the current balance of our coin
            current_balance = self.get_balance()
            #If the balance of our coin is greater than zero, then our order has
            #been filled and we can exit our loop
            if current_balance is not None:
                if current_balance > 0:
                    return "InTrade"

        #At this point our loop is finished and it's been 1 min without our order filling
        self.cancel_order() #cancel the order
        return "HourlyBuyZone" #bot couldnt buy so keep hunting

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
        time.sleep(2)
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
        @param period: The period of time for which the ema will be calculated over
        @param interval: The desired tick interval
        """
        closing_avg = sum(self.apicall.get_historical(self.market, period, interval))
        return (closing_avg / period)


    def calculate_ema(self, period, interval):
        """
        This function calcualtes our moving exponential averages that are used
        to determine our buy and sell signals.
        @param period: The period of time for which the ema will be calculated over
        @param interval: The desired tick interval
        """
        last_closing_price = self.apicall.get_historical(self.market, period, interval)
        while last_closing_price == None or isinstance(last_closing_price, list) == False:
            last_closing_price = self.apicall.get_historical(self.market, period, interval)
            time.sleep(2)

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
        #This comment section can be used for 15min ticks if needed
        EMA_yesterday = last_closing_price[0]
        counter = 0
        for i in range(len(last_closing_price)-1):
            if counter % 3 == 0:
                EMA_today = (last_closing_price[i + 1] * K) + (EMA_yesterday * (1 - K))
                EMA_yesterday = EMA_today
            counter += 1
            """
        EMA_yesterday = last_closing_price[0]
        for i in range(len(last_closing_price)-1):
            EMA_today = (last_closing_price[i + 1] * K) + (EMA_yesterday * (1 - K))
            EMA_yesterday = EMA_today
        return EMA_today

    def calculate_rsi(self, period, interval):
        """
        This function calculates the relative strength index of the market
        """
        last_closing_price = self.apicall.get_historical(self.market, period, interval)
        while last_closing_price == None or isinstance(last_closing_price, list) == False:
            time.sleep(2)
            last_closing_price = self.apicall.get_historical(self.market, period, interval)

        #AvgUt = α * Ut + ( 1 – α ) * AvgUt-1
        #AvgDt = α * Dt + ( 1 – α ) * AvgDt-1
        #α = 2 / ( N + 1 )  ALTERNATIVE EMA CONSTANT
        #α = 1 / N     J. Welles Wilder method
        #N = RSI period
        #For example, for RSI 14 the formula for average up move is:
        #AvgUt = 1/14 * Ut + 13/14 * AvgUt-1
        up_list = []
        down_list = []
        """
        This first for loop calculates all of the differences in the price closes and appends them to
        the corrosponding arrays - kept it in 2 lists for simplicity
        """
        for i in range(len(last_closing_price)-1):
            if last_closing_price[i + 1] == last_closing_price[i]:
                down_list.append(0)
                up_list.append(0)

            elif last_closing_price[i + 1] > last_closing_price[i]:
                up_list.append(last_closing_price[i + 1] - last_closing_price[i])
                down_list.append(0)
            else:
                down_list.append(abs(last_closing_price[i + 1] - last_closing_price[i]))
                up_list.append(0)
        """
        Now I need the smoothed exponential moving averages of the values calculated above
        """
        K = 1/period
        N = period
        avgUp_yesterday = up_list[0]
        avgDown_yesterday = down_list[0]
        for i in range(len(up_list)-1):
            #For the Up avg
            avgUp_today = (up_list[i + 1] * K) + (avgUp_yesterday * (1 - K))
            avgUp_yesterday = avgUp_today
            #For the Down avg
            avgDown_today = (down_list[i + 1] * K) + (avgDown_yesterday * (1 - K))
            avgDown_yesterday = avgDown_today
        """
        Now that we have the averages we can calculate the relative strength
        """
        #RS = AvgU / AvgD
        RS = avgUp_today / avgDown_today
        #RSI = 100 – 100 / ( 1 + RS)
        RSI = 100 - (100 / (1 + RS))
        return RSI


    def last_closing(self, period, interval):
        last_closing_price = self.apicall.get_historical(self.market, period, interval)
        while last_closing_price == None:
            last_closing_price = self.apicall.get_historical(self.market, period, interval)
        return last_closing_price[-1]
