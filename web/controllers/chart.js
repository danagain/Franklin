
// Load Highcharts
const Highcharts = require('js/highstock');
const request = require('request')

const seriesOptions = [],
seriesCounter = 0,
names = ["BTC-ETH", "USDT-BTC", "BTC-NEO", "BTC-LTC"];

// This is how a module is loaded. Pass in Highcharts as a parameter.
require('js/exporting')(Highcharts);

// Generate the chart
const chart = Highcharts.stockChart('container', {

        rangeSelector: {
            selected: 4
        },

        yAxis: {
            labels: {
                formatter: function () {
                    return (this.value > 0 ? ' + ' : '') + this.value + '%';
                }
            },
            plotLines: [{
                value: 0,
                width: 2,
                color: 'silver'
            }]
        },

        plotOptions: {
            series: {
                compare: 'percent',
                showInNavigator: true
            }
        },

        tooltip: {
            pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.change}%)<br/>',
            valueDecimals: 2,
            split: true
        },

        series: seriesOptions
    });


names.map((item) => {
    request.get('http://web-api:3000/api/info/' + name.toLowerCase(), (req, res, err) => {
        if (err) console.log(data)
        console.log(data)
        seriesOptions = {
            name: data.name,
            data: data.data
        };
        seriesCounter += 1;

        if (seriesCounter === names.length) {
            createChart();
        }
    })
})

