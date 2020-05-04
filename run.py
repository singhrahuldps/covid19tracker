import DataHandler
import Algorithms
import ChartHandler
import argparse

NO_ARGUMENT = "__none__"

def runAlgo(username, algoName, algoClass, countriesData):
    algo = algoClass(countriesData.countries, countriesData.countryCodes)

    algo.fit(countriesData.getTrainData())
    trainPred = algo.predict()
    trainloss, valloss = countriesData.evaluate(trainPred, True)

    algo.fit(countriesData.getPresentData())
    pred = algo.predict()
    loss = countriesData.evaluate(pred, False)
    print(sum(loss)/len(loss))

    ChartHandler.makePlot(username, algoName, countriesData.countries, countriesData.countryCodes, 
            countriesData.getPresentData(), pred)
            
    DataHandler.saveLoss(username, algoName, countriesData.countries, trainloss, valloss, loss)
    DataHandler.savePredictions(username, algoName, countriesData.countries, pred)

def main(username, algos):

    userClasses = dict([(name, cls) for name, cls in Algorithms.__dict__.items()
                        if name in Algorithms.usernames])

    countriesData = DataHandler.GetData()
    
    if username == NO_ARGUMENT:
        for username in userClasses:
            usermod = userClasses[username]
            algomod = dict([(name, cls) for name, cls in usermod.__dict__.items() if name in usermod.classNames])
            for algo in algomod:
                runAlgo(username, algo, algomod[algo], countriesData)
    elif username in userClasses:
        usermod = userClasses[username]
        algomod = dict([(name, cls) for name, cls in usermod.__dict__.items() if name in usermod.classNames])
        if algos[0] == NO_ARGUMENT:
            for algo in algomod:
                runAlgo(username, algo, algomod[algo], countriesData)
        else:
            for algo in algos:
                if algo in algomod:
                    runAlgo(username, algo, algomod[algo], countriesData)
                else:
                    print(algo + " algorithm not found!")
    else:
        print(username + " module not found!")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create Covid19 prediction graphs for one or all Algorithms")
    parser.add_argument('-u', nargs=1, default=NO_ARGUMENT, type = str, help="Your username")
    parser.add_argument('-a', nargs='+', default=NO_ARGUMENT, help="List of algorithms")
    args = parser.parse_args()

    username = args.u
    algos = args.a
    if type(username) == list:
        username = username[0]
    if type(algos) == str:
        algos = [algos]

    main(username, algos)

