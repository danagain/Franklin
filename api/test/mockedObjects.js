const mockedUUID = "e606d53c-8d70-11e3-94b5-425861b86ab6";

const expectedMarkets = [
  {
    markets: [
      "BTC-LSK",
      "BTC-ETH",
      "BTC-STORJ",
      "BTC-NEO",
      "BTC-QTUM",
      "BTC-ZEC",
      "BTC-OMG",
      "BTC-EMC2",
      "BTC-LTC",
      "BTC-XRP",
      "BTC-VTC",
      "BTC-ADA",
      "BTC-BAY",
      "BTC-POWR",
      "BTC-DASH",
      "BTC-XLM",
      "BTC-OK",
      "BTC-STRAT"
    ]
  }
];

const mockedOrder = {
  MarketName: "BTC-ETH",
  OrderType: "LIMIT",
  Quantity: 1.0,
  Rate: 0.542321,
  TimeInEffect: "IMMEDIATE_OR_CANCEL",
  ConditionType: "NONE",
  Target: 0
};

module.exports = {
  mockedOrder,
  mockedUUID,
  expectedMarkets
};
