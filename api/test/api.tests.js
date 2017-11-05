const request = require("supertest");
const test = require("tape");
const app = require("../api");

const expectedCoins = [
    { coins: ["BTC-ETH", "BTC-NEO", "BTC-LTC", "USDT-BTC"] }
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

expectedCoins[0].coins.forEach((item) => {
    test(`/api/bittrex/${item} contains valid data`, t => {
        request(app)
          .get(`/api/bittrex/${item}`)
          .expect("Content-Type", /json/)
          .expect(200)
          .end((err, res) => {
            const sampleData = res.body[0]

            t.same(sampleData.MarketName, item, `api bittrex data for ${item}`);
            t.error(err, "No error");
            t.end();
          });
      });
      test(`/api/buy/${item} returns valid 200 response`, t => {
        request(app)
          .post(`/api/buy/${item}`)
          .expect(200)
          .end((err, res) => {
            t.error(err, "No error");
            t.end();
          });
      });
      test(`/api/sell/${item} returns valid 200 response`, t => {
        request(app)
          .post(`/api/sell/${item}`)
          .expect(200)
          .end((err, res) => {
            t.error(err, "No error");
            t.end();
          });
      });

})

// Close the server
app.close();
