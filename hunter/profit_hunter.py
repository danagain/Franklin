"""Fill this in later"""
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
    data_base = client.franklin  # Access the franklin database
    # This is not a very elegent solution
    # but I don't know how to pass the data_base coin as a parameter
    if coin == "USDT-BTC":
        data_source = data_base.bitcoin
        return data_source
    if coin == "BTC-LTC":
        data_source = data_base.ltc
        return data_source
    if coin == "BTC-NEO":
        data_source = data_base.neo
        return data_source
    if coin == "BTC-ETH":
        data_source = data_base.ethereum
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


def make_purchase(python_dict, ptype):
    """Fill this in later"""
    try:
        buy_url = 'http://web-api:3000/api/{0}/{1}'.format(ptype, python_dict['currency'])
        jsondata = json.dumps(python_dict)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        requests.post(buy_url, data=jsondata, headers=headers)
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
            make_purchase(purchase_dict, "buy")

        elif last_price[-1] >= stdupper and purchase != 0 \
                and last_price[-1] > (purchase * 1.003):
            sell = last_price[-1]
            print("Making a sell")
            profitloss += (sell - (1.0025*purchase))
            trans_count += 1
            client = MongoClient(ENDPOINT)
            data_base = client.franklin
            posts = data_base.posts
            post_data = {
                'Coin': coin,
                'Buy Price': purchase,
                'Sell Price': stdupper,
                'Transaction Profit': (sell - (1.0025*purchase)),
                'Total Transaction Profit / Loss': profitloss,
                'Transction': trans_count
            }
            result = posts.insert_one(post_data)
            print('One post: {0}'.format(result.inserted_id))
            purchase = 0

        elif last_price[-1] <= (purchase * 0.85) and purchase != 0:
            sell = last_price[-1]
            print("Making a sell")
            trans_count += 1
            profitloss += (sell - (1.0025*purchase))
            client = MongoClient(ENDPOINT)
            data_base = client.franklin
            posts = data_base.posts
            post_data = {
                'Coin': coin,
                'Buy Price': purchase,
                'Sell Price': last_price[-1],
                'Transaction Loss': (sell - (1.0025*purchase)),
                'Total Transaction Profit / Loss': profitloss,
                'Transction': trans_count
            }
            result = posts.insert_one(post_data)
            print('One post: {0}'.format(result.inserted_id))
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
    print("Sleeping for 20 seconds - waiting for data to be Mongo")
    time.sleep(20)
    THREADS = []
    COINS = {0: "BTC-ETH", 1: "USDT-BTC", 2: "BTC-LTC", 3: "BTC-NEO"}
    '''
    if os.environ['APP_ENV'] == 'docker':
        print("Sleeping for 20 seconds - waiting for data to be Mongo")
        time.sleep(
            20)  # Since this is in docker lets just wait
            slightly here before connecting to Mongo,
            ensures everything is up and running
        endpoint = "mongodb://mongo:27017/franklin"
    else:
        endpoint = "mongodb://franklin:theSEGeswux8stat@ds241055.mlab.com:41055/franklin"
        '''
    ENDPOINT = "mongodb://mongo:27017/franklin"
    for c in range(0, len(COINS)):
        t = MyThread(COINS[c])
        t.setDaemon(True)
        THREADS.append(t)
    for i in range(0, len(COINS)):
        THREADS[i].start()
    while threading.active_count() > 0:
        time.sleep(0.1)
