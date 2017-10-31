import threading
import time
import process_data
import database_setup
import os

QUARTHOUR = 15 * 4 # Constant representing the data points per hour (15s intervals)

class mythread(threading.Thread):
    def __init__(self, coin, endpoint):
        threading.Thread.__init__(self)
        self.coin = coin
        self.endpoint = endpoint
    def run(self):
        thread_work(self.coin, self.endpoint)


def thread_work(coin, endpoint):
    testBuy = 0
    profitLoss = 0
    transactionCount = 0
    print("Mongo Endpoint is {0}".format(endpoint))
    while True:
        datasource = database_setup.form_db_connection(coin, endpoint)
        lastprice, xaxis, meanlast, stdhour, stdupper, stdlower, recentavgprice, recentstd, \
        recentstdupper, recentstdlower = process_data.generate_statlists(datasource, QUARTHOUR)
        print('Last recorded price', lastprice[-1])
        print('Last recorded 15min lower bound ', recentstdlower)
        print('Last recorded 15min Upper bound ', recentstdupper)
        if lastprice[-1] < recentstdlower and testBuy == 0:
            print("Making a purchase")
            testBuy = lastprice[-1]
        elif lastprice[-1] >= recentstdupper and testBuy != 0 \
                and lastprice[-1] > (testBuy * 0.0025): #bittrex trade fee = 0.0025
            print("Making a sell")
            profitLoss += (recentstdupper - (1.0025*testBuy))
            transactionCount += 1
            testBuy = 0
        elif lastprice[-1] <= testBuy * 0.9 and testBuy != 0:
            print("Making a sell")
            transactionCount += 1
            profitLoss += (lastprice[-1] - (1.0025*testBuy))
            testBuy = 0
        print('Current Purchase ', testBuy)
        if testBuy != 0:
            print('Current Sell Goal', recentstdupper)
        else:
            print('Current Sell Goal', 0)
        print("Profit / Loss ", profitLoss)
        print("Transaction Count ", transactionCount)
        print("\n\n")
        time.sleep(10)


if __name__ == "__main__":
    threads = []
    coins = {0:"ethereum", 1:"bitcoin", 2:"ltc", 3:"neo"}
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



