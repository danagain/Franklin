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

BTC_PER_PURCHASE = 0.00150000
CURRENT_HOUR = 0
CURRENT_MIN = 0
# For talking with Splunk Container
ssl._create_default_https_context = ssl._create_unverified_context



class MyThread(threading.Thread):
    """
    Class to handle all of the threading aspect
    """
    def __init__(self, market, num):
        """
        Class constructor for initialisation
        @param market: The market/stock this thread is
        responsible for monitoring
        """
        threading.Thread.__init__(self)
        self.market = market
        self.num = num

    def run(self):
        """
        Custom Override of the Thread Librarys run function to start the
        thread work function
        """
        thread_work(self.market, self.num)

def track_btc_balance(bittrex):
    balance = bittrex.get_btc_balance()
    return balance

def update_clock_globals(bittrex):
    latest_summary = bittrex.get_latest_summary()
    day_and_time_str = latest_summary['TimeStamp'].split("T")
    hour_min_sec = day_and_time_str[1].split(":")
    global CURRENT_HOUR
    global CURRENT_MIN
    CURRENT_HOUR = hour_min_sec[0]
    CURRENT_MIN = hour_min_sec[1]


def thread_work(market, num):
    """
    Initialise all components
    """
    global CURRENT_HOUR #global so threads can read the time
    global CURRENT_MIN# ^^
    #time.sleep(num)# incremental sleep timer to stop every thread calling api at once
    bittrex = Bittrex(market)#init bittrex class
    apicall = ApiCall()#init api class
    latest_summary = bittrex.get_latest_summary()#get the latest market summary
    new_hour = True#init the new hour as True
    new_min = True
    update_clock_globals(bittrex)#init the hunter_time_hour to current hour
    hunter_time_hour = CURRENT_HOUR
    hunter_time_min = CURRENT_MIN
    current_purchase_price_hourly = 999999 #assign an initial value to the current purchase price
    current_purchase_price_min = 999999 #assign an initial value to the current purchase price
    current_state_min = "NoTrade"
    hour_purchase_qty = 0
    min_purchase_qty = 0
    #Init the EMA to detect current coin trend status
    ema = bittrex.calculate_ema(10, 'hour')#"oneMin", "fiveMin", "thirtyMin", "hour" and "day"
    ema2 = bittrex.calculate_ema(21, 'hour')
    if ema > ema2 * 1.0025:
        current_state = "TrendingUp" #if the 10 ema is initially above the 21 EMA then coins trending up
    else:
        current_state = "TrendingDown"#else its down
    print("Current state for ", market, " is: ", current_state)
    time.sleep(10)
    while True: #hunt forever $$
        #variables that need to update every loop
        time.sleep(2.5)

        #Restrict time management to only the eth thread
        if market == "BTC-ADA":
            update_clock_globals(bittrex)
            time.sleep(0.2)
        if hunter_time_hour != CURRENT_HOUR: #if the times changed...
            hunter_time_hour = CURRENT_HOUR #take the new time
            new_hour = True#let hunter know its a new hour
        if hunter_time_min != CURRENT_MIN:
            hunter_time_min = CURRENT_MIN
            print("New min,", CURRENT_MIN, " for ", market)
            new_min = True
        #perform minuite tasks
        if new_min == True:
            latest_summary = bittrex.get_latest_summary()#get the latest market summary
            """
            Minuite tasks involve calculating the RSI for the given coins and deciding if the coin is over or under bought
            """
            RSI = bittrex.calculate_rsi(14, 'oneMin')
            print("Calculated RSI value for market", market, " : ", RSI)
            """
            Rule #1
            When coin is in a downtrend identified via the 1hr 21,10 ema lines. Hunter should be more careful and aim
            for smaller profits. (stock is unlikely to be overbought whilst trending down) using this logic
            hunter will purchase stock when it is over sold, but sell stock when in profit margin with RSI > 50

            Stock can be identified as over sold if the RSI is less than or equal to 20 - We can tweak this (20 is very overbought and on the safe side !)
            """
            #Buying time !
            if RSI <= 22 and current_state_min != "InTrade": #if stock is over bought !
                #btc_balance = track_btc_balance(bittrex) #check btc balance
                #balance = bittrex.get_balance()#check coin balance
                ask = latest_summary['Ask'] #guarentee the purchase !
                min_purchase_qty = BTC_PER_PURCHASE / ask #set the qty
                current_state_min = bittrex.place_buy_order(min_purchase_qty, ask)
                if current_state_min == "InTrade":
                    current_purchase_price_min = ask

            #Sell for smaller profit margin when down trending (Smaller RSI)
            if RSI >= 50 and current_state_min == "InTrade" and latest_summary['Bid'] >= current_purchase_price_min * 1.015 and current_state == "TrendingDown":
                bid = latest_summary['Bid']
                bittrex.place_sell_order(bid, min_purchase_qty)

            #Sell for larger profit margin when up trending (larger RSI)
            if RSI >= 78 and current_state_min == "InTrade" and latest_summary['Bid'] >= current_purchase_price_min * 1.015 and current_state == "TrendingUp":
                bid = latest_summary['Bid']
                bittrex.place_sell_order(bid, min_purchase_qty)
            #Stop loss for minuite trading
            if current_state_min == "InTrade" and latest_summary['Bid'] <= (current_purchase_price_min * 0.9):
                bid = latest_summary['Bid']
                bittrex.place_sell_order(bid, min_purchase_qty)
            """
            Rule #2 TO-DO
            During an uptrend there will be stages when the stock is over bought ,
            the hunter should sell the shares then buy back when RSI <= 60 (assuming up trend still going)

            """
            new_min = False
        #Perform hourly task
        if new_hour == True:
            latest_summary = bittrex.get_latest_summary()#get the latest market summary
            """
            Hourly task involves calculating the EMA values, checking if they have changed from trending down
            to trending up
            """
            ema = bittrex.calculate_ema(10, 'hour')#"oneMin", "fiveMin", "thirtyMin", "hour" and "day"
            ema2 = bittrex.calculate_ema(21, 'hour')
            print("ema 10  ", market, " ", ema )
            print("ema 21  ", market, " ", ema2 )
            #check the EMA values and compare against the current_state in memory
            if current_state == "TrendingUp" and (ema * 1.0025) < ema2: # ema must be 0.0025 percent less than ema2 (0.0025 threshold)
                current_state = "TrendingDown"
            elif current_state == "TrendingDown" and ema > (ema2 * 1.0025):
                current_state = "HourlyBuyZone"
            new_hour = False#turn off the new hour until hunter realises that the hour has changed

        #Now in the main loop we should look out for if we are in an hourly buy zone and continually check if
        #there is a decent buy in position
        if current_state == "HourlyBuyZone":
            btc_balance = track_btc_balance(bittrex) #check btc balance
            balance = bittrex.get_balance()#check coin balance
            ask = latest_summary['Ask']
            if ask < ema * 1.01: #if we are looking to buy, and the asking price is 1 percent away from our ema line
                    for i in range(10):
                        print("\n###############\n")
                        print("Buy Signal for: ", market)
                        print("\n###############\n")
                    hour_purchase_qty = BTC_PER_PURCHASE / ask #Get purchase qty
                    if btc_balance > hour_purchase_qty * ask: #Check we have enough bitcoin
                        current_state = bittrex.place_buy_order(hour_purchase_qty, ask)
                        if current_state == "InTrade": #if we know the bot bought
                            current_state = "InHourlyTrade" #identify the type of trade
                            current_purchase_price_hourly = ask #price that the bot bought at

        #if the hunters currently in an hourly trade using the EMA lines then check if they have crossed back into down trend
        if current_state == "InHourlyTrade" and ema * 1.0025 < ema2:
                bid = latest_summary['Bid']
                bittrex.place_sell_order(bid, hour_purchase_qty)
                current_state = "TrendingDown"
        #if we are down 10 percent on a trade than just ditch it
        if current_state == "InHourlyTrade" and current_purchase_price_hourly < latest_summary['Bid'] * 0.90:
                bid = latest_summary['Bid']
                bittrex.place_sell_order(bid, hour_purchase_qty)
                current_state = "TrendingDown"






if __name__ == "__main__":
    print("Waiting for correct amount of data")
    time.sleep(3)
    apicall = ApiCall() #instance of the ApiCall class
    markets = apicall.get_markets() # Get all of the markets from the WEB-API
    THREADS = []
    #for c in range(0, len(markets)):
    for c in range(0, 3): #temp to start just one thread
        t = MyThread(markets[c], c)
        t.setDaemon(True)
        THREADS.append(t)
    #for i in range(0, len(markets)):
    for i in range(0, 3):
        THREADS[i].start()
        time.sleep(0.1)
    while threading.active_count() > 0:
        time.sleep(1000)
