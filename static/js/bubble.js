var bubble_options = {
        chart: {
            type: 'packedbubble',
            height: '100%'
        },
        title: {
            text: 'Size of multi-user clusters'
        },
        tooltip: {
            useHTML: true,
            pointFormat: '</b> {point.value}'
        },
        plotOptions: {
            packedbubble: {
                minSize: '30%',
                maxSize: '120%',
                zMin: 0,
                zMax: 1000,
                layoutAlgorithm: {
                    splitSeries: false,
                    gravitationalConstant: 0.02
                },
                dataLabels: {
                    enabled: true,
                    format: '{point.name}',
                    filter: {
                        property: 'y',
                        operator: '>',
                        value: 250
                    },
                    style: {
                        color: 'black',
                        textOutline: 'none',
                        fontWeight: 'normal'
                    }
                }
            }
        },
        series: [{
            name: "",
            data: []
        }]
    }




var chart2 = Highcharts.chart('chart2', bubble_options);







