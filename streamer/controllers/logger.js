SplunkLogger = require("splunk-logging").Logger;

const logger = () => {

  const config = {
    token: process.env.SPLUNKTOKEN,
    url: "https://splunk:8088"
  };

  const Logger = new SplunkLogger(config);

  const log = payload => {
    Logger.send(payload);
  };

  return {
    log: log
  };
};

module.exports = logger;
