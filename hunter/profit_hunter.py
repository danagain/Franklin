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

BTC_PER_PURCHASE = 0.00100000

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



def thread_work(market):
    """
    Designated area for threads to buy and sell
    """
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
        mea = bittrex.calculate_mea(10, 'hour')
        time.sleep(10)
        mea2 = bittrex.calculate_mea(21, 'hour')
        if counter == 0:
            init_ticker = mea
        counter = 1
        balance = bittrex.get_balance()
        latest_summary = bittrex.get_latest_summary()
        last_closing_price = bittrex.last_closing(1, 'hour')
        gain_loss_percent = latest_summary['Last']/latest_summary['PrevDay']
        if balance is not None:
            """
            Buying Logic

            """
            #if  inital state is trending up over time the price dips then we have to
            #re adjust the ciurrnet state so that the hunter will buy
            if current_state == "InitTrendingUp" and mea < (0.999 * mea2):
                current_state = "TrendingDown"
            #If  ema lines are forming the opening arc and we are in the right state to purchase, then enter the purchase logic
            while mea > (1.009 * mea2) and current_state != "InitTrendingUp" and current_state != "TrendingUp" and balance == 0 and  gain_loss_percent <= 1.15:
                """
                While we are in between these thresholds we only want to buy at a reasonable ask price
                """
                mea = bittrex.calculate_mea(10, 'hour')
                time.sleep(10)
                mea2 = bittrex.calculate_mea(21, 'hour')
                latest_summary = bittrex.get_latest_summary()
                ask = latest_summary['Ask']
                if ask < mea * 1.025:
                    #If we get in here, I want to see what market
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
                ticker_data = apicall.get_last_ticker_data(market, 1, 'hour')
                print(ticker_data[0]['C'])
                print(ticker_data[0]['O'])
                last_closing_price = bittrex.last_closing(1, 'hour')
                mea = bittrex.calculate_mea(10, 'hour')
                time.sleep(10)
                mea2 = bittrex.calculate_mea(21, 'hour')
                balance = bittrex.get_balance()
                latest_summary = bittrex.get_latest_summary()

                """
                If the lines cross back then sell
                """
                if current_state == "TrendingUp" and (mea * 0.998) < mea2:
                    bid = latest_summary['Bid']
                    qty = balance
                    bittrex.place_sell_order(bid)
                    current_state = "TrendingDown"

                """
                This is to detect and bail out of pump and dumps at a small profit

                I was going to add some conditions to make sure we are in profit range, but im going to just
                see how selling no matter what, when the ticker rolls over from a pump
                """
                if (ticker_data[0]['C'] / ticker_data[0]['O']) > 1.1: # if the pump in the last hour was greater than a 10 percent rise, get out straight away
                    bid = latest_summary['Bid']
                    bittrex.place_sell_order(bid)
                    current_state = "InitTrendingUp"

                """
                This is our stop loss logic
                """
                if current_state == "TrendingUp":
                    if latest_summary['Last'] <= (current_purchase * 0.95): #If down 5% then sell
                        bid = latest_summary['Last']
                        bittrex.place_sell_order(bid)
                        if mea > mea2:
                            current_state = "InitTrendingUp"#if  10 mea is above  21 mea, set the right state
                        else:
                            current_state = "StoppedLoss"# as long as state is not InitTrendingUp hunter will buy again at the right time

                """
                If we make a 10 percent gain then sell
                """
                if current_state == "TrendingUp":
                    if latest_summary['Bid'] > (current_purchase * 1.10):
                        bid = latest_summary['Bid']
                        bittrex.place_sell_order(bid)
                        current_state = "InitTrendingUp"

                """
                This is useful for when the hunter doesn't have previous buys loaded into memory for stop loss prevention,
                the calculation is based on the BTC_PER_PURCHASE global variable value
                """
                if balance > 0 and (latest_summary['Last'] * balance) <= (0.00100 * 0.95):
                        bid = latest_summary['Last']
                        bittrex.place_sell_order(bid)
                        current_state = "InitTrendingUp" #this will stop hunter buying the same thing and losing possibly multiple times

                """
                Need to add code to detect bitcoin movements as they effect alt coin movements
                Thoughts:
                - When bitcoins moving upwards it usually pushes the btc market backwards.
                If btc starts moving upwards, purchases at a profit will be sold
                """
                time.sleep(60)

        print("Last Price: ",latest_summary['Last'])
        print("Current Purchase: ", current_purchase)
        print("ema 10  ", market, " ", mea )
        print("ema 21  ", market, " ", mea2 )
        print("Current state:", current_state, "\n" )
        if init_ticker == mea:
            time.sleep(120)
        else:
            time.sleep(1800)


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
        time.sleep(10)
    while threading.active_count() > 0:
        time.sleep(1000)
