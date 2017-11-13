# Franklin

Table of contents
=================

  * [Overview](#overview)
  * [Docker](#docker)
  * [Tests](#tests)
  * [Dependencies](#dependencies)

## Overview

#### API
The Web API component acts as a broker between the data layer and requestor for all other components. It is responsible for making all API calls to bittrex and all interactions with the Database.

#### Streamer
The Streamer component will query the API endpoint */api/markets* to get the list of markets that should be used to trade. It will then query the Bittrex API and insert relevant data to those markets into the Database.

#### Database
The Database will hold information that is streamed in from the Streamer component along with a separate table for computed data that has been written in from the Machine Learning components. There will also be a Users Database that will handle user authentication to the front-end of Franklin at a later date.

#### Hunter
The Hunter is the brains behind Franklin, It is caluclating which trades to make and when. Once it works out an action to make it will communicate with the Franklin API as it needs which in turns makes calls on its behalf.

<p align="center">
  <img src="https://github.com/danagain/Franklin/blob/master/docs/images/overview.png" alt="overview"/>
</p>

### Docker

To spin up this whole project simply run `docker-compose up -d` from the root of the repository. If you make any changes to the codebase and wish to test your changes locally be sure you run `docker-compose build` before you up the environment.

## Tests

#### Integration Tests
For Javascript components => `npm test`

## Dependencies

#### Node
*request*
*express*
*splunk-logging*
*bittrex-api-node*
*mongodb*
*body-parser*

#### Python
*numpy*
*scipy*
*requests*
