const express = require("express");
const bittrex = require("node-bittrex-api");
const mongoClient = require("mongodb").MongoClient;
const mongoController = require("../controllers/mongo");
const loggingController = require("../controllers/logger.js")();

let mongoUrl;
if (process.env.APP_ENV) {
  mongoUrl = "mongodb://mongo:27017/franklin";
} else {
  mongoUrl = "mongodb://localhost:27017/franklin";
}

bittrex.options({
  apikey: process.env.BIT_API_KEY,
  apisecret: process.env.BIT_API_SECRET
});

const routes = () => {
  const router = express.Router();

  router.route("/api/balance/:currency").get((req, res) => {
    bittrex.getbalance({ currency: req.params.currency }, (data, err) => {
      loggingController.log({
        message: { info: data, headers: req.headers, method: req.method },
        severity: "info"
      });
      res.json(data);
    });
  });

  router.route("/api/coins").get((req, res, next) => {
    // This is where we change the coins we are working with - This is the ONLY place also :)
    const coins = [
      {
        coins: [
          "BTC-ETH",
          "BTC-NEO",
          "BTC-LTC",
          "USDT-BTC",
          "BTC-BCC",
          "BTC-VTC",
          "BTC-OMG",
          "BTC-DASH",
          "BTC-XRP"
        ]
      }
    ];
    res.json(coins);
  });

  router.route("/api/buy/:currency").post((req, res, next) => {
    loggingController.log({
      message: { info: req.body, headers: req.headers, method: req.method },
      severity: "info"
    });
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
      mongoController
        .insertDocuments(collection, req.body)
        .then(data => {
          res.json(data);
          db.close();
        })
        .catch(err => {
          loggingController.log({
            message: { info: err, headers: req.headers, method: req.method },
            severity: "error"
          });
          db.close();
          res.status(500).json([{ error: err }]);
        });
    });
  });

  router.route("/api/sell/:currency").post((req, res, next) => {
    loggingController.log({
      message: { info: req.body, headers: req.headers, method: req.method },
      severity: "info"
    });
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
      mongoController
        .insertDocuments(collection, req.body)
        .then(data => {
          db.close();
          res.json(data);
        })
        .catch(err => {
          loggingController.log({
            message: { info: err, headers: req.headers, method: req.method },
            severity: "error"
          });
          res.status(500).json([{ error: err }]);
        });
    });
  });

  router
    .route("/api/bittrex/:currency")
    .post((req, res, next) => {
      mongoClient.connect(mongoUrl, (err, db) => {
        const collection = db.collection(req.params.currency);
        mongoController
          .insertDocuments(collection, req.body)
          .then(data => {
            res.json(data);
            db.close();
          })
          .catch(err => {
            loggingController.log({
              message: { info: err, headers: req.headers, method: req.method },
              severity: "error"
            });
            db.close();
            res.status(500).json([{ error: err }]);
          });
      });
    })
    .get((req, res) => {
      mongoClient.connect(mongoUrl, (err, db) => {
        const collection = db.collection(req.params.currency);
        const documentCount = parseInt(req.query.n);
        mongoController
          .findDocuments(collection, documentCount)
          .then(data => {
            db.close();
            res.json(data);
          })
          .catch(err => {
            loggingController.log({
              message: { info: err, headers: req.headers, method: req.method },
              severity: "error"
            });
            db.close();
            res.status(500).json([{ error: err }]);
          });
      });
    });
  return router;
};

module.exports = routes;
