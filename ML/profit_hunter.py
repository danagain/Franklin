import threading
import time
import process_data
import database_setup
import os
import buy_sell

QUARTHOUR = 15 * 4 # Constant representing the data points per hour (15s intervals)

class mythread(threading.Thread):
    def __init__(self, coin, endpoint):
        threading.Thread.__init__(self)
        self.coin = coin
        self.endpoint = endpoint
    def run(self):
        thread_work(self.coin, self.endpoint)


def thread_work(coin, endpoint):
    make_purchase = 0
    profitLoss = 0
    transactionCount = 0
    print("Mongo Endpoint is {0}".format(endpoint))
    while True:
        datasource = database_setup.form_db_connection(coin, endpoint)
        last_price, xaxis, meanlast, stdhour, stdupper, stdlower, recentavgprice, recentstd, \
        recentstdupper, recentstdlower = process_data.generate_statlists(datasource, QUARTHOUR)
        print('Last recorded price', last_price[-1])
        print('Last recorded 15min lower bound ', recentstdlower)
        print('Last recorded 15min Upper bound ', recentstdupper)

        # If the current price has fallen below our threshold, it's time to buy
        if last_price[-1] < recentstdlower and make_purchase == 0:
            print("Making a purchase")
            make_purchase = last_price[-1]

            purchase_dict = {'currency': coin, 'OrderType':'LIMIT', 'Quantity': 1.00000000, 'Rate':last_price[-1], 'TimeInEffect':'IMMEDIATE_OR_CANCEL'
                             ,'ConditionType':'NONE','Target':0}
            buy_sell.purchase(purchase_dict,"buy")



        elif last_price[-1] >= recentstdupper and make_purchase != 0 \
                and last_price[-1] > (make_purchase * 0.0025): #bittrex trade fee = 0.0025
            print("Making a sell")
            profitLoss += (recentstdupper - (1.0025*make_purchase))
            transactionCount += 1
            make_purchase = 0
        elif last_price[-1] <= make_purchase * 0.9 and make_purchase != 0:
            print("Making a sell")
            transactionCount += 1
            profitLoss += (last_price[-1] - (1.0025*make_purchase))
            make_purchase = 0
        print('Current Purchase ', make_purchase)
        if make_purchase != 0:
            print('Current Sell Goal', recentstdupper)
        else:
            print('Current Sell Goal', 0)
        print("Profit / Loss ", profitLoss)
        print("Transaction Count ", transactionCount)
        print("\n\n")
        time.sleep(10)


if __name__ == "__main__":
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



