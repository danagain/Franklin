const bittrex = require("node-bittrex-api");
const MongoClient = require("mongodb").MongoClient;

// Check to see if running inside a container. If so assume local development, else prod.
let connectionString;
if (process.env.APP_ENV === 'docker') {
  connectionString = "mongodb://mongo:27017/franklin";
} else {
  connectionString =
    "mongodb://franklin:theSEGeswux8stat@ds241055.mlab.com:41055/franklin";
}

// 10 Second interval
const interval = 10 * 1000;

setInterval(() => {
  console.log("Complete => Running in 10 seconds");

  // change this to env vars later
  bittrex.options({
    apikey: "1b64d15bace644849152c9e42f7091bc",
    apisecret: "5d392d3589004bf9988b72f10022c509"
  });

  // Use connect method to connect to the Server
  MongoClient.connect(connectionString, (err, db) => {
    console.log("Connected correctly to server");

    insertDocuments(db, () => {
      db.close();
    });
  });

  const insertDocuments = (db, callback) => {
    const ethcollection = db.collection("ethereum");
    const bitcoincollection = db.collection("bitcoin");
    const neocollection = db.collection("neo");
    const ltccollection = db.collection("ltc");

    bittrex.getmarketsummaries((data, err) => {
      if (err) {
        throw err;
      }
      const btcEth = data.result.filter(item => {
        return item.MarketName === "BTC-ETH";
      });
      const usdBtc = data.result.filter(item => {
        return item.MarketName === "USDT-BTC";
      });
      const btcNeo = data.result.filter(item => {
        return item.MarketName === "BTC-NEO";
      });
      const btcLtc = data.result.filter(item => {
        return item.MarketName === "BTC-LTC";
      });

      bitcoincollection.insertMany(usdBtc, (err, result) => {
        callback(result);
      });
      neocollection.insertMany(btcNeo, (err, result) => {
        callback(result);
      });
      ltccollection.insertMany(btcLtc, (err, result) => {
        callback(result);
      });
      ethcollection.insertMany(btcEth, (err, result) => {
        callback(result);
      });
    });
  };
}, interval);
