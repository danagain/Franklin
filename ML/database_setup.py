from pymongo import MongoClient


def form_db_connection(coin, endpoint):
    #client = MongoClient(endpoint)  # Connect to MongoDB Client WILL NOT WORK
    client = MongoClient(port=27017) # But then this will work ?
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