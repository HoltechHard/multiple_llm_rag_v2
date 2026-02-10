function render_global_time_boxplot(containerId) {
    Highcharts.chart(containerId, {
        chart: {
            type: 'boxplot'
        },

        title: {
            text: 'Global Analysis - Time'
        },

        legend: {
            enabled: false
        },

        xAxis: {
            categories: ['1', '2', '3', '4', '5'],
            title: {
                text: 'Experiment No.'
            }
        },

        yAxis: {
            title: {
                text: 'Observations'
            },
            plotLines: [{
                value: 932,
                color: 'red',
                width: 1,
                label: {
                    text: 'Theoretical mean: 932',
                    align: 'center',
                    style: {
                        color: 'gray'
                    }
                }
            }]
        },

        series: [{
            name: 'Observations',
            data: [
                [760, 801, 848, 895, 965],
                [733, 853, 939, 980, 1080],
                [714, 762, 817, 870, 918],
                [724, 802, 806, 871, 950],
                [834, 836, 864, 882, 910]
            ],
            tooltip: {
                headerFormat: '<em>Experiment No {point.key}</em><br/>'
            },
            color: Highcharts.defaultOptions.colors[1]
        }, {
            name: 'Outliers',
            color: Highcharts.defaultOptions.colors[1],
            type: 'scatter',
            data: [ // x, y positions where 0 is the first category
                [0, 644],
                [4, 718],
                [4, 951],
                [4, 969]
            ],
            marker: {
                fillColor: 'white',
                lineWidth: 1,
                lineColor: Highcharts.defaultOptions.colors[1]
            },
            tooltip: {
                pointFormat: 'Observation: {point.y}'
            }
        }]

    });
}

function render_detail_time_barplot(containerId, experiment_keys, experiment_series) {

    // dynamic height calculation
    const BASE_HEIGHT = 500;
    const EXTRA_PER_CATEGORY = 80;
    const CATEGORY_THRESHOLD = 4;
    const MAX_VISIBLE_HEIGHT = 1400;

    let calculatedHeight = BASE_HEIGHT;

    if (experiment_keys.length > CATEGORY_THRESHOLD) {
        calculatedHeight +=
            (experiment_keys.length - CATEGORY_THRESHOLD) * EXTRA_PER_CATEGORY;
    }

    // calculate the total height
    const container = document.getElementById(containerId);

    // control the size of the highchart
    if (calculatedHeight > MAX_VISIBLE_HEIGHT) {
        container.style.height = `${MAX_VISIBLE_HEIGHT}px`;
        container.style.overflowY = "auto";
    } else {
        container.style.height = `${calculatedHeight}px`;
        container.style.overflowY = "hidden";
    }

    Highcharts.chart(containerId, {
        chart: {
            type: 'bar',
            height: calculatedHeight
        },
        title: {
            text: 'Detailed Analysis - Time Performance of LLM Models by Experiment'
        },
        subtitle: {
            text: 'Source: Web - Chatbot'
        },
        xAxis: {
            categories: experiment_keys,
            title: {
                text: null
            },
            gridLineWidth: 1,
            lineWidth: 0
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Time (min)',
                align: 'high'
            },
            labels: {
                overflow: 'justify'
            },
            gridLineWidth: 0
        },
        tooltip: {
            valueSuffix: 'minutes'
        },
        plotOptions: {
            bar: {
                borderRadius: '50%',
                dataLabels: {
                    enabled: true
                },
                groupPadding: 0.1
            }
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'top',
            x: -40,
            y: 80,
            floating: true,
            borderWidth: 1,
            backgroundColor: 'var(--highcharts-background-color, #ffffff)',
            shadow: true
        },
        credits: {
            enabled: false
        },
        series: experiment_series
    });
}
