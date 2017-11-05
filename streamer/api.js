const bittrex = require("node-bittrex-api");
const loggingController = require("./controllers/logger.js")();
const request = require("request")

const mongoUrl = process.env.MONGO;

bittrex.options({
  apikey: process.env.BIT_API_KEY,
  apisecret: process.env.BIT_API_SECRET
});

// 10 Second interval
const interval = 10 * 1000;

setInterval(() => {
  console.log("Complete => Running in 10 seconds");

  request.get("http://web-api:3000/api/coins", (error, response) => {
    if (error) {
      loggingController.log({
        message: { info: err },
        severity: "error"
      });
      throw err;
    }
    bittrex.getmarketsummaries((data, err) => {
      if (err) {
        throw err;
      }

      // Return array of market information for the above names
      const marketArray = data.result.filter(obj => {
        if (response.body.indexOf(obj.MarketName) === -1) {
          return false;
        }
        return true;
      });
      marketArray.map(coin => {
        request.post({
          url: `http://web-api:3000/api/bittrex/${coin.MarketName}`,
          json: true,
          body: coin
      });
      });
    });
  });
}, interval);
