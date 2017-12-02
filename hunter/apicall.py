import requests
import json
import sys
import time

class ApiCall:
    def http_request(self, ptype, python_dict, method):
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
                try:
                    x = r.json()
                    return x
                except ValueError:  # includes simplejson.decoder.JSONDecodeError
                    x = r.text #return the value in text if there was a JSON decode error
                    return x
        except requests.exceptions.RequestException as error:
            print(error)
            sys.exit(1)

    def get_markets(self):
         """
         This is the first function that is called as the hunter runs,
         this function makes a call to the WEB-API to determine which stocks
         are going to be hunted
         @return data: Returns a list of markets returned from the WEB-API
         """
         try:
             endpoint_url = 'http://web-api:3000/api/markets'
             resp = requests.get(url=endpoint_url)
             data = json.loads(resp.text)
             data = data[0]["markets"]
             if data is None:
                 print("No Markets selected in API, Hunter quiting")
                 sys.exit(1)
             else:
                 return data
         except requests.exceptions.RequestException as error:
             print(error)
             sys.exit(1)

    def get_last_ticker_data(self, market, period, interval):
        """
        This function is needed to return all of the data, not just the closing price
        back to the hunter.
        """
        closing_price = []
        try:
            query = '?interval={0}'.format(interval)
            endpoint_url = 'http://web-api:3000/api/historical/{0}/{1}'.format(market, query)
            resp = requests.get(url=endpoint_url)
            historical_data = json.loads(resp.text)
            while historical_data is None or isinstance(historical_data, dict) == False:
                endpoint_url = 'http://web-api:3000/api/historical/{0}/{1}'.format(market, query)
                resp = requests.get(url=endpoint_url)
                historical_data = json.loads(resp.text)
                time.sleep(2)
            for data in historical_data['result']:
                closing_price.append(data) # append the entire dict
            #closing_price = closing_price[(len(closing_price)-(period + 1)) : -1] # PERIOD + 1 to seed EMA
            return closing_price
        except Exception as err:
            print ("Error sending request")
            print (str(err))

    def get_historical(self, market, period, interval):
        """
        This function calcualtes our moving exponential averages that are used
        to determine our buy and sell signals.
        @param period: The period of time for which the mea will be calculated over
        @param interval: The desired tick interval
        """
        #getting the historical tick closing prices
        closing_price = []
        try:
            query = '?interval={0}'.format(interval)
            endpoint_url = 'http://web-api:3000/api/historical/{0}/{1}'.format(market, query)
            resp = requests.get(url=endpoint_url)
            historical_data = json.loads(resp.text)
            while historical_data is None or isinstance(historical_data, dict) == False:
                endpoint_url = 'http://web-api:3000/api/historical/{0}/{1}'.format(market, query)
                resp = requests.get(url=endpoint_url)
                historical_data = json.loads(resp.text)
                time.sleep(2)
            for data in historical_data['result']:
                closing_price.append(data['C'])
            #closing_price = closing_price[(len(closing_price)-(period + 1)) : -1] # PERIOD + 1 to seed EMA
            return closing_price
        except Exception as err:
            print ("Error sending request")
            print (str(err))
