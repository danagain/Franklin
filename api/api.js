"use strict";

const express = require("express"),
  bodyParser = require("body-parser"),
  router = require("./routes/routes")();

const app = express();

// parse application/json
app.use(bodyParser.json());


app.use((req, res, next) => {

    // Website you wish to allow to connect
    res.setHeader('Access-Control-Allow-Origin', 'http://localhost:5000');

    // Request methods you wish to allow
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');

    // Request headers you wish to allow
    res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type');

    // Set to true if you need the website to include cookies in the requests sent
    // to the API (e.g. in case you use sessions)
    res.setHeader('Access-Control-Allow-Credentials', true);

    // Pass to next layer of middleware
    next();
});

// Routes
app.use("/", router);

// Catch all 404's
app.get("*", (req, res) => {
  res.status(404).json([{ "Not found": true }]);
});

// Listener
const server = app.listen(3000, () => {
  console.log("listening on port 3000");
});

module.exports = server;
