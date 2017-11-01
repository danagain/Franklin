import json
import requests

python_dict = {'currency': "BTC", 'OrderType':'LIMIT', 'Quantity': float("1.00000000"), 'Rate':float("5.000"), 'TimeInEffect':'IMMEDIATE_OR_CANCEL'
                             ,'ConditionType':'NONE','Target':0}
jsondata = json.dumps(python_dict)
buy_url = 'http://localhost:3000/api/{0}/{1}'.format("buy", python_dict['currency'])
jsondata = json.dumps(python_dict)
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
print(jsondata)
requests.post(buy_url, headers=headers, data=jsondata)

