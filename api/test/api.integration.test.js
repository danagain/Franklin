const request = require("supertest");
const test = require("tape");
const app = require("../api");
const bodyParser = require("body-parser");

console.log(
  "Running Integration Tests, Ensure Docker-Compose env is up and running."
);

const expectedMarkets = [
  {
    markets: [
      "BTC-ETH",
      "BTC-NEO",
      "BTC-LTC",
      "BTC-BCC",
      "BTC-VTC",
      "BTC-OMG",
      "BTC-DASH"
    ]
  }
];

test("/ should 404", t => {
  request(app)
    .get("/")
    .expect(404)
    .end((err, res) => {
      t.error(err, "No error");
      t.end();
    });
});
test("/api should 404", t => {
  request(app)
    .get("/api")
    .expect(404)
    .end((err, res) => {
      t.error(err, "No error");
      t.end();
    });
});
test("/api/balance/BTC be 200", t => {
  request(app)
    .get("/api/balance/BTC")
    .expect("Content-Type", /json/)
    .expect(200)
    .end((err, res) => {
      t.error(err, "No error");
      t.end();
    });
});
test("/api/markets be valid", t => {
  request(app)
    .get("/api/markets")
    .expect("Content-Type", /json/)
    .expect(200)
    .end((err, res) => {
      t.same(res.body, expectedMarkets, "Markets as expected");
      t.error(err, "No error");
      t.end();
    });
});

// Foreach of the Markets - Test endpoints with parameters
expectedMarkets[0].markets.forEach(item => {
  test(`/api/bittrex/${item} contains valid data`, t => {
    request(app)
      .get(`/api/bittrex/${item}`)
      .expect("Content-Type", /json/)
      .expect(200)
      .end((err, res) => {
        const sampleData = res.body[0];

        t.same(sampleData.MarketName, item, `api bittrex data for ${item}`);
        t.error(err, "No error");
        t.end();
      });
  });
  test(`/api/bittrex/${item}?n=2 contains valid return amount`, t => {
    request(app)
      .get(`/api/bittrex/${item}?n=2`)
      .expect("Content-Type", /json/)
      .expect(200)
      .end((err, res) => {
        const sampleData = res.body;

        t.same(
          sampleData.length,
          2,
          `value return amount for query string ${item}`
        );
        t.error(err, "No error");
        t.end();
      });
  });
});

// Close the server
app.close();
