const request = require( "supertest" );
 
const app = require( "../index" );
 
describe( "GET on main router paths", () => {
    it( "/ returns with 200", ( done ) => {
        request( app )
            .get( "/" )
            .expect( 200, done );
    } );
    it( "/news returns with 200", ( done ) => {
        request( app )
            .get( "/news" )
            .expect( 200, done );
    } );
    it( "/predictions returns with 200", ( done ) => {
        request( app )
            .get( "/predictions" )
            .expect( 200, done );
    } );
    it( "/fail returns with 404", ( done ) => {
        request( app )
            .get( "/fail" )
            .expect( 404, done );
    } );
} );

// Close the server
app.close();
