const request = require("supertest");
const test = require("tape");
const app = require("../api");
const mocks = require("./mockedObjects");

console.log(
  "Running Integration Tests, Ensure Docker-Compose env is up and running."
);

test("/ should 404", t => {
  request(app)
    .get("/")
    .expect(404)
    .end((err, res) => {
      t.end();
    });
});
test("/api should 404", t => {
  request(app)
    .get("/api")
    .expect(404)
    .end((err, res) => {
      t.end();
    });
});
test("/api/markets be valid", t => {
  request(app)
    .get("/api/markets")
    .expect("Content-Type", /json/)
    .expect(200)
    .end((err, res) => {
      t.same(res.body, mocks.expectedMarkets, "Markets as expected");
      t.end();
    });
});
test(`/api/cancel/${mocks.mockedUUID} be valid`, t => {
  request(app)
    .post(`/api/cancel/${mocks.mockedUUID}`)
    .expect("Content-Type", /json/)
    .expect(200)
    .end((err, res) => {
      t.same(res.body, "INVALID_ORDER", "Cancel UUID working as expected");
      t.end();
    });
});

test(`/api/buy/BTC-ETH return INSUFFIENT FUNDS`, t => {
  request(app)
    .post("/api/buy/BTC-ETH")
    .send(mocks.mockedOrder)
    .expect("Content-Type", /json/)
    .expect(200)
    .end((err, res) => {
      t.same(res.body, "INSUFFICIENT_FUNDS", "INSUFFIENT FUNDS for BUY Orders");
      t.end();
    });
});

test(`/api/sell/BTC-ETH return INSUFFIENT FUNDS`, t => {
  request(app)
    .post("/api/sell/BTC-ETH")
    .send(mocks.mockedOrder)
    .expect("Content-Type", /json/)
    .expect(200)
    .end((err, res) => {
      t.same(res.body, "INSUFFICIENT_FUNDS", "INSUFFIENT FUNDS for SELL Orders");
      t.end();
    });
});

// Foreach of the Markets - Test endpoints with parameters
mocks.expectedMarkets[0].markets.forEach(item => {
  // Getting the currency from the market string
  const currency = item.split("-")[1];

  test(`/api/balance/${currency} be 200`, t => {
    request(app)
      .get(`/api/balance/${currency}`)
      .expect("Content-Type", /json/)
      .expect(200)
      .end((err, res) => {
        t.same(
          res.body.success,
          true,
          "Get Balance for all coins"
        );
        t.end();
      });
  });
  test(`/api/orders/${item} be valid`, t => {
    request(app)
      .get(`/api/orders/${item}`)
      .expect("Content-Type", /json/)
      .expect(200)
      .end((err, res) => {
        t.same(
          res.body.success,
          true,
          "Get ALL open orders for a specific market"
        );

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
        t.end();
      });
  });
});

// Close the server
app.close();
