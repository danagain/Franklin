## 28/10/2017

Thoughts: 
The Streamer component would constantly stream data from bittrex's API into a database. The data in the database could then be used for machine learning algorithms and computations. This component would be constantly running and would act as a syncing mechanism between bettrix and Franklin.

The data that is stored in the database could be used as we see fit by any sort of learning algorithms. Once it has been computed the data can then be written to a new predictions table in the database which can be accessible via the web api component.

This way if a user wants to get a prediction they can request one via the web interface which calls the API to fetch prediction data from the table that has been updated from the learning's output.


### Types

The type '0' is a simple add operation, the type '1' is a delete operation and the type '2' is a replace/update operation.


### Inital outline

Grabbing the market summary every 15 seconds of BTC-ETH and storing in Database. Append the data object