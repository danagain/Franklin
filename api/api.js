"use strict";

const express = require("express"),
  bodyParser = require("body-parser"),
  router = require("./routes/routes")();

const app = express();

// parse application/json
app.use(bodyParser.json());

// Routes
app.use("/api", router);

// Catch all 404's
app.get("*", (req, res) => {
  res.status(404).json([{ "Not found": true }]);
});

// Listener
const server = app.listen(3000, () => {
  console.log("listening on port 3000");
});

module.exports = server;
