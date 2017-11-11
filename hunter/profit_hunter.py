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

LOOP_SECONDS = int(os.environ['LOOP_SECONDS'])
COLLECTION_MINUTES = int(os.environ['COLLECTION_MINUTES'])
DATACOUNT = COLLECTION_MINUTES * (60/LOOP_SECONDS)
ssl._create_default_https_context = ssl._create_unverified_context
BTC_PER_PURCHASE = 0.00060000
PROFIT = 0.00000000
LOSS = 0.00000000
PROFIT_MINUS_LOSS = 0.00000000

class MyThread(threading.Thread):
    """
    Class to handle all of the threading aspect
    """
    def __init__(self, coin):
        """
        Class constructor for initialisation
        @param coin: The coin/stock this thread is
        responsible for monitoring
        """
        threading.Thread.__init__(self)
        self.coin = coin
        self.lock = threading.Lock()

    def run(self):
        """
        Custom Override of the Thread Librarys run function to start the
        thread work function
        """

        thread_work(self.coin, self.lock)


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


def http_request(ptype, python_dict, method):
    """
    This function is used to post data from the hunter to the
    web-api
    @param ptype: Specifies the post type, e.g graph, buy, sell
    @param python_dict: Python dictionary containing data
    sent to web-api
    """
    try:
        endpoint_url = 'http://web-api:3000/api/{0}/{1}'.format(ptype, python_dict['Coin'])
        jsondata = json.dumps(python_dict)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        if method == 'Post':
            requests.post(endpoint_url, data=jsondata, headers=headers)
        if method == 'Get':
            r = requests.get(endpoint_url)
            x = r.json()
            return x
    except requests.exceptions.RequestException as error:
        print(error)
        sys.exit(1)

def get_coins():
    """
    This is the first function that is called as the hunter runs,
    this function makes a call to the WEB-API to determine which stocks
    are going to be hunted
    @return data: Returns a list of coins returned from the WEB-API
    """
    try:
        endpoint_url = 'http://web-api:3000/api/coins'
        resp = requests.get(url=endpoint_url)
        data = json.loads(resp.text)
        data = data[0]["coins"]
        if data is None:
            print("No coins selected in API, Hunter quiting")
            sys.exit(1)
        else:
            return data
    except requests.exceptions.RequestException as error:
        print(error)
        sys.exit(1)

def get_data(coin):
    last_price = []
    datetime_data = []
    bid_price = []
    ask_price = []
    try:
        query = '?n={0}'.format(DATACOUNT)
        endpoint_url = 'http://web-api:3000/api/bittrex/{0}/{1}'.format(coin, query)
        resp = requests.get(url=endpoint_url)
        data = json.loads(resp.text)
        if data is None:
            print("No coin data, hunter out!")
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

def thread_work(coin, lock):
    """
    Thread_work handles all of the work each thread must continually
    perform whilst in a never ending loop
    @param coin: The stock/coin to be monitored
    """
    global LOSS
    global PROFIT
    global PROFIT_MINUS_LOSS
    purchase = 0
    profitloss = 0
    trans_count = 0
    purchase_qty = 0
    purchase_total = 0
    sell = 0
    split_market = coin.split('-')
    split_market = split_market[-1]
    split_market_dict = {'Coin':split_market}
    while True:
        last_price, stdupper,\
        stdlower, time_stamp, bid_price, ask_price = get_data(coin)
        balance_return = http_request('Balance', split_market_dict, 'Get')
        result_return = balance_return['result']
        current_balance = result_return['Balance']
        print(balance_return)
        # If the current price has fallen below our threshold, it's time to buy
        if bid_price[-1] < (0.999*stdlower) and current_balance == 0 and \
                        stdupper >= (ask_price[-1] * 1.0025):
            purchase = bid_price[-1]
            purchase_qty = ((BTC_PER_PURCHASE + profitloss) / bid_price[-1])
            purchase_qty = round(purchase_qty,8)
            purchase_total = purchase_qty * bid_price[-1]
            purchase_dict = {'Coin': coin, 'OrderType':'LIMIT',\
                    'Quantity': purchase_qty, 'Rate':bid_price[-1],\
                    'TimeInEffect':'IMMEDIATE_OR_CANCEL', \
                    'ConditionType': 'NONE', 'Target': 0}

            http_request("buy", purchase_dict, 'Post')

        elif ask_price[-1] >= (1.004 * purchase) and current_balance != 0:
             sell = purchase_qty * ask_price[-1]
             profitloss += (sell - (1.0025 * purchase_total))
             lock.acquire()
             PROFIT += (sell - (1.0025 * purchase_total))
             PROFIT_MINUS_LOSS += (sell - (1.0025 * purchase_total))
             lock.release()
             trans_count += 1
             purchase = 0
             purchase_qty = 0
             purchase_total = 0

        elif bid_price[-1] <= (purchase * 0.996) and current_balance != 0:
             sell = purchase_qty * bid_price[-1]
             lock.acquire()
             profitloss += (sell - (1.0025 * purchase_total))
             LOSS += (sell - (1.0025 * purchase_total))
             PROFIT_MINUS_LOSS += (sell - (1.0025 * purchase_total))
             lock.release()
             trans_count += 1
             purchase = 0
             purchase_qty = 0
             purchase_total = 0

        hunter_dict = {'Coin': coin, 'Bid':bid_price[-1], 'Ask':ask_price[-1], 'Last':last_price[-1], 'Upper':stdupper,\
         'Lower':stdlower, 'Time':time_stamp, 'Transactions':trans_count,\
         'Balance':profitloss, 'Profit':PROFIT, 'Loss':LOSS, 'Net':PROFIT_MINUS_LOSS}
        token = os.environ['SPLUNKTOKEN']
        print(hunter_dict)
        send_event("splunk", token, hunter_dict)
        time.sleep(1)


if __name__ == "__main__":
    print("Waiting for correct amount of data")
    #time_for_data = COLLECTION_MINUTES * 60
    time.sleep(15)
    #time.sleep(time_for_data)
    COINS = get_coins() # Get all of the coins from the WEB-API
    # Add 15 min wait here for profit testing phase
    THREADS = []

    for c in range(0, len(COINS)):
        t = MyThread(COINS[c])
        t.setDaemon(True)
        THREADS.append(t)
    for i in range(0, len(COINS)):
        THREADS[i].start()
        time.sleep(2)
    while threading.active_count() > 0:
        time.sleep(30)
