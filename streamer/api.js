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
