const request = require("supertest");
const test = require("tape");
const app = require("../api");
const bodyParser = require("body-parser");

console.log(
  "Running Integration Tests, Ensure Docker-Compose env is up and running."
);

const mockedUUID = "e606d53c-8d70-11e3-94b5-425861b86ab6"

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
test(`/api/cancel/${mockedUUID} be valid`, t => {
  request(app)
    .post(`/api/cancel/${mockedUUID}`)
    .expect("Content-Type", /json/)
    .expect(200)
    .end((err, res) => {
      t.same(res.body, 'INVALID_ORDER', "Cancel UUID working as expected");
      t.end();
    });
});

// Foreach of the Markets - Test endpoints with parameters
expectedMarkets[0].markets.forEach(item => {

  // Getting the currency from the market string
  const currency = item.split('-')[1]

  test(`/api/balance/${currency} be 200`, t => {
    request(app)
      .get(`/api/balance/${currency}`)
      .expect("Content-Type", /json/)
      .expect(200)
      .end((err, res) => {
        t.error(err, "No error");
        t.end();
      });
  });
  test(`/api/orders/${item} be valid`, t => {
    request(app)
      .get(`/api/orders/${item}`)
      .expect("Content-Type", /json/)
      .expect(200)
      .end((err, res) => {
        t.same(res.body.success, true, "Get ALL open orders for a specific market");
        t.error(err, "No error");
        t.end();
      });
  });
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
