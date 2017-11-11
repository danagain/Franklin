const mongoClient = require("mongodb").MongoClient;
const mongoController = require("../controllers/mongo");
const assert = require("assert");

const mongoUrl = "mongodb://localhost:27017/franklin";

const mockedEntry = {
  success: true,
  message: "",
  result: {
    uuid: "e606d53c-8d70-11e3-94b5-425861b86ab6"
  }
};

mongoClient.connect(mongoUrl, (err, db) => {
  const collection = db.collection("transactions-BTC-ETH");
  mongoController
    .findOrderStatus(collection, mockedEntry.result.uuid)
    .then(data => {
      console.log(data);
      db.close();
    })
    .catch(err => {
      console.log(err);
    });
});
