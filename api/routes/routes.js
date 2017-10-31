const express = require( "express" );
const bittrex = require("node-bittrex-api");

let connectionString;
if (process.env.APP_ENV === 'docker') {
  connectionString = "mongodb://mongo:27017/franklin";
} else {
  connectionString =
    "mongodb://franklin:theSEGeswux8stat@ds241055.mlab.com:41055/franklin";
}

// change this to env vars later
bittrex.options({
    apikey: "1b64d15bace644849152c9e42f7091bc",
    apisecret: "5d392d3589004bf9988b72f10022c509"
});

const routes = () => {

    // Create Router
    const router = express.Router();

    router.route( "/api" )
        .get( ( req, res ) => {
            res.json([{"version": "0.0.1"}])
        } );
    router.route( "/api/balance/:currency" )
        .get( (req, res) => {
            bittrex.getbalance({ currency : req.params.currency }, ( data, err ) => {
                res.json(data)
              });
        } );
    router.route( "/api/buy/:currency" )
        .post( (req, res) => {
            bittrex.tradebuy({
                MarketName: req.params.currency,
                OrderType: req.body.OrderType,
                Quantity: req.body.Quantity,
                Rate: req.body.Rate,
                TimeInEffect: req.body.TimeInEffect, // supported options are 'IMMEDIATE_OR_CANCEL', 'GOOD_TIL_CANCELLED', 'FILL_OR_KILL'
                ConditionType: req.body.ConditionType, // supported options are 'NONE', 'GREATER_THAN', 'LESS_THAN'
                Target: req.body.Target, // used in conjunction with ConditionType
              }, ( data, err ) => {
                res.json( data );
              });
        } );
    router.route( "/api/sell/:currency" )
        .post( (req, res) => {
            bittrex.tradesell({
                MarketName: req.params.currency,
                OrderType: req.body.OrderType,
                Quantity: req.body.Quantity,
                Rate: req.body.Rate,
                TimeInEffect: req.body.TimeInEffect, // supported options are 'IMMEDIATE_OR_CANCEL', 'GOOD_TIL_CANCELLED', 'FILL_OR_KILL'
                ConditionType: req.body.ConditionType, // supported options are 'NONE', 'GREATER_THAN', 'LESS_THAN'
                Target: req.body.Target, // used in conjunction with ConditionType
              }, ( data, err ) => {
                res.json( data );
              });
        } );

    return router;
};

module.exports = routes;
