const request = require("supertest");
const test = require("tape");
const app = require("../api");

console.log(
  "Running Integration Tests, Ensure Docker-Compose env is up and running."
);

const expectedCoins = [
  {
    coins: [
      "BTC-ETH",
      "BTC-NEO",
      "BTC-LTC",
      "BTC-BCC",
      "BTC-VTC",
      "BTC-OMG",
      "BTC-DASH",
      "BTC-XRP",
      "BTC-TRST",
      "BTC-ARK",
      "BTC-XVG",
      "BTC-EMC2",
      "BTC-XVC",
      "BTC-VOX"
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
test("/api/coins be valid", t => {
  request(app)
    .get("/api/coins")
    .expect("Content-Type", /json/)
    .expect(200)
    .end((err, res) => {
      t.same(res.body, expectedCoins, "Coins as expected");
      t.error(err, "No error");
      t.end();
    });
});

// Foreach of the Coins - Test endpoints with parameters
expectedCoins[0].coins.forEach(item => {
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
