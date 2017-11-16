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
import numpy as np
import urllib.request
import ssl
from bittrex import Bittrex
from apicall import ApiCall

# Loop/Based Settings
LOOP_SECONDS = int(os.environ['LOOP_SECONDS'])
COLLECTION_MINUTES = int(os.environ['COLLECTION_MINUTES'])
DATACOUNT = COLLECTION_MINUTES * (60/LOOP_SECONDS)

# For talking with Splunk Container
ssl._create_default_https_context = ssl._create_unverified_context

# Init Settings in relation to profits/loss
BTC_PER_PURCHASE = 0.00060000

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
        self.lock = threading.Lock()

    def run(self):
        """
        Custom Override of the Thread Librarys run function to start the
        thread work function
        """
        thread_work(self.market, self.lock)


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


def get_data(market):
    last_price = []
    datetime_data = []
    bid_price = []
    ask_price = []
    try:
        query = '?n={0}'.format(DATACOUNT)
        endpoint_url = 'http://web-api:3000/api/bittrex/{0}/{1}'.format(market, query)
        resp = requests.get(url=endpoint_url)
        data = json.loads(resp.text)
        if data is None:
            print("No market data, hunter out!")
            sys.exit(1)
        else:
            for doc in data:  # Iterate stored documents
                last_price.append(doc['Last'])
                datetime_data.append(doc['TimeStamp'])
                bid_price.append(doc['Bid'])
                ask_price.append(doc['Ask'])
            avgrecentprice = np.mean(last_price[(len(last_price) - int(DATACOUNT)):-1])
            recentstd = np.std(last_price[(len(last_price) - int(DATACOUNT)):-1])
            recentstdupper = avgrecentprice + 2*(recentstd/2)
            recentstdlower = avgrecentprice - 2*(recentstd/2)
            datedata = datetime_data[-1]

            return last_price, recentstdupper, recentstdlower,\
            datedata, bid_price, ask_price
    except requests.exceptions.RequestException as error:
        print(error)
        sys.exit(1)



def thread_work(market, lock):
    """

    Thread_work handles all of the work each thread must continually
    perform whilst in a never ending loop

    @param market: The stock/market to be monitored

    """
    bittrex = Bittrex(market)#create an instance of the Bittrex class
    current_state = "NoBuy"#init the current state variable to NoBuy
    price = 0#variable to keep track of what price we are buying shares at
    while True:
        #Request the latest data each loop
        last_price, stdupper,\
        stdlower, time_stamp, bid_price, ask_price = get_data(market)
        # If the current price has fallen below our threshold, it's time to buy
        if last_price[-1] < (0.999*stdlower) and current_state == "NoBuy" and \
                        stdupper >= (last_price[-1] * 1.0025):
                        qty = BTC_PER_PURCHASE / last_price[-1]
                        price = last_price[-1]
                        current_state = bittrex.place_buy_order(qty, price)
        #if state variable is ActiveBuy then an order has been sucessfully filled and we now need to
        #place an immediate sell order at our desired profit margin
        if  current_state == "ActiveBuy":
            sell_goal = price * 1.006 #sell for a 0.1% profit
            current_state = bittrex.place_sell_order(sell_goal)
        #if we are in a current state where we have placed a sell then lets keep an eye on our balance
        #so we know when our sell order has been filled, then update our state
        if current_state == "SellPlaced":
            check_balance = bittrex.get_balance()
            if check_balance == 0 or check_balance == None:
                current_state = "NoBuy"
        #if the price is tanking after making a purchase then we need to cut our losses and cancel
        #our current sell and re list it at a lower price
        if last_price[-1] <= (price * 0.996) and current_state == "SellPlaced":
            bittrex.cancel_order()
            price = last_price[-1] #update the price variable
            bittrex.place_sell_order(price)

        hunter_dict = {'market': market, 'Bid':bid_price[-1], 'Ask':ask_price[-1], 'Last':last_price[-1], 'Upper':stdupper,\
         'Lower':stdlower, 'Time':time_stamp, 'Transactions':trans_count,\
         'Balance':profitloss, 'Profit':PROFIT, 'Loss':LOSS, 'Net':PROFIT_MINUS_LOSS}
        token = os.environ['SPLUNKTOKEN']
        print(hunter_dict)
        send_event("splunk", token, hunter_dict)
        time.sleep(3)


if __name__ == "__main__":
    print("Waiting for correct amount of data")
    #time_for_data = COLLECTION_MINUTES * 60
    time.sleep(10)
    #time.sleep(time_for_data)
    apicall = ApiCall() #instance of the ApiCall class
    markets = aipcall.get_markets() # Get all of the markets from the WEB-API
    # Add 15 min wait here for profit testing phase
    THREADS = []

    for c in range(0, len(markets)):
        t = MyThread(markets[c])
        t.setDaemon(True)
        THREADS.append(t)
    for i in range(0, len(markets)):
        THREADS[i].start()
        time.sleep(2)
    while threading.active_count() > 0:
        time.sleep(30)
