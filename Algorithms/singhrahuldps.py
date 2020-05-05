import numpy as numpy
import pandas as pd
from scipy.stats import norm

classNames = ['BestFitBellCurve']
classDescription = ['This model is based on simply finding the best fitting asymmetric normal distribution on each country case data.']

def fetchCountryData(data, countryName):
    countryData = data[countryName]
    return countryData

def getNewCases(data, countryName):
    countryData = fetchCountryData(data, countryName)
    return list(abs(countryData.new_cases.values))

def getNewDeaths(data, countryName):
    countryData = fetchCountryData(data, countryName)
    return list(abs(countryData.new_deaths.values))

def getTotalCases(data, countryName):
    countryData = fetchCountryData(data, countryName)
    return list(abs(countryData.total_cases.values))

def getMovingAverage(newCases, d, avgDuration):
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

def getMovingAverageChange(movingAverage, d, avgDuration):
    mac = [0]
    for i in range(1,len(movingAverage)):
        mac.append(movingAverage[i] - movingAverage[i-1])
    return mac

def goLeft(newCases, i, d, avgDuration):
    cl = 0
    lsum = 0
    for j in range(i-1, -1, -1):
        if(newCases[j] != 0):
            cl += 1
            lsum += newCases[j]
        if(cl == d):
            break
    return lsum, cl

def goRight(newCases, i, d, avgDuration):
    cr = 0
    rsum = 0
    for j in range(i+1, len(newCases)):
        if(newCases[j] != 0):
            cr += 1
            rsum += newCases[j]
        if(cr == d):
            break
    return rsum, cr

def getMovingAverageNew(newCases, d, avgDuration):
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
    if(len(nc)-mi < 15):
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


class BestFitBellCurve():
    def __init__(self, countryNames, countryCodes):
        self.countryName = countryNames
        self.countryCodes = countryCodes

    def fit(self, data):
        tc = [getTotalCases(data, country) for country in self.countryName]
        nc = [getNewCases(data, country) for country in self.countryName]
        nd = [getNewDeaths(data, country) for country in self.countryName]

        processedVariables = [getBestMovingAverageCurveFit(newCases) for newCases in nc]

        self.ma = [a for (a,b,c,d,e) in processedVariables]
        self.meanpos = [b for (a,b,c,d,e) in processedVariables]
        self.ds = [c for (a,b,c,d,e) in processedVariables]
        self.sigmas = [d for (a,b,c,d,e) in processedVariables]
        rawrss = [e for (a,b,c,d,e) in processedVariables]

        rsclean = [rs for rs in rawrss if not isinstance(rs, str)]
        self.rscleanavg = int(sum(rsclean)/len(rsclean))
        self.reverseSigmas = []
        for rs in rawrss:
            if isinstance(rs, str):
                self.reverseSigmas.append(rscleanavg)
            else:
                self.reverseSigmas.append(rs)
    
    def predict(self):
        return [makeActualBellCurve(self.sigmas[i], self.reverseSigmas[i], self.ma[i][self.meanpos[i]], self.meanpos[i])
                     for i, country in enumerate(self.countryName)]
        
