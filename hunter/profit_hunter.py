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
from pymongo import MongoClient
import numpy as np
import datetime

QUARTHOUR = 15 * 6 # Constant representing the data points per hour

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
        self.endpoint = ENDPOINT

    def run(self):
        """

        Custom Override of the Thread Librarys run function to start the
        thread work function

        """
        thread_work(self.coin)


def form_db_connection(coin):
    """

    Function to form a connection with the database,
    will eventually be replaced with API call to WEB-API

    @param coin: The coin/stock we want to query

    """
    client = MongoClient(ENDPOINT)
    data_base = client.franklin
    data_source = data_base['{0}'.format(coin)]
    return data_source


def generate_statlists(datasource, quart_hour):
    """

    Generates the upper and lower threshold values to spot buy/sell signals

    @param datasource: The mongodb database source
    @param quart_hour: Time frame to determine the amount of data we are
    working with

    @return last_price: Array of Last values for the currency
    @return recentstdupper: The most recent upper threshhold value
    @return recentstdlower: The most recent lower threshhold value
    @return datetime_data[-1]: The TimeStamp of most recent Last price

    """
    last_price = []
    datetime_data = []
    while datasource.count() < (QUARTHOUR):
        print("Waiting for 15 mins of data .. going to sleep for 30 seconds")
        time.sleep(30)
    for doc in datasource.find():  # Iterate stored documents
        last_price.append(doc['Last'])
        datetime_data.append(doc['_id'].generation_time)
    avgrecentprice = np.mean(last_price[len(last_price) - quart_hour : -1])
    recentstd = np.std(last_price[len(last_price) - (quart_hour):-1])
    recentstdupper = avgrecentprice + 2*(recentstd/2)
    recentstdlower = avgrecentprice - 2*(recentstd/2)
    datedata = datetime_data[-1]
    datedata = datedata.strftime("%s")+"000"

    return last_price, recentstdupper, recentstdlower,\
    datedata


def http_request(ptype, python_dict):
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
        requests.post(endpoint_url, data=jsondata, headers=headers)
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

def thread_work(coin):
    """

    Thread_work handles all of the work each thread must continually
    perform whilst in a never ending loop

    @param coin: The stock/coin to be monitored

    """
    purchase = 0
    profitloss = 0
    trans_count = 0
    sell = 0
    print("Mongo Endpoint is {0}".format(ENDPOINT))
    while True:
        datasource = form_db_connection(coin)
        last_price, stdupper,\
        stdlower, time_stamp = generate_statlists(datasource, QUARTHOUR)
        # If the current price has fallen below our threshold, it's time to buy
        if last_price[-1] < stdlower and purchase == 0 and \
                        stdupper >= (last_price[-1] * 1.0025):
            purchase = last_price[-1]
            purchase_dict = {'Coin': coin, 'OrderType':'LIMIT',\
                    'Quantity': 1.00000000, 'Rate':last_price[-1],\
                    'TimeInEffect':'IMMEDIATE_OR_CANCEL', \
                    'ConditionType': 'NONE', 'Target': 0}

            http_request("buy", purchase_dict)

        elif last_price[-1] >= (1.003 * purchase) and purchase != 0:
            sell = last_price[-1]
            profitloss += (sell - (1.0025 * purchase))
            trans_count += 1
            purchase = 0

        elif last_price[-1] <= (purchase * 0.996) and purchase != 0:
            sell = last_price[-1]
            trans_count += 1
            profitloss += (sell - (1.0025*purchase))
            purchase = 0

        hunter_dict = {'Coin': coin, 'Last':last_price[-1], 'Upper':stdupper,\
         'Lower':stdlower, 'Time':time_stamp, 'Transactions':trans_count,\
         'Balance':profitloss, 'Current Buy':purchase}
        http_request("graph", hunter_dict)
        time.sleep(10)


if __name__ == "__main__":
    print("Wait 10 seconds for Mongo to fire up")
    time.sleep(10)
    COINS = get_coins() # Get all of the coins from the WEB-API
    # Add 15 min wait here for profit testing phase
    THREADS = []
    ENDPOINT = os.environ['MONGO']

    for c in range(0, len(COINS)):
        t = MyThread(COINS[c])
        t.setDaemon(True)
        THREADS.append(t)
    for i in range(0, len(COINS)):
        THREADS[i].start()
    while threading.active_count() > 0:
        time.sleep(9)
