"use strict";

const express = require( "express" ),
    ejs = require( "ejs" ), // eslint-disable-line no-unused-vars
    router = require( "./routes/routes" )();

const app = express();

// View Engine
app.set( "view engine", "ejs" );

// Middleware
app.use( express.static( "static" ) );

// Routes
app.use( "/", router );

// Catch all 404's
app.get( "*", ( req, res ) => {
    res.status( 404 ).render( "404" );
} );

// Listener
const server = app.listen( 3000, () => {
    console.log( "listening on port 3000" );
} );

module.exports = server;
