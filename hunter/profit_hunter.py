"""Fill this in later"""
import os
import threading
import time
import json
import sys
import requests
from pymongo import MongoClient
import numpy as np
import datetime

TIME_STAMP = 0
QUARTHOUR = 15 * 4 # Constant representing the data points per hour (15s intervals)

LAST_PRICE_BTC = 0
UPPER_BOUND_BTC = 0
LOWER_BOUND_BTC = 0

LAST_PRICE_LTC = 0
UPPER_BOUND_LTC = 0
LOWER_BOUND_LTC = 0

LAST_PRICE_NEO = 0
UPPER_BOUND_NEO = 0
LOWER_BOUND_NEO= 0

LAST_PRICE_ETH = 0
UPPER_BOUND_ETH = 0
LOWER_BOUND_ETH = 0



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

def update_globals(coin, last, upper, lower, timestamp):
    """Fill this in later"""
    if coin == "BTC-ETH":
        global LAST_PRICE_ETH
        LAST_PRICE_ETH = last
        global UPPER_BOUND_ETH
        UPPER_BOUND_ETH = upper
        global LOWER_BOUND_ETH
        LOWER_BOUND_ETH = lower
        global TIME_STAMP
        TIME_STAMP = timestamp
        TIME_STAMP = TIME_STAMP.strftime("%s")
    if coin == "USDT-BTC":
        global LAST_PRICE_BTC
        LAST_PRICE_BTC = last
        global UPPER_BOUND_BTC
        UPPER_BOUND_BTC = upper
        global LOWER_BOUND_BTC
        LOWER_BOUND_BTC = lower
    if coin == "BTC-LTC":
        global LAST_PRICE_LTC
        LAST_PRICE_LTC = last
        global UPPER_BOUND_LTC
        UPPER_BOUND_LTC = upper
        global LOWER_BOUND_LTC
        LOWER_BOUND_LTC = lower
    if coin == "BTC-NEO":
        global LAST_PRICE_NEO
        LAST_PRICE_NEO = last
        global UPPER_BOUND_NEO
        UPPER_BOUND_NEO = upper
        global LOWER_BOUND_NEO
        LOWER_BOUND_NEO = lower

def generate_statlists(datasource, quart_hour, coin):
    """Fill this in later"""
    last_price = []
    datetime_data = []
    while datasource.count() < (15*6):
        print("Waiting for 15 mins of data .. going to sleep for 30 seconds")
        time.sleep(30)
    for doc in datasource.find():  # Iterate stored documents
        last_price.append(doc['Last'])  # Store the entire collections last values in memory
        datetime_data.append(doc['_id'].generation_time) # gotta find way to just get last collection from mongo
    #print(datetime_data)
    avgrecentprice = np.mean(last_price[len(last_price) - quart_hour : -1])
    recentstd = np.std(last_price[len(last_price) - (quart_hour):-1])
    recentstdupper = avgrecentprice + 2*(recentstd/2)
    recentstdlower = avgrecentprice - 2*(recentstd/2)
    update_globals(coin, last_price[-1], recentstdupper, recentstdlower, datetime_data[-1])
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
        stdlower = generate_statlists(datasource, QUARTHOUR, coin)

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
    print("Wait 20 seconds for Mongo to fire up")
    time.sleep(20)
    while threading.active_count() > 0:
        '''
        Here we create a function to either call API or insert values into MONGO
        '''
        hunter_dict = [{"currency":COINS[0], "Last":LAST_PRICE_ETH,"Upper":UPPER_BOUND_ETH, \
        "Lower":LOWER_BOUND_ETH, "time":TIME_STAMP},{"currency":COINS[1], "Last":LAST_PRICE_BTC, \
        "Upper":UPPER_BOUND_BTC, "Lower":LOWER_BOUND_BTC, "time":TIME_STAMP},{ \
        "currency":COINS[2], "Last":LAST_PRICE_LTC, "Upper":UPPER_BOUND_LTC, "Lower":LOWER_BOUND_LTC \
        , "time":TIME_STAMP},{"currency":COINS[3], "Last":LAST_PRICE_NEO, "Upper":UPPER_BOUND_NEO, "Lower":LOWER_BOUND_NEO, "time":TIME_STAMP}]
        for i in range(4):
            http_request(hunter_dict[i],"hunterdata")

        print(LAST_PRICE_NEO)
        print(LAST_PRICE_BTC)
        print(LAST_PRICE_LTC)
        print(LAST_PRICE_ETH)
        print(TIME_STAMP)
        time.sleep(10)
