const seriesOptions = [],
seriesCounter = 0,
names = ["BTC-ETH", "USDT-BTC", "BTC-NEO", "BTC-LTC"];

/**
* Create the chart when all data is loaded
* @returns {undefined}
*/
// UTC TIMESTAMP followed by value
// [1506988800000,957.79],
function createChart() {

Highcharts.stockChart('container', {

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
}

$.each(names, function(i, name) {

$.getJSON('http://localhost:3000/api/last/' + name.toLowerCase() + '-c.json&callback=?',  function(data) {
    console.log('data')
    console.log(data)
    seriesOptions[i] = {
        name: name,
        data: data
    };

    seriesCounter += 1;

    if (seriesCounter === names.length) {
        createChart();
    }
});
});
