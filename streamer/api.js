const bittrex = require("node-bittrex-api");
const loggingController = require("./controllers/logger.js")();
const request = require("request");

const mongoUrl = process.env.MONGO;

bittrex.options({
  apikey: process.env.BIT_API_KEY,
  apisecret: process.env.BIT_API_SECRET
});

// Interval
const interval = process.env.TIMEINTERVAL * 1000;

setInterval(() => {
  console.log(`Complete => Running in ${process.env.TIMEINTERVAL} seconds`);

  request.get("http://web-api:3000/api/markets", (error, response) => {
    if (error) {
      loggingController.log({
        message: { info: error },
        severity: "error"
      });
      throw error;
    }
    bittrex.getmarketsummaries((data, err) => {
      if (err) {
        loggingController.log({
          message: { info: err },
          severity: "error"
        });
        throw err;
      }

      // Return array of market information for markets returned from /api/markets
      const marketArray = data.result.filter(obj => {
        if (response.body.indexOf(obj.MarketName) === -1) {
          return false;
        }
        return true;
      });

      marketArray.map(market => {
        request.post({
          url: `http://web-api:3000/api/bittrex/${market.MarketName}`,
          json: true,
          body: market
        });
      });
    });
  });
}, interval);
