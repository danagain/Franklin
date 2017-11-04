const express = require("express");
const bittrex = require("node-bittrex-api");
const mongoClient = require("mongodb").MongoClient;
const mongoController = require("../controllers/mongo");
const SplunkLogger = require("splunk-logging").Logger;
const loggingController = require('../controllers/logger.js')();

const splunkConfig = {
   token: process.env.SPLUNKTOKEN,
   url: "https://splunk:8088"
};

const logger = new SplunkLogger(splunkConfig);

const mongoUrl = process.env.MONGO;

bittrex.options({
  apikey: process.env.BIT_API_KEY,
  apisecret: process.env.BIT_API_SECRET
});

const routes = () => {
  const router = express.Router();

  router.route("/api").get((req, res, next) => {
    loggingController.log({message: { info: [{ version: "0.0.1" }], headers: req.headers, method: req.method }, severity: 'info'})
    res.json([{ version: "0.0.1" }]);
  });
  router.route("/api/balance/:currency").get((req, res) => {
    bittrex.getbalance({ currency: req.params.currency }, (data, err) => {
      loggingController.log({message: { info: data, headers: req.headers, method: req.method }, severity: 'info'})
      res.json(data);
    });
  });

  router.route("/api/coins").get((req, res, next) => {
    res.json([{coins: ['BTC-ETH','BTC-NEO', 'BTC-LTC', 'USDT-BTC']}]);
  });

  router.route("/api/buy/:currency").post((req, res, next) => {
    loggingController.log({message: { info: req.body, headers: req.headers, method: req.method }, severity: 'info'})
    // bittrex.tradebuy({
    //     MarketName: req.params.currency,
    //     OrderType: req.body.OrderType,
    //     Quantity: req.body.Quantity,
    //     Rate: req.body.Rate,
    //     TimeInEffect: req.body.TimeInEffect, // supported options are 'IMMEDIATE_OR_CANCEL', 'GOOD_TIL_CANCELLED', 'FILL_OR_KILL'
    //     ConditionType: req.body.ConditionType, // supported options are 'NONE', 'GREATER_THAN', 'LESS_THAN'
    //     Target: req.body.Target, // used in conjunction with ConditionType
    //   }, ( data, err ) => {
    //     res.json( data );
    //   });
    mongoClient.connect(mongoUrl, (err, db) => {
      const collection = db.collection(`buy-${req.params.currency}`);
      mongoController.insertDocuments(collection, req.body)
        .then(data => {
          res.send(data);
          db.close();
        })
        .catch(err => {
          res.status(500).json([{error: err}]);
          res.end()
        });
    });
  });
  router.route("/api/sell/:currency").post((req, res, next) => {
    loggingController.log({message: { info: req.body, headers: req.headers, method: req.method }, severity: 'info'})
    // bittrex.tradesell({
    //     MarketName: req.params.currency,
    //     OrderType: req.body.OrderType,
    //     Quantity: req.body.Quantity,
    //     Rate: req.body.Rate,
    //     TimeInEffect: req.body.TimeInEffect, // supported options are 'IMMEDIATE_OR_CANCEL', 'GOOD_TIL_CANCELLED', 'FILL_OR_KILL'
    //     ConditionType: req.body.ConditionType, // supported options are 'NONE', 'GREATER_THAN', 'LESS_THAN'
    //     Target: req.body.Target, // used in conjunction with ConditionType
    //   }, ( data, err ) => {
    //     res.json( data );
    //   });
    mongoClient.connect(mongoUrl, (err, db) => {
      const collection = db.collection(`sell-${req.params.currency}`);
      mongoController.insertDocuments(collection, req.body)
        .then(data => {
          res.send(data);
          db.close();
        })
        .catch(err => {
          res.status(500).json([{error: err}]);
          res.end()
        });
    });
  });
  router.route("/api/graph/:currency")
    .get((req, res, next) => {
      mongoClient.connect(mongoUrl, (err, db) => {
        const collection = db.collection(`graph-${req.params.currency}`);
        let arr = [];
        let arr2 = [];
        let arr3 = [];
        let arr4 = [];
        mongoController.findDocuments(collection)
          .then(data => {
            for(var x in data){
              let lastarr = [parseInt(data[x]['time']), data[x]['Last']];
              let upperarr = [parseInt(data[x]['time']), data[x]['Upper']];
              let lowerarr = [parseInt(data[x]['time']), data[x]['Lower']];
              arr.push(lastarr);
              arr2.push(upperarr);
              arr3.push(lowerarr);
            }
              arr4.push(arr);
              arr4.push(arr2);
              arr4.push(arr3);

            res.send(arr4);
            db.close()
          })
          .catch(err => {
            res.status(500).json([{error: err}]);
            res.end()
          });
      });
    })
    .post((req, res, next) => {
      loggingController.log({message: { info: req.body, headers: req.headers, method: req.method }, severity: 'info'})
      mongoClient.connect(mongoUrl, (err, db) => {
        const collection = db.collection(`graph-${req.params.currency}`);
        mongoController.insertDocuments(collection, req.body)
          .then(data => {
            res.send(data);
            db.close();
          })
          .catch(err => {
            res.status(500).json([{error: err}]);
            res.end()
          });
      });
    });

  return router;
};

module.exports = routes;
