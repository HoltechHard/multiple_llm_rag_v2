function render_global_time_boxplot(containerId, model_names, observations, outliers) {
    Highcharts.chart(containerId, {
        chart: {
            type: 'boxplot'
        },

        title: {
            text: 'Global Analysis - Time Performance of LLM'
        },

        legend: {
            enabled: false
        },

        xAxis: {
            categories: model_names,
            title: {
                text: 'LLM Models'
            }
        },

        yAxis: {
            title: {
                text: 'Time (min)'
            }
        },

        series: [{
            name: 'Observations',
            data: observations,
            tooltip: {
                headerFormat: '<em>Model: {point.key}</em><br/>'
            },
            color: Highcharts.defaultOptions.colors[1]
        }, {
            name: 'Outliers',
            color: Highcharts.defaultOptions.colors[1],
            type: 'scatter',
            data: outliers,
            marker: {
                fillColor: 'white',
                lineWidth: 1,
                lineColor: Highcharts.defaultOptions.colors[1]
            },
            tooltip: {
                pointFormat: 'Value: {point.y}'
            }
        }]

    });
}

function render_detail_time_barplot(containerId, bar_keys, bar_series) {

    // dynamic height calculation
    const BASE_HEIGHT = 500;
    const EXTRA_PER_CATEGORY = 80;
    const CATEGORY_THRESHOLD = 4;
    const MAX_VISIBLE_HEIGHT = 1400;

    let calculatedHeight = BASE_HEIGHT;

    if (bar_keys.length > CATEGORY_THRESHOLD) {
        calculatedHeight +=
            (bar_keys.length - CATEGORY_THRESHOLD) * EXTRA_PER_CATEGORY;
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
            categories: bar_keys,
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
        series: bar_series
    });
}
