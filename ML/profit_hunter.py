import threading
import time
import numpy as np
import time
from pymongo import MongoClient
import requests
import json


QUARTHOUR = 15 * 4 # Constant representing the data points per hour (15s intervals)

class mythread(threading.Thread):
    def __init__(self, coin, endpoint):
        threading.Thread.__init__(self)
        self.coin = coin
        self.endpoint = endpoint
    def run(self):
        thread_work(self.coin, self.endpoint)


def form_db_connection(coin, endpoint):
    client = MongoClient(endpoint)  # Connect to MongoDB Client WILL NOT WORK
    #client = MongoClient(port=27017) # But then this will work ?
    db = client.franklin  # Access the franklin database
    # This is not a very elegent solution but I don't know how to pass the db coin as a parameter
    if coin == "USDT-BTC":
        data_source = db.bitcoin
        return data_source
    if coin == "BTC-LTC":
        data_source = db.ltc
        return data_source
    if coin == "BTC-NEO":
        data_source = db.neo
        return data_source
    if coin == "BTC-ETH":
        data_source = db.ethereum
        return data_source

def generate_statlists(datasource, quart_hour):
    lastprice = []
    xaxis = []
    meanlast = []
    stdhour = []
    stdupper = []
    stdlower = []
    #print("Checking DB data count, then generating statistics ")
    #print(datasource.count())
    while datasource.count() < (15*6):
        print("Waiting for 15 mins of data .. going to sleep for 30 seconds")
        time.sleep(30)

    for doc in datasource.find():  # Iterate stored documents
        lastprice.append(doc['Last'])  # Store the entire collections last values in memory
        #print(lastprice)
    avgrecentprice = np.mean(lastprice[len(lastprice) - quart_hour : -1])
    recentstd = np.std(lastprice[len(lastprice) - (quart_hour):-1])
    recentstdupper = avgrecentprice + 2*(recentstd/2)
    recentstdlower = avgrecentprice - 2*(recentstd/2)
    return lastprice, xaxis, meanlast, stdhour, stdupper, stdlower, avgrecentprice, recentstd, recentstdupper, recentstdlower

def purchase(python_dict, type):
    try:
        buy_url = 'http://localhost:3000/api/{0}/{1}'.format(type, python_dict['currency'])
        jsondata = json.dumps(python_dict)
        requests.post(buy_url, json=jsondata)
    except:
        pass

def thread_work(coin, endpoint):
    purchase = 0
    profitLoss = 0
    transactionCount = 0
    print("Mongo Endpoint is {0}".format(endpoint))
    while True:
        datasource = form_db_connection(coin, endpoint)
        last_price, xaxis, meanlast, stdhour, stdupper, stdlower, recentavgprice, recentstd, \
        recentstdupper, recentstdlower = generate_statlists(datasource, QUARTHOUR)
        print('Last recorded price', last_price[-1])
        print('Last recorded 15min lower bound ', recentstdlower)
        print('Last recorded 15min Upper bound ', recentstdupper)

        # If the current price has fallen below our threshold, it's time to buy
        if last_price[-1] < recentstdlower and purchase == 0:
            print("Making a purchase")
            purchase = last_price[-1]

            purchase_dict = {'currency': coin, 'OrderType':'LIMIT', 'Quantity': 1.00000000, 'Rate':last_price[-1], 'TimeInEffect':'IMMEDIATE_OR_CANCEL'
                             ,'ConditionType':'NONE','Target':0}
            #purchase(purchase_dict,"buy")

        elif last_price[-1] >= recentstdupper and purchase != 0 and last_price[-1] > (purchase * 1.003): #bittrex trade fee = 0.0025
            sell = last_price[-1]
            print("Making a sell")
            profitLoss += (sell - (1.0025*purchase))
            transactionCount += 1
            client = MongoClient(endpoint)
            db = client.franklin
            posts = db.posts
            post_data = {
                'Coin': coin,
                'Buy Price': purchase,
                'Sell Price': recentstdupper,
                'Transaction Profit': (sell - (1.0025*purchase)),
                'Total Transaction Profit / Loss': profitLoss,
                'Transction': transactionCount
            }
            result = posts.insert_one(post_data)
            print('One post: {0}'.format(result.inserted_id))
            purchase = 0

        elif last_price[-1] <= (purchase * 0.7) and purchase != 0:
            sell = last_price[-1]
            print("Making a sell")
            transactionCount += 1
            profitLoss += (sell - (1.0025*purchase))
            client = MongoClient(endpoint)
            db = client.franklin
            posts = db.posts
            post_data = {
                'Coin': coin,
                'Buy Price': purchase,
                'Sell Price': last_price[-1],
                'Transaction Loss': (sell - (1.0025*purchase)),
                'Total Transaction Profit / Loss': profitLoss,
                'Transction': transactionCount
            }
            result = posts.insert_one(post_data)
            print('One post: {0}'.format(result.inserted_id))
            purchase = 0

        print('Current Purchase ', purchase)
        if purchase != 0:
            print('Current Sell Goal', recentstdupper)
        else:
            print('Current Sell Goal', 0)
        print("Profit / Loss ", profitLoss)
        print("Transaction Count ", transactionCount)
        print("\n\n")
        time.sleep(10)




if __name__ == "__main__":
    print("Sleeping for 20 seconds - waiting for data to be Mongo")
    time.sleep(20)
    threads = []
    coins = {0:"BTC-ETH", 1:"USDT-BTC", 2:"BTC-LTC", 3:"BTC-NEO"}
    '''
    if os.environ['APP_ENV'] == 'docker':
        print("Sleeping for 20 seconds - waiting for data to be Mongo")
        time.sleep(
            20)  # Since this is in docker lets just wait slightly here before connecting to Mongo, ensures everything is up and running
        endpoint = "mongodb://mongo:27017/franklin"
    else:
        endpoint = "mongodb://franklin:theSEGeswux8stat@ds241055.mlab.com:41055/franklin"
        '''
    endpoint = "mongodb://mongo:27017/franklin"
    for c in range(0,len(coins)):
        t = mythread(coins[c] , endpoint)
        t.setDaemon(True)
        threads.append(t)
    for i in range(0,len(coins)):
        threads[i].start()
    while threading.active_count() > 0:
        time.sleep(0.1)



