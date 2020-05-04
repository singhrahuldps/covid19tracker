import bokeh
import numpy as np
import os
from pathlib import Path
from bokeh.plotting import figure, output_file, show, save
from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models import Range1d
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.embed import file_html
from jinja2 import Template
import io

template = Template(
    '''<!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <title>Overview</title>
                {{ resources }}
                {{ script }}
                <style>
                    .embed-wrapper {
                        display: flex;
                        justify-content: space-evenly;
                    }
                </style>
            </head>
            <body  style="width: min-content ;margin: 0 auto;">
                <div>
                    {{ table }}
                </div>                    
                <div class="embed-wrapper">
                    {{ div }}
                </div>
            </body>
        </html>
        ''')

def makeData(data, pred):
    cases = data['new_cases'].values
    deaths = data['new_deaths'].values
    
    r = list(range(0, max(len(cases), len(deaths), len(pred))))

    return r, cases, deaths, pred

def savePlot(path, filename, country, r, cases, deaths, curve):
    p = figure(plot_height=350, plot_width=500, title=country, x_axis_label='Days (since 100 cases)', y_axis_label='',
            toolbar_location='right', tools = "hover",
            y_range=Range1d(0, int(1.05*max(cases)), bounds="auto"), x_range=Range1d(0, int(1.05*max(r)), bounds="auto"))

    hover = p.select(dict(type=HoverTool))
    hover.tooltips = [
            ('People', '$y'),
            ('Days (since 100 cases)' , '$index')
            ]

    p.vbar(r, top=cases, width=0.9, legend_label="Daily Cases", color = 'orange')

    p.vbar(r, top=deaths, width=0.9, legend_label="Daily Deaths", color = 'red', )

    p.line(r, curve, legend_label="Predicted Curve", line_width=2, line_color = 'red')

    script_bokeh, div_bokeh = components(p)
    resources_bokeh = CDN.render()

    html = template.render(resources=resources_bokeh,
                        script=script_bokeh,
                        div=div_bokeh)

    out_file_path = path + filename
    with io.open(out_file_path, mode='w') as f:
        f.write(html)

def makePlot(username, algoname, countryList, countryCodes, data, pred):
    path = "charts/" + username + "/" + algoname + "/"
    Path(path).mkdir(parents=True, exist_ok=True)
    for i, (country,code) in enumerate(zip(countryList, countryCodes)):
        r, cases, deaths, curve = makeData(data[country], pred[i])
        savePlot(str(path), code + ".html", country, r, cases, deaths, curve)
