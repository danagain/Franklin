const express = require( "express" );
const bittrex = require("node-bittrex-api");
const mongoClient = require('mongodb').MongoClient
const mongoController = require('../controllers/mongo')

const mongoUrl = process.env.MONGO;

bittrex.options({
    apikey: process.env.BIT_API_KEY,
    apisecret: process.env.BIT_API_SECRET
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
            console.log(req.body)
            console.log("Purchased!")
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
                const collection = db.collection(`buy-${req.params.currency}`)
                mongoController.insertDocuments(collection, req.body)
                    .then(db.close())
                    .then((data) => {
                        res.send(data)
                    })
                    .catch((err) => {
                        throw err
                    })
              });
        });
    router.route( "/api/sell/:currency" )
        .post( (req, res) => {
            console.log(req.body)
            console.log('Selling!')
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
                const collection = db.collection(`sell-${req.params.currency}`)
                mongoController.insertDocuments(collection, req.body)
                    .then(db.close())
                    .then((data) => {
                        res.send(data)
                    })
                    .catch((err) => {
                        throw err
                    })
              });
        } );

    return router;
};

module.exports = routes;
