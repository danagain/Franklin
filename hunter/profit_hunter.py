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

BTC_PER_PURCHASE = 0.00200000

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
    bittrex = Bittrex(market)
    mea = bittrex.calculate_mea(10, 'hour')
    mea2 = bittrex.calculate_mea(20, 'hour')
    balance = bittrex.get_balance()
    current_state = ""
    if mea > mea2:
        current_state = "InitTrendingUp"
    else:
        current_state = "InitTrendingDown"

    while True:
        #test the historical data is getting called properly, interval, hour
        mea = bittrex.calculate_mea(10, 'hour')
        mea2 = bittrex.calculate_mea(20, 'hour')
        balance = bittrex.get_balance()
        #if the smaller period mea has risen 1.5% above the larger period mea then buy
        if balance is not None:
            if mea >= (1.0015 * mea2) and current_state != "InitTrendingUp" and balance == 0:
                latest_summary = bittrex.get_latest_summary()
                ask = latest_summary['Ask']
                qty = BTC_PER_PURCHASE / ask
                bittrex.place_buy_order(qty, ask)
                current_state = "TrendingUp"
            #if the smaller period mea has fallen 1.5% below the larger period mea then sell
            if mea <= (0.9985 * mea2) and current_state == "TrendingUp" and balance > 0:
                latest_summary = bittrex.get_latest_summary()
                bid = latest_summary['Bid']
                qty = balance
                bittrex.place_sell_order(bid)
                current_state = "TrendingDown"

        print("ema 10  ", market, " ", mea )
        print("ema 20  ", market, " ", mea2 )
        time.sleep(300)


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
