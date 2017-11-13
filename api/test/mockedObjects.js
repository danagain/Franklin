const mockedUUID = "e606d53c-8d70-11e3-94b5-425861b86ab6";

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

const mockedOrder = {
  MarketName: "BTC-ETH",
  OrderType: "LIMIT",
  Quantity: 1.00000,
  Rate: 0.542321,
  TimeInEffect: "IMMEDIATE_OR_CANCEL",
  ConditionType: "NONE",
  Target: 0
};

module.exports = {
    mockedOrder,
    mockedUUID,
    expectedMarkets
}
