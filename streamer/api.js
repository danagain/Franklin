const bittrex = require("node-bittrex-api");
const MongoClient = require("mongodb").MongoClient;

const mongoUrl = process.env.MONGO;

bittrex.options({
    apikey: process.env.BIT_API_KEY,
    apisecret: process.env.BIT_API_SECRET
});

// 10 Second interval
const interval = 10 * 1000;

setInterval(() => {
  console.log("Complete => Running in 10 seconds");

  // Use connect method to connect to the Server
  MongoClient.connect(mongoUrl, (err, db) => {
    console.log("Connected correctly to server");

    insertDocuments(db, () => {
      db.close();
    });
  });

  const insertDocuments = (db, callback) => {
    bittrex.getmarketsummaries((data, err) => {
      if (err) { throw err }
      // The markets we're interested in
      const marketName = ["BTC-ETH", "USDT-BTC", "BTC-NEO", "BTC-LTC"];

      // Return array of market information for the above names
      const marketArray = data.result.filter((obj) => {
            if(marketName.indexOf(obj.MarketName) === -1) {
              return false;
            }
            return true;
          });

      // map the markets and insert into their specific mongo collection
      marketArray.map((item) => {
        const collection = db.collection(item.MarketName);
        collection.insertMany([item], (err, result) => {
          if (err) { throw err }
          callback(result);
        });
      })
    });
  };
}, interval);
