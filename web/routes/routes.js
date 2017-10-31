const express = require( "express" );

const routes = () => {

    // Create Router
    const router = express.Router();

    router.route( "/" )
        .get( ( req, res ) => {
            res.render( "index" );
        } );

    router.route( "/news" )
        .get( ( req, res ) => {
            res.render( "news" );
        } );

    router.route( "/predictions" )
        .get( ( req, res ) => {
            res.render( "predictions" );
        } );
    
    return router;
};

module.exports = routes;
