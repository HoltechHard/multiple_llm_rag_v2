from highcharts_core.chart import Chart
from highcharts_core.options import HighchartsOptions
from highcharts_core.options.series.bar import BarSeries

def population_bar_chart():
    options = HighchartsOptions()

    options.chart = {
        "type": "bar"
    }

    options.title = {
        "text": "Historic World Population by Region"
    }

    options.subtitle = {
        "text": (
            'Source: <a href="https://en.wikipedia.org/wiki/'
            'List_of_continents_and_continental_subregions_by_population" '
            'target="_blank">Wikipedia.org</a>'
        )
    }

    options.xAxis = {
        "categories": ["Africa", "America", "Asia", "Europe"],
        "gridLineWidth": 1,
        "lineWidth": 0
    }

    options.yAxis = {
        "min": 0,
        "title": {
            "text": "Population (millions)",
            "align": "high"
        },
        "labels": {
            "overflow": "justify"
        },
        "gridLineWidth": 0
    }

    options.tooltip = {
        "valueSuffix": " millions"
    }

    options.plotOptions = {
        "bar": {
            "borderRadius": "50%",
            "dataLabels": {
                "enabled": True
            },
            "groupPadding": 0.1
        }
    }

    options.legend = {
        "layout": "vertical",
        "align": "right",
        "verticalAlign": "top",
        "x": -40,
        "y": 80,
        "floating": True,
        "borderWidth": 1,
        "backgroundColor":"var(--highcharts-background-color, #ffffff)",
        "shadow": True
    }

    options.credits = {
        "enabled": False
    }

    options.series = [{
        "name": "Year 1990",
        "data": [632, 727, 3202, 721]
    }, {
        "name": 'Year 2000',
        "data": [814, 841, 3714, 726]
    }, {
        "name": 'Year 2021',
        "data": [1393, 1031, 4695, 745]
    }]        
    
    # Return the options JSON directly
    json_output = options.to_json()

    if isinstance(json_output, bytes):
       return json_output.decode('utf-8')
    
    return json_output
