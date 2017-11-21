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

const BIT_API_KEY = process.env.BIT_API_KEY;

bittrex.options({
  apikey: BIT_API_KEY,
  apisecret: process.env.BIT_API_SECRET
});

const routes = () => {
  const router = express.Router();

  router.route("/balance/:currency").get((req, res, next) => {
    bittrex.sendCustomRequest(
      `https://bittrex.com/api/v1.1/account/getbalance?apikey=${BIT_API_KEY}&currency=${req
        .params.currency}`,
      (data, err) => {
        if (err) {
          loggingController.log({
            message: {
              info: err.message,
              headers: req.headers,
              uuid: req.params.uuid,
              market: req.params.currency,
              route: req.route.path
            },
            severity: "error"
          });
          res.status(500).json(err.message);
        } else {
          res.json(data);
        }
      },
      true
    );
  });

  router.route("/markets").get((req, res, next) => {
    // This is where we change the markets we are working with - This is the ONLY place also :)
    const markets = [
      {
        markets: [
          "BTC-NEO",
          "BTC-ETH",
          "BTC-BCC",
          "BTC-OMG",
          "BTC-LSK",
          "BTC-POWR",
          "BTC-GRS",
          "BTC-LTC",
          "BTC-ADA",
          "BTC-PAY",
          "BTC-CVC",
          "BTC-XRP",
          "BTC-MER",
          "BTC-CLUB",
          "BTC-QTUM",
          "BTC-EMC2",
          "BTC-FTC",
          "BTC-GRS",
          "BTC-SLR",
          "BTC-ETC",
          "BTC-VTC",
          "BTC-XLM",
          "BTC-NXT",
          "BTC-OK",
          "BTC-SALT",
          "BTC-XVG",
          "BTC-XEM",
          "BTC-DASH",
          "BTC-XMR",
          "BTC-WAVES",
          "BTC-DNT",
          "BTC-ZEC"
        ]
      }
    ];
    res.json(markets);
  });
  router.route("/buy/:currency").post((req, res, next) => {
    bittrex.tradebuy(
      {
        MarketName: req.params.currency,
        OrderType: req.body.OrderType,
        Quantity: req.body.Quantity,
        Rate: req.body.Rate,
        TimeInEffect: req.body.TimeInEffect, // supported options are 'IMMEDIATE_OR_CANCEL', 'GOOD_TIL_CANCELLED', 'FILL_OR_KILL'
        ConditionType: req.body.ConditionType, // supported options are 'NONE', 'GREATER_THAN', 'LESS_THAN'
        Target: req.body.Target // used in conjunction with ConditionType
      },
      (data, err) => {
        if (err) {
          loggingController.log({
            message: {
              info: err.message,
              headers: req.headers,
              body: req.body,
              method: req.method,
              route: req.route.path
            },
            severity: "error"
          });
          res.status(500).json(err.message);
        } else {
          loggingController.log({
            message: {
              info: data,
              headers: req.headers,
              body: req.body,
              method: req.method,
              route: req.route.path
            },
            severity: "info"
          });
          mongoClient.connect(mongoUrl, (err, db) => {
            const collection = db.collection(
              `transactions-${req.params.currency}`
            );
            mongoController
              .insertDocuments(collection, data)
              .then(data => {
                db.close();
                res.json(data);
              })
              .catch(err => {
                loggingController.log({
                  message: {
                    info: err.message,
                    headers: req.headers,
                    body: req.body,
                    method: req.method,
                    route: req.route.path
                  },
                  severity: "error"
                });
                db.close();
                res.status(500).json([{ error: err.message }]);
              });
          });
        }
      }
    );
  });
  router.route("/sell/:currency").post((req, res, next) => {
    bittrex.tradesell(
      {
        MarketName: req.params.currency,
        OrderType: req.body.OrderType,
        Quantity: req.body.Quantity,
        Rate: req.body.Rate,
        TimeInEffect: req.body.TimeInEffect, // supported options are 'IMMEDIATE_OR_CANCEL', 'GOOD_TIL_CANCELLED', 'FILL_OR_KILL'
        ConditionType: req.body.ConditionType, // supported options are 'NONE', 'GREATER_THAN', 'LESS_THAN'
        Target: req.body.Target // used in conjunction with ConditionType
      },
      (data, err) => {
        if (err) {
          loggingController.log({
            message: {
              info: err.message,
              headers: req.headers,
              body: req.body,
              method: req.method,
              route: req.route.path
            },
            severity: "error"
          });
          res.status(500).json(err.message);
        } else {
          loggingController.log({
            message: {
              info: data,
              body: req.body,
              headers: req.headers,
              method: req.method,
              route: req.route.path
            },
            severity: "info"
          });
          mongoClient.connect(mongoUrl, (err, db) => {
            const collection = db.collection(
              `transactions-${req.params.currency}`
            );
            mongoController
              .insertDocuments(collection, data)
              .then(data => {
                db.close();
                res.json(data);
              })
              .catch(err => {
                loggingController.log({
                  message: {
                    info: err.message,
                    headers: req.headers,
                    body: req.body,
                    method: req.method,
                    route: req.route.path
                  },
                  severity: "error"
                });
                res.status(500).json([{ error: err.message }]);
              });
          });
        }
      }
    );
  });
  router.route("/cancel/:uuid").get((req, res, next) => {
    bittrex.sendCustomRequest(
      `https://bittrex.com/api/v1.1/market/cancel?apikey=${BIT_API_KEY}&uuid=${req
        .params.uuid}`,
      (data, err) => {
        if (err) {
          loggingController.log({
            message: {
              info: err.message,
              headers: req.headers,
              uuid: req.params.uuid,
              method: req.method,
              route: req.route.path
            },
            severity: "error"
          });
          res.status(500).json(err.message);
        } else {
          res.json(data);
        }
      },
      true
    );
  });
  router.route("/historical/:market").get((req, res, next) => {
    bittrex.sendCustomRequest(
      `https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName=${req.params.market}&tickInterval=${req
        .query.interval}`,
      (data, err) => {
        if (err) {
          loggingController.log({
            message: {
              info: err.message,
              headers: req.headers,
              method: req.method,
              route: req.route.path
            },
            severity: "error"
          });
          res.status(500).json(err.message);
        } else {
          res.json(data);
        }
      },
      true
    );
  });
  router.route("/summary/:market").get((req, res, next) => {
    bittrex.sendCustomRequest(
      `https://bittrex.com/api/v1.1/public/getmarketsummary?market=${req.params.market}`,
      (data, err) => {
        if (err) {
          loggingController.log({
            message: {
              info: err.message,
              headers: req.headers,
              market: req.params.market,
              method: req.method,
              route: req.route.path
            },
            severity: "error"
          });
          res.status(500).json(err.message);
        } else {
          res.json(data);
        }
      },
      true
    );
  });
  router.route("/orders/:currency").get((req, res, next) => {
    bittrex.sendCustomRequest(
      `https://bittrex.com/api/v1.1/market/getopenorders?apikey=${BIT_API_KEY}&market=${req
        .params.currency}`,
      (data, err) => {
        if (err) {
          loggingController.log({
            message: {
              info: err.message,
              headers: req.headers,
              market: req.params.currency,
              method: req.method,
              route: req.route.path
            },
            severity: "error"
          });
          res.status(500).json(err.message);
        } else {
          res.json(data);
        }
      },
      true
    );
  });
  router
    .route("/bittrex/:currency")
    .post((req, res, next) => {
      mongoClient.connect(mongoUrl, (err, db) => {
        const collection = db.collection(req.params.currency);
        mongoController
          .insertDocuments(collection, req.body)
          .then(data => {
            db.close();
            res.json(data);
          })
          .catch(err => {
            loggingController.log({
              message: {
                info: err.message,
                headers: req.headers,
                body: req.body,
                method: req.method,
                route: req.route.path
              },
              severity: "error"
            });
            db.close();
            res.status(500).json([{ error: err.message }]);
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
              message: {
                info: err.message,
                headers: req.headers,
                body: req.body,
                method: req.method,
                route: req.route.path
              },
              severity: "error"
            });
            db.close();
            res.status(500).json([{ error: err.message }]);
          });
      });
    });
  return router;
};

module.exports = routes;
