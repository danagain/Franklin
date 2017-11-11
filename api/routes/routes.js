const express = require("express");
const bittrex = require("node-bittrex-api");
const mongoClient = require("mongodb").MongoClient;
const mongoController = require("../controllers/mongo");
const requests = require("requests");
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
      if (err) {
        loggingController.log({
          message: {
            info: err.message,
            headers: req.headers,
            body: req.body,
            method: req.method,
            route: req.route.path,
            market: req.params.currency
          },
          severity: "error"
        });
        res.status(500).send(err.message);
      } else {
        res.json(data);
      }
    });
  });

  router.route("/api/markets").get((req, res, next) => {
    // This is where we change the markets we are working with - This is the ONLY place also :)
    const markets = [
      {
        markets: [
          "BTC-ETH",
          "BTC-NEO",
          "BTC-LTC",
          "BTC-BCC",
          "BTC-VTC",
          "BTC-OMG",
          "BTC-DASH"
        ]
      }
    ];
    res.json(markets);
  });

  router.route("/api/buy/:currency").post((req, res, next) => {
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
          res.status(500).send(err.message);
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

  router.route("/api/sell/:currency").post((req, res, next) => {
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
          res.status(500).send(err.message);
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

  router
    .route("/api/orders/:currency/:uuid")
    .post((req, res, next) => {
      requests.post(
        `https://bittrex.com/api/v1.1/market/cancel?apikey=${process.env
          .BIT_API_KEY}&uuid=${req.params.uuid}`,
        (err, res) => {
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
            res.status(500).send(err.message);
          } else {
            mongoClient.connect(mongoUrl, (err, db) => {
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
                res.status(500).send(err.message);
              }
              const collection = db.collection(
                `transactions-${req.params.currency}`
              );
              mongoController
                .updateOrderStatus(collection, req.params.uuid)
                .then(data => {
                  db.close();
                  res.json(data);
                })
                .catch(err => {
                  loggingController.log({
                    message: {
                      info: err.message,
                      headers: req.headers,
                      uuid: req.params.uuid,
                      body: req.params.currency,
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
    })
    .get((req, res, next) => {
      mongoClient.connect(mongoUrl, (err, db) => {
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
          res.status(500).send(err.message);
        }
        const collection = db.collection(`transactions-${req.params.currency}`);
        mongoController
          .findOrderStatus(collection, req.params.uuid)
          .then(data => {
            db.close();
            res.json(data);
          })
          .catch(err => {
            loggingController.log({
              message: {
                info: err.message,
                headers: req.headers,
                uuid: req.params.uuid,
                body: req.params.currency,
                method: req.method,
                route: req.route.path
              },
              severity: "error"
            });
            res.status(500).json([{ error: err.message }]);
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
