"""Fill this in later"""
import os
import threading
import time
import json
import sys
import requests
from pymongo import MongoClient
import numpy as np


QUARTHOUR = 15 * 4 # Constant representing the data points per hour (15s intervals)


class MyThread(threading.Thread):
    """Fill this in later"""
    def __init__(self, coin):
        threading.Thread.__init__(self)
        self.coin = coin
        self.endpoint = ENDPOINT

    def run(self):
        thread_work(self.coin)


def form_db_connection(coin):
    """Fill this in later"""
    client = MongoClient(ENDPOINT)
    data_base = client.franklin
    data_source = data_base['{0}'.format(coin)]
    return data_source


def generate_statlists(datasource, quart_hour):
    """Fill this in later"""
    last_price = []
    while datasource.count() < (15*6):
        print("Waiting for 15 mins of data .. going to sleep for 30 seconds")
        time.sleep(30)
    for doc in datasource.find():  # Iterate stored documents
        last_price.append(doc['Last'])  # Store the entire collections last values in memory
    avgrecentprice = np.mean(last_price[len(last_price) - quart_hour : -1])
    recentstd = np.std(last_price[len(last_price) - (quart_hour):-1])
    recentstdupper = avgrecentprice + 2*(recentstd/2)
    recentstdlower = avgrecentprice - 2*(recentstd/2)
    return last_price, recentstdupper, recentstdlower


def http_request(python_dict, ptype):
    """Fill this in later"""
    try:
        endpoint_url = 'http://web-api:3000/api/{0}/{1}'.format(ptype, python_dict['currency'])
        jsondata = json.dumps(python_dict)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        requests.post(endpoint_url, data=jsondata, headers=headers)
    except requests.exceptions.RequestException as error:
        print(error)
        sys.exit(1)

def thread_work(coin):
    """Fill this in later"""
    purchase = 0
    profitloss = 0
    trans_count = 0
    print("Mongo Endpoint is {0}".format(ENDPOINT))
    while True:
        datasource = form_db_connection(coin)
        last_price, stdupper,\
        stdlower = generate_statlists(datasource, QUARTHOUR)

        timestamp = int(time.time())
        last_dict = {'currency': coin, 'timestamp': timestamp, 'last': last_price[-1]}
        http_request(last_dict, "last")
        print('Last recorded price', last_price[-1])
        print('Last recorded 15min lower bound ', stdlower)
        print('Last recorded 15min Upper bound ', stdupper)

        # If the current price has fallen below our threshold, it's time to buy
        if last_price[-1] < stdlower and purchase == 0 and \
                        stdupper >= (last_price[-1] * 1.003):
            print("Making a purchase")
            purchase = last_price[-1]
            purchase_dict = {'currency': coin, 'OrderType':'LIMIT',
                    'Quantity': 1.00000000, 'Rate':last_price[-1],\
                    'TimeInEffect':'IMMEDIATE_OR_CANCEL', \
                    'ConditionType': 'NONE', 'Target': 0}

            http_request(purchase_dict, "buy")

        elif last_price[-1] >= stdupper and purchase != 0 \
                and last_price[-1] > (purchase * 1.003):
            sell = last_price[-1]
            print("Making a sell")
            profitloss += (sell - (1.0025*purchase))
            trans_count += 1
            purchase = 0

        elif last_price[-1] <= (purchase * 0.85) and purchase != 0:
            sell = last_price[-1]
            print("Making a sell")
            trans_count += 1
            profitloss += (sell - (1.0025*purchase))
            purchase = 0

        print('Current Purchase ', purchase)
        if purchase != 0:
            print('Current Sell Goal', stdupper)
        else:
            print('Current Sell Goal', 0)
        print("Profit / Loss ", profitloss)
        print("Transaction Count ", trans_count)
        print("\n\n")
        time.sleep(10)


if __name__ == "__main__":
    THREADS = []
    COINS = {0: "BTC-ETH", 1: "USDT-BTC", 2: "BTC-LTC", 3: "BTC-NEO"}
    ENDPOINT = os.environ['MONGO']
    for c in range(0, len(COINS)):
        t = MyThread(COINS[c])
        t.setDaemon(True)
        THREADS.append(t)
    for i in range(0, len(COINS)):
        THREADS[i].start()
    while threading.active_count() > 0:
        time.sleep(0.1)
