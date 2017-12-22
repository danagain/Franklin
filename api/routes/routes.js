const express = require("express");
const bittrex = require("node-bittrex-api");
const emailer = require("../controllers/emailer");
const loggingController = require("../controllers/logger.js")();

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
              error: err,
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
          "BTC-ETH",
          "BTC-BCC",
          "BTC-BTG",
          "BTC-SYS",
          "BTC-VTC",
          "BTC-EMC2",
          "BTC-NEO",
          "BTC-LTC",
          "BTC-POWR",
          "BTC-OMG",
          "BTC-XVG",
          "BTC-TIX",
          "BTC-TRIG",
          "BTC-XRP",
          "BTC-ETC",
          "BTC-DASH",
          "BTC-RCN",
          "BTC-STRAT",
          "BTC-LSK",
          "BTC-SHIFT",
          "BTC-DCR",
          "BTC-POT",
          "BTC-ZEC",
          "BTC-ADA",
          "BTC-XLM",
          "BTC-NXT",
          "BTC-QTUM",
          "BTC-OK",
          "BTC-XMR",
          "BTC-TRUST",
          "BTC-NXS",
          "BTC-MONA",
          "BTC-ARK",
          "BTC-KMD",
          "BTC-XZC",
          "BTC-CLUB",
          "BTC-PTOY",
          "BTC-PAY",
          "BTC-NMR",
          "BTC-CVC",
          "BTC-NAV",
          "BTC-NXT",
          "BTC-VOX",
          "BTC-DGD",
          "BTC-MER",
          "BTC-ADX",
          "BTC-WAVES",
          "BTC-ZEN",
          "BTC-RISE",
          "BTC-SNT",
          "BTC-MCO",
          "BTC-GUP",
          "BTC-IOP"
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
              error: err,
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
          emailer.email(data)
          res.json(data);
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
              error: err,
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
          emailer.email(data)
          res.json(data);
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
              error: err,
              headers: req.headers,
              uuid: req.params.uuid,
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
          res.json(data);
        }
      },
      true
    );
  });
  router.route("/historical/:market").get((req, res, next) => {
    bittrex.sendCustomRequest(
      `https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName=${req.params
        .market}&tickInterval=${req.query.interval}`,
      (data, err) => {
        if (err) {
          loggingController.log({
            message: {
              error: err,
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
      `https://bittrex.com/api/v1.1/public/getmarketsummary?market=${req.params
        .market}`,
      (data, err) => {
        if (err) {
          loggingController.log({
            message: {
              error: err,
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
              error: err,
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
  return router;
};

module.exports = routes;
