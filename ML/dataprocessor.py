import numpy as np
import matplotlib.pyplot as plt
import os
import time
from pymongo import MongoClient
from sklearn import model_selection, neighbors

HOUR = 60 * 4  # Constant representing the data points per hour (15s intervals)


def generate_stat_lists(datasource, HOUR):
    lastprice = []
    xaxis = []
    meanlast = []
    stdhour = []
    stdupper = []
    stdlower = []
    count = 0
    datapts = 60 * 4  # Every 60 mins there is 60*4 data points (1pt per 15s) - neglecting holes in the data
    for doc in datasource.find():  # Iterate stored documents
        count += 1
        lastprice.append(doc['Last'])  # Store the entire collections last values in memory
        xaxis.append(count)  # Making a quick and easy xaxis for plotting purposes
        if count == datapts:  # When we have iterated 1 hours worth of data
            meanlast.append(
                np.mean(lastprice[len(lastprice) - (HOUR):-1]))  # total indexs - hourly count : iterate to end
            stdhour.append(np.std(lastprice[len(lastprice) - (HOUR):-1]))
            stdupper.append(meanlast[-1] + 3 * (stdhour[-1] / 2))
            stdlower.append(meanlast[-1] - 3 * (stdhour[-1] / 2))
            datapts += HOUR
    return lastprice, xaxis, meanlast, stdhour, stdupper, stdlower


def form_db_connection(endpoint):
    client = MongoClient(endpoint)  # Connect to MongoDB Client
    db = client.franklin  # Access the franklin database
    datasource = db.bittrex  # Point to the Bittrex table
    return datasource


def plotting(xaxis, ydata, ydatamean, stdupper, stdlower):
    xmean = np.linspace(1, max(xaxis), len(ydatamean))
    plt.plot(xaxis, ydata)  # Best way to quickly understand the data
    plt.plot(xmean, ydatamean)
    plt.plot(xmean, stdupper)
    plt.plot(xmean, stdlower)
    plt.xlabel('Linear vector')
    plt.ylabel('Last Price')
    plt.show()


def classify_data(meanlast):
    X = meanlast
    classid = []
    if len(meanlast) > 2:
        for i in range(len(X) - 1):
            # check every closing price and if the closing price for today is greater than yesterday
            # then classify as '1' , else '0'
            if X[i] < X[i + 1]:
                classid.append(1)
            else:
                classid.append(0)
        if X[-2] < X[-1]:
            classid.append(1)
        else:
            classid.append(0)
    return classid


def build_NN_classifier(X_training, y_training, currentprice):
    '''
        #10-fold cross validation with K=5 for KNN
        # search for an optiomal value of K for KNN
        '''
    k_range = range(1, 20)
    k_scores = []
    for k in k_range:
        knn = neighbors.KNeighborsClassifier(n_neighbors=k)
        scores = model_selection.cross_val_score(knn, X_training, y_training, cv=10, scoring='accuracy')
        k_scores.append(scores.mean())
    plt.plot(k_range, k_scores)
    plt.xlabel('Value of k for KNN')
    plt.ylabel('Cross-Validated Accuracy')
    plt.show()
    best_k = np.argmax(k_scores)
    # print("best k value is : ",best_k, "with accuracy of : ",k_scores[best_k])


    # Only Really need the 5 lines below this comment for the NN classifier, all of the above code
    # is just to determine how many neighbours is an optimal parameter for the system
    clf = neighbors.KNeighborsClassifier(n_neighbors=best_k)  # use best score param
    X_train, X_test, y_train, y_test = model_selection.train_test_split(X_training, y_training, test_size=0.15, \
                                                                        random_state=42)
    clf.fit(X_train, y_train)
    prediction = clf.predict(currentprice)
    print(prediction)

if __name__ == "__main__":
    if os.environ['APP_ENV'] == 'docker':
        print("Sleeping for 20 seconds - waiting for data to be Mongo")
        time.sleep(
            20)  # Since this is in docker lets just wait slightly here before connecting to Mongo, ensures everything is up and running
        endpoint = "mongodb://mongo:27017/franklin"
    else:
        endpoint = "mongodb://franklin:theSEGeswux8stat@ds241055.mlab.com:41055/franklin"

    print("Mongo Endpoint is {0}".format(endpoint))
    datasource = form_db_connection(endpoint)
    if datasource.bitcoin.find().count() > 2 * HOUR:
        lastprice, xaxis, meanlast, stdhour, stdupper, stdlower = generate_stat_lists(datasource, HOUR)
        ml = classify_data(meanlast)
        build_NN_classifier(np.reshape(meanlast, (-1, 1)), ml, lastprice[-1])  # KNN prediciton on current price
        plotting(xaxis, lastprice, meanlast, stdupper, stdlower)
    else:
        print("Waiting for more data to continue ...")
