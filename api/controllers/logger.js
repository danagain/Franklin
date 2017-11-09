SplunkLogger = require("splunk-logging").Logger;

let splunkEndpoint;

if (process.env.APP_ENV) {
  splunkEndpoint = "https://splunk:8088";
} else {
  splunkEndpoint = "https://localhost:8088";
}

const logger = () => {
  const config = {
    token: process.env.SPLUNKTOKEN,
    url: splunkEndpoint
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
