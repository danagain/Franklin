import requests
import json
import sys


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
            endpoint_url = 'http://localhost:3000/api/{0}/{1}'.format(ptype, python_dict['Coin'])
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
