from pymongo import MongoClient


def form_db_connection(coin, endpoint):
    #client = MongoClient(endpoint)  # Connect to MongoDB Client WILL NOT WORK
    client = MongoClient(port=27017) # But then this will work ?
    db = client.franklin  # Access the franklin database
    # This is not a very elegent solution but I don't know how to pass the db coin as a parameter
    if coin == "bitcoin":
        data_source = db.bitcoin
        return data_source
    if coin == "ltc":
        data_source = db.ltc
        return data_source
    if coin == "neo":
        data_source = db.neo
        return data_source
    if coin == "ethereum":
        data_source = db.ethereum
        return data_source