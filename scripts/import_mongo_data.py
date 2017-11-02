import csv
import json
import pandas as pd
import sys, getopt, pprint
from pymongo import MongoClient

docs = ["USDT-BTC","BTC-LTC","BTC-NEO","BTC-ETH"]

for i in range(0, len(docs)):
    csvfile = open('./imports/{0}.csv'.format(docs[i]), 'r')
    reader = csv.DictReader( csvfile )
    client = MongoClient()
    db = client.franklin
    col = docs[i]
    header = ["MarketName","High","Low","Volume","Last","BaseVolume","Bid","Ask","OpenBuyOrders","OpenSellOrders","PrevDay","Created"]

    for each in reader:
        row = {}
        for field in header:
            try:
                value = float(each[field])
            except ValueError:
                value = str(each[field])

            row[field] = value

        db[col].insert(row)

    print("Complete for {0}".format(docs[i]))
