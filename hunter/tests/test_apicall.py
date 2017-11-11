import requests
import json



def get_coins():
    """
    This is the first function that is called as the hunter runs,
    this function makes a call to the WEB-API to determine which stocks
    are going to be hunted
    @return data: Returns a list of coins returned from the WEB-API
    """
    try:
        endpoint_url = 'http://localhost:3000/api/coins'
        resp = requests.get(url=endpoint_url)
        data = json.loads(resp.text)
        data = data[0]["coins"]
        if data is None:
            print("No coins selected in API, Hunter quiting")
            sys.exit(1)
        else:
            return data
    except requests.exceptions.RequestException as error:
        print(error)
        sys.exit(1)


def http_request(ptype, python_dict, method):
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
            try:
                r = requests.get(endpoint_url)
                x = r.json()
                print(x)
                return x
            except ValueError:  # includes simplejson.decoder.JSONDecodeError
                print("JSON ERROR")
    except requests.exceptions.RequestException as error:
        print(error)
        sys.exit(1)


if __name__ == "__main__":
    coins = get_coins()
    pydict = {"Coin":'ETH'}
    while True:
        http_request("Balance",pydict, 'Get' )
