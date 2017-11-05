# Franklin

Table of contents
=================

  * [Overview](#overview)
  * [Installation](#installation)
  * [Usage](#usage)
    * [Web Interface](#webinterface)
  * [Tests](#tests)
  * [Dependencies](#dependencies)
  * [Database Export/Import](#database-export-import)


## Overview

#### Web
The Web component is the user facing front-end to Franklin.

#### Web API
The Web API component acts as a broker between the data layer and the front-end.
The API will be used to interact with the data tier to retrieve and store data as required.

#### Streamer
The Streamer component will stream data via web sockets from the Bittrex API into the Database.

#### Database
The Database will hold information that is streamed in from the Streamer component along with a separate table for computed data that has been written in from the Machine Learning components. There will also be a Users Database that will handle user authentication to the front-end of Franklin at a later date.

#### Machine Learning (ML)
The Machine Learning component will interact with the database to retreive information and run through a predefined list of algorithms on the data. Once computation is complete the data can be written to a Database table that is able to be quiered by the Web API for users wanting predictions.

<p align="center">
  <img src="https://github.com/danagain/Franklin/blob/master/docs/images/overview.png" alt="overview"/>
</p>


## Installation

TO-DO

## Usage

TO-DO

### Docker

To spin up this whole project simply run `docker-compose up -d` from the root of the repository. If you make any changes to the codebase and wish to test your changes locally be sure you run `docker-compose build` before you up the environment.

### Web Interface

TO-DO

## Tests

#### Linting
For Javascript components => `npm lint`

#### Acceptance Tests
For Javascript components => `npm test | tap-spec` (After you have done docker-compose up -d)

## Dependencies
See `requirements.txt` for Python Components and Package.json for Javascript components.

## Database Export/Import
The below assumes you are working with this project in its default `docker-compose` environment.

The ability to import and export bulk CSV files into the database is available. If you wish to export the currently running MongoDB Database into CSV files simply run the `mongo_export.sh` script within the *scripts* folder. This will export a CSV file for each collection in MongoDB and place them in the *imports* folder within the *scripts* directory.

You can also Import CSV files into MongoDB by placing the CSV files you wish to import into the *imports* folder and running the `import_mongo_data.py` file. This will take each of the CSV files within the imports folder and import them into their own collection.


## TO-DO

* Add Hunter tests.
* Add extensive API tests with Mock data (when x is called with y data it should 404, or should return xyz).
* Add single command for testing all components.
* Work out hosting options:
  * AWS? (Could make new account and use free tier)
  * Cheap LaNode option or something?
* Estimate data storage requirements for Splunk and for MongoDB. (current 500MB limit)
* Remove web component and its code once happy with Splunk.
* Create new Bittrex account to use for official trades. Ensure the account has the ability to make trades.


