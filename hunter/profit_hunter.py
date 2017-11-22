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

BTC_PER_PURCHASE = 0.00100000

# For talking with Splunk Container
ssl._create_default_https_context = ssl._create_unverified_context



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

    def run(self):
        """
        Custom Override of the Thread Librarys run function to start the
        thread work function
        """
        thread_work(self.market)


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



def thread_work(market):
    """
    Thread work now needs to check the two current moving exponential values
    to determine if an overlap greater than our set threshold has occured.
    In the instance that the overlap occurs the appropriate action will be taken
    """
    #make an instance of the bittrex class which takes market as a constructor arg
    bittrex = Bittrex(market)


    #print("Pandas MEA")
    #mea = bittrex.mea_pandas(10, 'hour')
    time.sleep(10)
    #mea2 = bittrex.mea_pandas(20, 'hour')
    #print("ema 10  ", market, " ", mea )
    #print("ema 20  ", market, " ", mea2 )

    #"oneMin", "fiveMin", "thirtyMin", "hour" and "day"
    #print("My MEA")
    mea = bittrex.calculate_mea(10, 'fiveMin')
    time.sleep(10)
    mea2 = bittrex.calculate_mea(21, 'fiveMin')
    print("ema 10  ", market, " ", mea )
    print("ema 21  ", market, " ", mea2 )
    downtrend_gap = False
    current_purchase = 99999999999
    balance = bittrex.get_balance()
    current_state = ""
    if mea > mea2:
        current_state = "InitTrendingUp"
    else:
        current_state = "TrendingDown"

    while True:
        #test the historical data is getting called properly, interval, hour
        #mea = bittrex.mea_pandas(10, 'hour')
        #mea2 = bittrex.mea_pandas(20, 'hour')
        mea = bittrex.calculate_mea(10, 'fiveMin')
        time.sleep(10)
        mea2 = bittrex.calculate_mea(21, 'fiveMin')
        balance = bittrex.get_balance()
        latest_summary = bittrex.get_latest_summary()
        last_closing_price = bittrex.last_closing(1, 'fiveMin')
        #if the smaller period mea has risen 1.5% above the larger period mea then buy
        if balance is not None:
            """
            Buying Logic

            """
            #if the inital state is trending up over time the price dips then we have to
            #re adjust the ciurrnet state so that the hunter will buy
            if current_state == "InitTrendingUp" and mea < (1 * mea2):
                current_state = "TrendingDown"
            if mea > (1.001 * mea2) and current_state != "InitTrendingUp" and balance == 0 and mea2 < (1.001 * mea):
                """
                While we are in between these thresholds we only want to buy at a reasonable ask price
                """
                ask = latest_summary['Ask']
                if ask <= 1.001*mea:
                    #ask = mea2
                    qty = BTC_PER_PURCHASE / ask
                    current_state = bittrex.place_buy_order(qty, ask)
                    if current_state == "TrendingUp":
                        current_purchase = ask #this the price that the bot bought at
                #if the smaller period mea has fallen 1.5% below the larger period mea then sell

            """
            - There has to be some logic that says while we are in a down trend, look for the moment we start to reverse
            the reversal might not end up in an uptrend but it should reverse up enough to make our static profit margin
            - When the down trend is occuring the 10mea should keep progressively moving further apart from the 21mea
            - If we rechonise that during the down trend there was quite a large gap in price between the two bands, say 0.002  (2 percent)
            We then say well we know there has been a decent dip so when the 10 band is 1 percent away from the 21 band then its clear the price is coming back up
            and we should get in early
            """
            if current_state == "TrendingDown":
                #check to see if our bands are 2 percent apart
                if mea2 >= mea*1.002: #if our 21band is greater than our 10 band plus 2 percent, then yes there is a gap
                    downtrend_gap = True #set our flag
            #now we have a down trend gap identifier we should look to see when the gap between our bands is closing up
            if downtrend_gap == True and mea2 <= mea*1.0015: #if our lower band plus 1.5 percent is above or equal to our upperband then we are back on the rise, jump on early
                #we want to make a purchase here so we should check our balance
                if balance == 0:
                    ask = mea2 #try and buy at the lower bands price
                    qty = BTC_PER_PURCHASE / ask
                    current_state = bittrex.place_buy_order(qty, ask) #return the state depending on if our order is filled or not
                    if current_state == "TrendingUp":#if we know our order was filled ... set our current purchase price
                        current_purchase = ask #this the price that the bot bought at
                        downtrend_gap = False#we know our order was filled so now we should reset our downtrend variable

            """
            PANIC SELL PURCHASES
            - When the price is falling we want to catch panic sellers, lets look for oppourtunities at very low prices
            """
            if current_state == "TrendingDown":
                latest_summary = bittrex.get_latest_summary() #getting the latest summary
                #if there is a 2.25 percent gap in mea lines and the price is further 0.5 percent lower than hunter should go ahead and purchase
                if mea2 >= 1.0225*mea and latest_summary['Ask'] <= (mea - (0.01*mea)) and balance == 0:
                    ask = latest_summary['Ask'] #pick up price
                    qty = BTC_PER_PURCHASE / ask
                    current_state = bittrex.place_buy_order(qty, ask) #return the state depending on if our order is filled or not
                    if current_state == "TrendingUp":#if we know our order was filled ... set our current purchase price
                        current_purchase = ask #this the price that the bot bought at
                        current_state = "PanicSellPurchase" #update to notify hunter that we have purchased a panic sell
            """
            Selling logic
            """
            #while we are making gainz, if the price rises past 0.07 percent gain lets bail
            if current_state == "TrendingUp":
                if (latest_summary['Last'] >= (current_purchase * 1.007)):
                    bid = latest_summary['Last']
                    qty = balance
                    bittrex.place_sell_order(bid)
                    current_state = "InitTrendingUp"#because we sold off at a static value, price needs to fall below MEA's before we purchase again
                    #inittrendingup will prevent the bot from purchasing

            if current_state == "PanicSellPurchase":
                if (latest_summary['Last'] <= (current_purchase * 1.014)): #lets try and sell our panicbuys for double
                    bid = latest_summary['Last']
                    qty = balance
                    bittrex.place_sell_order(bid)
                    if mea > mea2:
                        current_state = "InitTrendingUp"#because we sold off at a static value, price needs to fall below MEA's before we purchase again
                        #inittrendingup will prevent the bot from purchasing
                    else:
                        current_state = "TrendingDown"
            """
            This is our stop loss logic
            """
            if current_state == "TrendingUp" or current_state == "PanicSellPurchase":
                if (latest_summary['Last'] <= current_purchase * 0.95): #If somethings gone horrible wrong and we are down 5 percent on a purchase then we need to bail
                    bid = latest_summary['Last']
                    qty = balance
                    bittrex.place_sell_order(bid)
                    if mea > mea2:
                        current_state = "InitTrendingUp"#if our 10 mea is above the 21 then set the right state
                    else:
                        current_state = "StoppedLoss"# as long as state is not InitTrendingUp hunter will buy again at the right time
        print("Last Price: ",latest_summary['Last'])
        print("Current Purchase: ", current_purchase)
        print("ema 10  ", market, " ", mea )
        print("ema 21  ", market, " ", mea2 )
        print("Current state:", current_state, "\n" )
        time.sleep(30)


if __name__ == "__main__":
    print("Waiting for correct amount of data")
    time.sleep(3)
    #time.sleep(time_for_data)
    apicall = ApiCall() #instance of the ApiCall class
    markets = apicall.get_markets() # Get all of the markets from the WEB-API
    # Add 15 min wait here for profit testing phase
    THREADS = []

    for c in range(0, len(markets)):
        t = MyThread(markets[c])
        t.setDaemon(True)
        THREADS.append(t)
    for i in range(0, len(markets)):
        THREADS[i].start()
        time.sleep(10)
    while threading.active_count() > 0:
        time.sleep(1000)
