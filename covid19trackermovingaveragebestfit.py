# -*- coding: utf-8 -*-

#import os
#os.system("wget https://covid.ourworldindata.org/data/owid-covid-data.csv")

# required install scipy numpy pandas bokeh requests

import requests
url = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
myfile = requests.get(url)
open('owid-covid-data.csv', 'wb').write(myfile.content)

import pandas as pd
import numpy as np
from scipy.stats import norm

from bokeh.plotting import figure, output_file, show, save
from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models import Range1d
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.embed import file_html
from jinja2 import Template
import io
#output_notebook()

data = pd.read_csv('owid-covid-data.csv')

countries = list(data.location.unique())
countrySortFactor = [data[data.location == country].total_cases.values[-1] for country in countries]
numCountries = 19
topCountries = [b for a,b in sorted(zip(countrySortFactor,countries), reverse=True)[:numCountries]]

countrydict = {c:i for i,c in enumerate(topCountries)}

def fetchCountryData(countryName, cases = 100):
    countryData = data[data.location == countryName]
    countryData = countryData[countryData.total_cases >= cases]
    return countryData

def getNewCases(countryName):
    countryData = fetchCountryData(countryName)
    return list(abs(countryData.new_cases.values))

def getNewDeaths(countryName):
    countryData = fetchCountryData(countryName)
    return list(abs(countryData.new_deaths.values))

def getTotalCases(countryName):
    countryData = fetchCountryData(countryName)
    return list(abs(countryData.total_cases.values))

avgMortality = 0.7
avgDeathLag = 7
d = 0
avgDuration = 2 * d + 1

def getMovingAverage(newCases, d = d, avgDuration = avgDuration):
    #ma = [0] * d
    avg = 0
    ma = newCases[:d]
    ma.append(sum(newCases[:avgDuration])/avgDuration)

    for i in range(avgDuration , len(newCases)):
        if(newCases[i] == 0):
            avg += (avg - newCases[i - avgDuration])/avgDuration
        else:
            avg += (newCases[i] - newCases[i - avgDuration])/avgDuration
        ma.append(avg)
    for i in range(len(newCases) - d, len(newCases)):
        j = avgDuration
        avg = ( avg * j - newCases[i - d])/(j-1)
        ma.append(avg)
        j -= 1
    #ma = ma + newCases[len(newCases)-d:]
    return ma

def getMovingAverageChange(movingAverage, d = d, avgDuration = avgDuration):
    mac = [0]
    for i in range(1,len(movingAverage)):
        mac.append(movingAverage[i] - movingAverage[i-1])
    return mac

def goLeft(newCases, i, d = d, avgDuration = avgDuration):
    cl = 0
    lsum = 0
    for j in range(i-1, -1, -1):
        if(newCases[j] != 0):
            cl += 1
            lsum += newCases[j]
        if(cl == d):
            break
    return lsum, cl

def goRight(newCases, i, d = d, avgDuration = avgDuration):
    cr = 0
    rsum = 0
    for j in range(i+1, len(newCases)):
        if(newCases[j] != 0):
            cr += 1
            rsum += newCases[j]
        if(cr == d):
            break
    return rsum, cr

def getMovingAverageNew(newCases, d = d, avgDuration = avgDuration):
    ma = []
    for i,val in enumerate(newCases):
        c = int(val > 0)
        lsum, cl = goLeft(newCases, i, d, avgDuration)
        rsum, cr = goRight(newCases, i, d, avgDuration)
        divisor = c + cl + cr
        if divisor == 0:
            res = 0
        else:
            res = ( val + lsum + rsum ) / divisor
        ma.append(res)
    return ma

def getMaxIndex(l):
    maxv = 0
    maxi = 0
    for i,val in enumerate(l):
        if val > maxv:
            maxv = val
            maxi = i
    return maxi

def getMinIndex(l):
    minv = 0
    mini = 0
    for i,val in enumerate(l):
        if val < minv:
            minv = val
            mini = i
    return mini

def getFlatIndex(l):
    mini = getMinIndex(l)
    maxi = getMaxIndex(l)
    nl = [abs(ele) for ele in l[maxi:mini]]
    v = getMinIndex(nl)
    return maxi + v

def getError(pred, target):
    e = 0
    c = 0
    for p,t in zip(pred,target):
        if p != 0:
            e += abs(p - t)
            c += 1
    if c == 0: return 0
    return e/c

def getSigmaRegression(nc, mi, sendError = False):
    s = 1
    bests = 1
    beste = 10000000000
    while s < 30:
        r = list(range(0, mi + 1))
        bellcurve = norm.pdf(r, mi, s)
        bellcurve = [a * (nc[mi]/max(bellcurve)) for a in list(bellcurve)]
        error = getError(nc[:mi + 1], bellcurve)
        
        if error < beste:
            beste = error
            bests = s

        s += 0.05
    if sendError:
        return bests, int(beste)
    return bests

def getReverseSigmaRegression(nc, mi, sendError = False):
    if(len(nc)-mi < 10):
        if sendError:
            return "NA", 0
        return "NA"
    s = 1
    bests = 1
    beste = 10000000000
    while s < 30:
        r = list(range(mi, len(nc)))
        bellcurve = norm.pdf(r, mi, s)
        bellcurve = [a * (nc[mi]/max(bellcurve)) for a in list(bellcurve)]
        error = getError(nc[mi:], bellcurve)
        if error < beste:
            beste = error
            bests = s
        s += 0.05
    if sendError:
        return bests, int(beste)
    return bests

rsavg = 18

def getBestMovingAverageCurveFit(newCases):
    d = 3
    bestd = 0
    bests1 = 0
    bests2 = 0
    bestmi = 0
    bestma = []
    beste = 100000000000000000
    while d < 6:
        avgDuration = 2 * d + 1
        movingAverage = getMovingAverageNew(newCases, d, avgDuration)
        maxIndex = getMaxIndex(movingAverage)
        s1 = getSigmaRegression(movingAverage, maxIndex)
        s2 = getReverseSigmaRegression(movingAverage, maxIndex)
        sfactor = 2
        rsfactor = 4
        mafactor = 1
        if isinstance(s2, str):
            s2 = rsavg
            rsfactor = 0

        r = range(len(newCases))
        
        start = norm.pdf(r, maxIndex, s1)
        maxstart = max(start)
        start = start * (movingAverage[maxIndex]/maxstart)
        
        end = norm.pdf(r, maxIndex, s2)
        maxend = max(end)
        end = end * (movingAverage[maxIndex]/maxend)

        bellcurve = list(start)[:maxIndex] + list(end)[maxIndex:]

        error = (getError(bellcurve[:maxIndex], newCases[:maxIndex]) + getError(bellcurve[maxIndex:], newCases[maxIndex:]) * rsfactor + 
                    getError(movingAverage, newCases) * mafactor)
        #print(error, beste)

        if error < beste:
            beste = error
            bestd = d
            bests1 = s1
            bests2 = s2
            bestma = movingAverage
            bestmi = maxIndex
        d += 1
    return bestma, bestmi, bestd, bests1, bests2

def makeActualBellCurve(sigma, reverseSigma, maxMA, maxIndex):

    r = list(range(0, maxIndex*2 + 30))

    start = norm.pdf(r, maxIndex, sigma)
    maxstart = max(start)
    start = start * (maxMA/maxstart)

    end = norm.pdf(r, maxIndex, reverseSigma)
    maxend = max(end)
    end = end * (maxMA/maxend)

    bellcurve = list(start)[:maxIndex] + list(end)[maxIndex:]

    return bellcurve

tc = [getTotalCases(country) for country in topCountries]
nc = [getNewCases(country) for country in topCountries]
nd = [getNewDeaths(country) for country in topCountries]

processedVariables = [getBestMovingAverageCurveFit(newCases) for newCases in nc]

ma = [a for (a,b,c,d,e) in processedVariables]
meanpos = [b for (a,b,c,d,e) in processedVariables]
ds = [c for (a,b,c,d,e) in processedVariables]
sigmas = [d for (a,b,c,d,e) in processedVariables]
rawrss = [e for (a,b,c,d,e) in processedVariables]

rsclean = [rs for rs in rawrss if not isinstance(rs, str)]
rscleanavg = int(sum(rsclean)/len(rsclean))
reverseSigmas = []
for rs in rawrss:
    if isinstance(rs, str):
        reverseSigmas.append(rscleanavg)
    else:
        reverseSigmas.append(rs)
print(rscleanavg)

d = countrydict
bellcurves = [makeActualBellCurve(sigmas[d[country]], reverseSigmas[d[country]], ma[d[country]][meanpos[d[country]]], meanpos[d[country]])
                     for country in topCountries]

def getCountryDetails(country):
    countryIndex = countrydict[country]
    maxIndex = meanpos[countryIndex]

    r = list(range(0, maxIndex*2 + 30))

    newCases = nc[countryIndex]
    newDeaths = nd[countryIndex]
    movingAverage = ma[countryIndex]
    '''
    newCases = newCases + [0]*(len(r)-len(newCases))
    newDeaths = newDeaths + [0]*(len(r)-len(newDeaths))
    movingAverage = movingAverage + [0]*(len(r)-len(movingAverage))
    '''

    if(len(newCases) > len(r)):
        newCases = newCases[:len(r)]
    if(len(newDeaths) > len(r)):
        newDeaths = newDeaths[:len(r)]
    if(len(movingAverage) > len(r)):
        movingAverage = movingAverage[:len(r)]

    bellcurve = bellcurves[countryIndex]

    return r, newCases, newDeaths, movingAverage, bellcurve

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


def savehtmlbokeh(country):
    r, cases, deaths, movingAverage, bellcurve = getCountryDetails(country)

    #output_file(country + ".html")
    #sizing_mode = "scale_both"
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

    p.line(r, movingAverage, legend_label="Moving Average", line_width=2, line_color = 'blue')

    p.line(r, bellcurve, legend_label="Predicted Curve", line_width=2, line_color = 'red')

    #save(p)
    #show(p)

    script_bokeh, div_bokeh = components(p)
    resources_bokeh = CDN.render()

    # render everything together
    html = template.render(resources=resources_bokeh,
                        script=script_bokeh,
                        div=div_bokeh)

    out_file_path = "charts/" + country + ".html"
    with io.open(out_file_path, mode='w') as f:
        f.write(html)

for country in topCountries:
    savehtmlbokeh(country)