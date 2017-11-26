# Franklin

Table of contents
=================

  * [Overview](#overview)
  * [Docker](#docker)
  * [Tests](#tests)
  * [Dependencies](#dependencies)

## Overview

#### API
The Web API component acts as a broker between the data layer and requestor for all other components. It is responsible for making all API calls to bittrex and all interactions.

#### Hunter
The Hunter is the brains behind Franklin, It is caluclating which trades to make and when. Once it works out an action to make it will communicate with the Franklin API as it needs which in turns makes calls on its behalf.

### Docker

To spin up this whole project simply run `docker-compose up -d` from the root of the repository. If you make any changes to the codebase and wish to test your changes locally be sure you run `docker-compose build` before you up the environment.

## Tests

#### Integration Tests (API)
For Javascript components => `npm test`