# Franklin

Table of contents
=================

  * [Overview](#overview)
  * [Installation](#installation)
  * [Usage](#usage)
    * [Web Interface](#webinterface)
  * [Tests](#tests)
  * [Dependencies](#dependencies)


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

#### Tests
For Javascript components => `npm test`

## Dependencies
See `requirements.txt` for Python Components and Package.json for Javascript components.
