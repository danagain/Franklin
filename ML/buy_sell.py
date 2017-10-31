import requests
import json

def purchase(python_dict, type):
    try:
        buy_url = 'http://localhost:3000/api/{0}/{1}'.format(type, python_dict['currency'])
        jsondata = json.dumps(python_dict)
        requests.post(buy_url, json=jsondata)
    except:
        pass




