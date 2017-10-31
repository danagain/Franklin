import numpy as np
import time

def generate_statlists(datasource, quart_hour):
    lastprice = []
    xaxis = []
    meanlast = []
    stdhour = []
    stdupper = []
    stdlower = []
    if datasource.count() < (15*6):
        time.sleep(15*6)
    else:
        for doc in datasource.find():  # Iterate stored documents
            lastprice.append(doc['Last'])  # Store the entire collections last values in memory
        avgrecentprice = np.mean(lastprice[len(lastprice) - quart_hour : -1])
        recentstd = np.std(lastprice[len(lastprice) - (quart_hour):-1])
        recentstdupper = avgrecentprice + 2*(recentstd/2)
        recentstdlower = avgrecentprice - 2*(recentstd/2)
        return lastprice, xaxis, meanlast, stdhour, stdupper, stdlower, avgrecentprice, recentstd, recentstdupper, recentstdlower