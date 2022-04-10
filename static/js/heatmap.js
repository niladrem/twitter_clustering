var heat_options = {

    chart: {
        type: 'heatmap',
        marginTop: 40,
        marginBottom: 80,
        plotBorderWidth: 1
    },


    title: {
        text: 'Visualisation of user distance matrix as heatmap'
    },

    xAxis: {
        labels: {
            enabled: false
        }
    },


    yAxis: {
        labels: {
            enabled: false
        }
    },

    
    colorAxis: {
        min: 0,
        minColor: '#FFFFFF',
        maxColor: Highcharts.getOptions().colors[0]
    },

    legend: {
        align: 'right',
        layout: 'vertical',
        margin: 0,
        verticalAlign: 'top',
        y: 25,
        symbolHeight: 280
    },

    tooltip: {
        formatter: function () {
            return f();
        }
    },

    series: [{
        name: 'Visualisation of user distance matrix as heatmap',
        borderWidth: 1,
        data: [],
        dataLabels: {
            enabled: true,
            color: '#000000'
        }
    }]

    
}



var chart1 = Highcharts.chart('chart1', heat_options);