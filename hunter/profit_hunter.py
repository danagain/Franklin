"""
Module to interact with WEB-API to locate and signal for potentially
profitable trades. Market stocks to monitor are passed from the WEB-API
where a thread is spawned to handle each market.
"""
import os
import threading
import time
import json
import sys
import requests
import urllib.request
import ssl
from bittrex import Bittrex
from apicall import ApiCall

BTC_PER_PURCHASE = 0.00150000
# For talking with Splunk Container
ssl._create_default_https_context = ssl._create_unverified_context



class MyThread(threading.Thread):
    """
    Class to handle all of the threading aspect
    """
    def __init__(self, market):
        """
        Class constructor for initialisation
        @param market: The market/stock this thread is
        responsible for monitoring
        """
        threading.Thread.__init__(self)
        self.market = market

    def run(self):
        """
        Custom Override of the Thread Librarys run function to start the
        thread work function
        """
        thread_work(self.market)


def send_event(splunk_host, auth_token, log_data):
   """Sends an event to the HTTP Event collector of a Splunk Instance"""

   try:
      # Integer value representing epoch time format
     # event_time = 0

      # String representing the host name or IP
      host_id = "splunk"

      # String representing the Splunk sourcetype, see:
      # docs.splunk.com/Documentation/Splunk/6.3.2/Data/Listofpretrainedsourcetypes
      source_type = "access_combined"

      # Create request URL
      request_url = "https://%s:8088/services/collector" % splunk_host

      post_data = {
        # "time": event_time,
         "host": host_id,
         "sourcetype": source_type,
         "event": log_data
      }

      # Encode data in JSON utf-8 format
      data = json.dumps(post_data).encode('utf8')

      # Create auth header
      auth_header = "Splunk %s" % auth_token
      headers = {'Authorization' : auth_header}

      # Create request
      req = urllib.request.Request(request_url, data, headers)
      response = urllib.request.urlopen(req)

      # read response, should be in JSON format
      read_response = response.read()

      try:
         response_json = json.loads(str(read_response)[2:-1])

         if "text" in response_json:
            if response_json["text"] == "Success":
               post_success = True
            else:
               post_success = False
      except:
         post_success = False

      if post_success == True:
         # Event was recieved successfully
         print ("Event was recieved successfully by the API")
      else:
         # Event returned an error
         print ("Error sending request.")

   except Exception as err:
      # Network or connection error
      post_success = False
      print ("Error sending request")
      print (str(err))

   return post_success

def track_btc_balance(bittrex):
    balance = bittrex.get_btc_balance()
    return balance

def thread_work(market):
    """
    Designated area for threads to buy and sell
    """
    def btc_mea(bittrex):
        mea = bittrex.calculate_mea(10, 'fifteenMinBtc')
        time.sleep(5)
        mea2 = bittrex.calculate_mea(21, 'fifteenMinBtc')
        #print("btc mea 10 ", mea)
        #print("btc mea 21 ", mea2)
        if mea2 > 1.001 * mea:
            #print("returning true")
            return True
        return False
    bittrex = Bittrex(market)#make an instance of the bittrex class which takes market as a constructor arg
    apicall = ApiCall()
    time.sleep(10)
    mea = bittrex.calculate_mea(10, 'hour')#"oneMin", "fiveMin", "thirtyMin", "hour" and "day"
    time.sleep(10)
    mea2 = bittrex.calculate_mea(21, 'hour')
    print("ema 10  ", market, " ", mea )
    print("ema 21  ", market, " ", mea2 )
    current_purchase = 99999999999
    balance = bittrex.get_balance()
    current_state = ""
    counter = 0
    init_ticker = 0


    if mea > mea2:
        current_state = "InitTrendingUp"
    else:
        current_state = "TrendingDown"

    while True:
        btc_daily_highs = bittrex.get_btc_daily_highs("USDT-BTC", 'day')
        mea = bittrex.calculate_mea(10, 'hour')
        time.sleep(10)
        mea2 = bittrex.calculate_mea(21, 'hour')
        if counter == 0:
            init_ticker = mea
        counter = 1
        balance = bittrex.get_balance()
        print("Current Balance: ", market, "is: ", balance)
        latest_summary = bittrex.get_latest_summary()
        latest_btc_summary = bittrex.get_latest_btc_summary()
        btc_daily_highs.append(latest_btc_summary['High']) #check if the new ATH is currently happening, add to list
        #print("Last 10 Bitcoin peaks and current high: ", btc_daily_highs)
        last_closing_price = bittrex.last_closing(1, 'hour')
        gain_loss_percent = latest_summary['Last']/latest_summary['PrevDay']
        if current_state == "InitTrendingUp" and mea < (0.999 * mea2):
            current_state = "TrendingDown"
            #If  ema lines are forming the opening arc and we are in the right state to purchase, then enter the purchase logic
        btc_mea(bittrex)
        if balance is not None:
            while mea > (1.009 * mea2) and current_state != "InitTrendingUp" and current_state != "TrendingUp" and balance == 0 and  gain_loss_percent <= 1.15 \
             and latest_summary['Volume'] > 600:
                #while mea > (1.009 * mea2) and current_state != "InitTrendingUp" and current_state != "TrendingUp"  and  gain_loss_percent <= 1.15: # TRAIL ACCOUNT
                """
                While we are in between these thresholds we only want to buy at a reasonable ask price
                """
                btc_balance = track_btc_balance(bittrex) #check btc balance
                if btc_balance < 1.0025 * BTC_PER_PURCHASE:#if we dont have enough then dont try and buy
                    break
                mea = bittrex.calculate_mea(10, 'hour')
                time.sleep(10)
                mea2 = bittrex.calculate_mea(21, 'hour')
                latest_summary = bittrex.get_latest_summary()
                ask = latest_summary['Ask']
                if ask < mea * 1.015:
                        #If we get in here, I want to see what market
                    for i in range(10):
                        print("\n###############\n")
                        print("Buy Signal for: ", market)
                        print("\n###############\n")
                    qty = BTC_PER_PURCHASE / ask
                    current_state = bittrex.place_buy_order(qty, ask)
                    if current_state == "TrendingUp":
                        current_purchase = ask #price that the bot bought at
                        break
                time.sleep(40)

        else:
            while mea > (1.009 * mea2) and current_state != "InitTrendingUp" and current_state != "TrendingUp" \
            and  gain_loss_percent <= 1.15 and latest_summary['Volume'] > 600:
                    #while mea > (1.009 * mea2) and current_state != "InitTrendingUp" and current_state != "TrendingUp"  and  gain_loss_percent <= 1.15: # TRAIL ACCOUNT
                """
                While we are in between these thresholds we only want to buy at a reasonable ask price
                """
                mea = bittrex.calculate_mea(10, 'hour')
                time.sleep(10)
                mea2 = bittrex.calculate_mea(21, 'hour')
                latest_summary = bittrex.get_latest_summary()
                ask = latest_summary['Ask']
                if ask < mea * 1.015:
                            #If we get in here, I want to see what market
                    for i in range(10):
                        print("\n###############\n")
                        print("Buy Signal for: ", market)
                        print("\n###############\n")
                    qty = BTC_PER_PURCHASE / ask
                    current_state = bittrex.place_buy_order(qty, ask)
                    if current_state == "TrendingUp":
                        current_purchase = ask #price that the bot bought at
                        break
                time.sleep(40)

            """
            Selling Logic
            """
        while current_state == "TrendingUp":
                ticker_data = apicall.get_last_ticker_data(market, 1, 'fiveMin')
                last_closing_price = bittrex.last_closing(1, 'hour')
                mea = bittrex.calculate_mea(10, 'hour')
                time.sleep(10)
                mea2 = bittrex.calculate_mea(21, 'hour')
                balance = bittrex.get_balance()
                latest_summary = bittrex.get_latest_summary()
                latest_btc_summary = bittrex.get_latest_btc_summary()
                gain = (latest_summary['Bid']/current_purchase)
                print("Current Gain on ", market, " is: ", gain)

                """
                If the lines cross back then sell
                """
                if (mea * 0.998) < mea2:
                    bid = latest_summary['Bid']
                    qty = balance
                    bittrex.place_sell_order(bid)
                    current_state = "TrendingDown"

                """
                This is to detect and bail out of pump and dumps at a small profit

                I was going to add some conditions to make sure we are in profit range, but im going to just
                see how selling no matter what, when the ticker rolls over from a pump
                """
                if (ticker_data[0]['C'] / ticker_data[0]['O']) > 1.15: # if the pump in the last hour was greater than a 15 percent rise, get out straight away
                    print("Five Min ticker pump sell for ",market)
                    bid = latest_summary['Bid']
                    bittrex.place_sell_order(bid)
                    current_state = "InitTrendingUp"

                """
                This is our stop loss logic
                """
                if latest_summary['Last'] <= (current_purchase * 0.9): #If down 10% then sell
                    bid = latest_summary['Last']
                    bittrex.place_sell_order(bid)
                    if mea > mea2:
                        current_state = "InitTrendingUp"#if  10 mea is above  21 mea, set the right state
                    else:
                        current_state = "StoppedLoss"# as long as state is not InitTrendingUp hunter will buy again at the right time

                #seperate rules for these coins
                good_coins = ["BTC-LTC", "BTC-ETH", "BTC-DASH", "BTC-NEO", "BTC-XRP", "BTC-ZEC", "BTC-BCC", "BTC-ADA", "BTC-POWR", "BTC-BTG"]
                """
                If we make a 20 percent gain then sell
                """
                if market in good_coins:
                    if latest_summary['Bid'] > (current_purchase * 1.20):
                        bid = latest_summary['Bid']
                        bittrex.place_sell_order(bid)
                        current_state = "InitTrendingUp"
                """
                Sell shit coins for 10 percent gains
                """
                if market not in good_coins:
                    if latest_summary['Bid'] > (current_purchase * 1.10):
                        bid = latest_summary['Bid']
                        bittrex.place_sell_order(bid)
                        current_state = "InitTrendingUp"
                        print("Making a sell now for ", market, " at ", bid)

                #Shouldn't need this if block, but hunter has not sold for some reason when it should
                if gain > 1.1 and market not in good_coins:
                    print("Gain > 1.1")
                    bid = latest_summary['Bid']
                    bittrex.place_sell_order(bid)
                    current_state = "InitTrendingUp"
                    print("Making a sell now for ", market, " at ", bid)

                """
                This is useful for when the hunter doesn't have previous buys loaded into memory for stop loss prevention,
                the calculation is based on the BTC_PER_PURCHASE global variable value
                """
                if balance > 0 and (latest_summary['Last'] * balance) <= (BTC_PER_PURCHASE * 0.9):
                        bid = latest_summary['Last']
                        bittrex.place_sell_order(bid)
                        current_state = "InitTrendingUp" #this will stop hunter buying the same thing and losing possibly multiple times

                """
                If bitcoins current price is greater or equal to 1.02 * it's previous daily closing high and hunter purchases
                are at a profit then sell as it's likely BTC will push and drive prices down quickly
                """
                if latest_btc_summary['Last'] >= (0.995 * max(btc_daily_highs)) and latest_summary['Bid'] > current_purchase:
                        bid = latest_summary['Last']
                        bittrex.place_sell_order(bid)
                        current_state = "InitTrendingUp" #this will stop hunter buying the same thing and losing possibly multiple times

                time.sleep(5)

        print("Last Price: ",latest_summary['Last'])
        print("Current Purchase: ", current_purchase)
        print("ema 10  ", market, " ", mea )
        print("ema 21  ", market, " ", mea2 )
        print("Current state:", current_state, "\n" )
        if init_ticker == mea:
            time.sleep(120)
        else:
            time.sleep(1800)
            btc_daily_highs = bittrex.get_btc_daily_highs("USDT-BTC", 'day')


if __name__ == "__main__":
    print("Waiting for correct amount of data")
    time.sleep(3)
    apicall = ApiCall() #instance of the ApiCall class
    markets = apicall.get_markets() # Get all of the markets from the WEB-API
    THREADS = []
    for c in range(0, len(markets)):
        t = MyThread(markets[c])
        t.setDaemon(True)
        THREADS.append(t)
    for i in range(0, len(markets)):
        THREADS[i].start()
        time.sleep(20)
    while threading.active_count() > 0:
        time.sleep(1000)
