"""
This module is responsible for handling all of the bittrex
functionality necessary. This involves buying, selling, canceling of orders
and checking current balances.
"""
from apicall import ApiCall

class Bittrex:
    """
    Class constructor, initalising the market and coin name relevant to each
    thread
    """
    def __init__(self, market):
        self.market = market
        split_market_string = market.split('-')
        #coin is a dict for our http_request function
        self.coin = {"Coin": split_market_string[-1]}
        self.apicall = ApiCall()


    def get_balance(self, coin):
        """
        Get the current balance for a given market
        @param coin: The stock/market
        """
        balance_return = self.apicall.http_request('Balance', coin, 'Get')
        result_return = balance_return['result']
        current_balance = result_return['Balance']
        return current_balance

    def place_buy_order(self, market, coin, qty, price):
        """
        Place a buy order, check every 20 seconds for 1 minuite if order has
        been executed. If order is executed then call place_sell_order, else we
        need to cancel this order and try to buy again at the next buy oppourtunity
        @param coin: The stock/market to be bought
        """
        #Dictionary of purchase order params for WEB-API to send to bittrex
        purchase_dict = {'Coin': market, 'OrderType':'LIMIT',\
            'Quantity': qty, 'Rate':price,\
            'TimeInEffect':'GOOD_TIL_CANCELLED', \
            'ConditionType': 'NONE', 'Target': 0}
        #Sending the purchase request to our web-api
        self.apicall.http_request("buy", purchase_dict, 'Post')
        #Lets wait 1 minuite, checking 3 times on the state of our purchase order
        for i in range(3):
            time.sleep(20)
            #Getting the current balance of our coin
            current_balance = get_balance(coin)
            #If the balance of our coin is greater than zero, then our order has
            #been filled and we can exit our loop
            if current_balance > 0:
                break
        #At this point our loop is finished and it's been 1 min without our order filling

    def cancel_order(self, market):
        """
        Cancel a currently active order on bittrex
        @param coin: The stock/market
        """
        #First let's get the current uuid of the active order by calling the web-api
        #put the coin in a dictionary for the httpreq function
        get_uuid = self.apicall.http_request('order', market, 'Get')
        print(get_uuid)
        return None
