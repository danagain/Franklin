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
    Thread work now needs to check the two current moving exponential values
    to determine if an overlap greater than our set threshold has occured.
    In the instance that the overlap occurs the appropriate action will be taken
    """
    #make an instance of the bittrex class which takes market as a constructor arg
    print("made it in the thread work")
    bittrex = Bittrex(market)
    time.sleep(10)
    #"hour", "hour", "thirtyMin", "hour" and "day"
    mea = bittrex.calculate_mea(10, 'hour')
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
        #if the smaller period mea has risen 1.5% above the larger period mea then buy
        if balance is not None:
            """
            Buying Logic

            """
            #if the inital state is trending up over time the price dips then we have to
            #re adjust the ciurrnet state so that the hunter will buy
            if current_state == "InitTrendingUp" and mea < (0.999 * mea2):
                current_state = "TrendingDown"
            #If we the ema lines are forming the opening arc and we are in the right state to purchase, then enter the purchase logic
            while mea > (1.009 * mea2) and current_state != "InitTrendingUp" and current_state != "TrendingUp" and balance == 0 and  gain_loss_percent <= 1.15:
                """
                While we are in between these thresholds we only want to buy at a reasonable ask price
                """
                mea = bittrex.calculate_mea(10, 'hour')
                time.sleep(10)
                mea2 = bittrex.calculate_mea(21, 'hour')
                latest_summary = bittrex.get_latest_summary()
                ask = latest_summary['Ask']
                if ask < mea*1.025:
                    #If we get in here, I want to see what market
                    print("\n###############\n")
                    print("Buy Signal for: ", market)
                    print("\n###############\n")
                    #ask = mea2
                    qty = BTC_PER_PURCHASE / ask
                    current_state = bittrex.place_buy_order(qty, ask)
                    if current_state == "TrendingUp":
                        current_purchase = ask #this the price that the bot bought at
                        break
                time.sleep(40)

            """
            SELLING LOGIC
            """
            """
            If the lines cross back then sell
            """
            while current_state == "TrendingUp":
                mea = bittrex.calculate_mea(10, 'hour')
                time.sleep(10)
                mea2 = bittrex.calculate_mea(21, 'hour')
                balance = bittrex.get_balance()
                latest_summary = bittrex.get_latest_summary()
                if current_state == "TrendingUp" and (mea * 0.998) < mea2:
                    bid = latest_summary['Bid']
                    qty = balance
                    bittrex.place_sell_order(bid)
                    current_state = "TrendingDown"
                """
                This is our stop loss logic
                """
                if current_state == "TrendingUp":
                    if latest_summary['Last'] <= (current_purchase * 0.95): #If somethings gone horrible wrong and we are down 5 percent on a purchase then we need to bail
                        bid = latest_summary['Last']
                        bittrex.place_sell_order(bid)
                        if mea > mea2:
                            current_state = "InitTrendingUp"#if our 10 mea is above the 21 then set the right state
                        else:
                            current_state = "StoppedLoss"# as long as state is not InitTrendingUp hunter will buy again at the right time
                """
                If we make a 15 percent gain then sell
                """
                if current_state == "TrendingUp":
                    if latest_summary['Bid'] > (current_purchase * 1.10):
                        bid = latest_summary['Bid']
                        bittrex.place_sell_order(bid)
                        current_state = "InitTrendingUp"

                if balance > 0 and (latest_summary['Last'] * balance) <= (0.00100 * 0.95):
                        bid = latest_summary['Last']
                        bittrex.place_sell_order(bid)
                        current_state = "InitTrendingUp" # this will stop hunter buying the same thing and losing possibly multiple times
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
    #time.sleep(time_for_data)
    apicall = ApiCall() #instance of the ApiCall class
    markets = apicall.get_markets() # Get all of the markets from the WEB-API
    # Add 15 min wait here for profit testing phase
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
