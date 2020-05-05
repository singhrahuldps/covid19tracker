import requests
import pandas as pd
import numpy as np
import os
import io
from datetime import datetime

url = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
filePath = 'owid-covid-data.csv'

def saveLoss(username, algoname, countries, trainloss, valloss, loss):
    df = pd.DataFrame()
    df['country'] = countries
    df['train_loss'] = trainloss
    df['valid_loss'] = valloss
    df['loss'] = loss

    df.to_csv("loss/" + username + "_" + algoname + ".csv")

def savePredictions(username, algoname, countries, preds):
    df = pd.DataFrame()
    df['country'] = countries
    df['predictions'] = list(preds)

    now = datetime.now() # current date and time
    dt = now.strftime("%d_%m_%Y")

    df.to_csv("preds/" + username + "_" + algoname + "_" + str(dt) + ".csv")

def createcountryselect(countryNames, countryCodes):
    script = "window.addEventListener('DOMContentLoaded', function(){\ninnerHTML = \""
    text = ""
    for country,code in zip(countryNames, countryCodes):
        text += "<option value = \'" + code  +"\'>" + country + "</option>"
    script += text + "\";\nvar countryselect = document.querySelector('#countryselect');\ncountryselect.innerHTML = innerHTML;\n});"
    out_file_path = "countryselect.js"
    with io.open(out_file_path, mode='w') as f:
        f.write(script)

class GetData():
    def __init__(self, numCountries = 19, delete_csv = False):
        myfile = requests.get(url)
        open('owid-covid-data.csv', 'wb').write(myfile.content)
        data = pd.read_csv(filePath)
        countries = list(data.location.unique())
        countrySortFactor = [data[data.location == country].total_cases.values[-1] for country in countries]
        topCountries = [b for a,b in sorted(zip(countrySortFactor,countries), reverse=True)[:numCountries]]
        self.tillDateTrainData = 10
        self.data = self.fetchData(data, topCountries)
        self.countries = topCountries
        self.countryCodes = [self.data[country].iso_code.unique()[0] for country in self.countries]
        self.countryCodes[0] = "WORLD"

        createcountryselect(self.countryCodes, self.countryCodes)

        self.tData = None
        self.tData = self.getTrainData()
        self.pData = None
        self.pData = self.getPresentData()

        if os.path.exists(filePath) and delete_csv:
            os.remove(filePath)

    def fetchCountryData(self, data, countryName, cases = 100):
        countryData = data[data.location == countryName]
        countryData = countryData[countryData.total_cases >= cases]
        return countryData

    def fetchData(self, data, countries):
        d = {}
        for country in countries:
            d[country] = self.fetchCountryData(data, country)
        return d

    def tillDateData(self, tillDaysFromEnd = 0):
        d = {}
        for country in self.data:
            d[country] = self.data[country][:len(self.data[country]) - tillDaysFromEnd]
        return d
    
    def getTrainData(self):
        if self.tData == None:
            self.tData = self.tillDateData(self.tillDateTrainData)
        return self.tData

    def getPresentData(self):
        if self.pData == None:
            self.pData = self.tillDateData()
        return self.pData

    def getError(self, pred, target):
        e = 0
        c = 0
        pred = list(pred)
        target = list(target)
        for p,t in zip(pred,target):
            if p != 0:
                e += abs(p - t)
                c += 1
        if c == 0: return 0
        return e/c

    def evaluate(self, preds, isTrain):
        trainloss = []
        valloss = []
        for i,country in enumerate(self.countries):
            length = len(self.pData[country])
            trainloss.append(0)
            valloss.append(0)
            if isTrain:
                trainloss[i] = self.getError(preds[i][:length - self.tillDateTrainData], self.tData[country].new_cases.values)
                valloss[i] = self.getError(preds[i][length - self.tillDateTrainData:length], self.pData[country].new_cases.values[length - self.tillDateTrainData:])
            else:
                trainloss[i] = self.getError(preds[i][:length], self.pData[country].new_cases.values)
        if not isTrain:
            return trainloss
        return trainloss, valloss

gd  = GetData()