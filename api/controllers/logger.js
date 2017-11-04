const elasticsearch = require('elasticsearch');
const client = new elasticsearch.Client({
  host: 'elk:9200',
  log: 'trace'
});
