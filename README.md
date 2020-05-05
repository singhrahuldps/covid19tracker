# Covid-19 Tracker

Create your own algorithms which fit on the covid-19 Dataset and send a Pull Request. Accepted code algorithms will be published to the website [singhrahuldps.github.io/covid19tracker](https://singhrahuldps.github.io/covid19tracker).

## Add your own algorithm

Add your module to the Algorithm folder and add the py file name to the __init__.py file. Make sure to keep the file name to be your GitHub username. Also add the import statement for your module in the __init__.py.

Add a classNames list to your module which contains the names of your algorithm classes.

Your class must have the following methods:

```python
class MyAlgorithm():
    def __init__(self, countryNames, countryCodes):
        #  countryNames, countryCodes are list of str
        # statements

    def fit(self, data):
        # data is a dictionary with country names as the key
        # and corresponding pandas dataFrame as value
        # Fit or train your algorithm on the data
        # statements

    def predict(self):
        # statements
        # returns list
        return your_new_cases_prediction_for_each_country_in_the_order_of_country_names
```

Your module must have your github username as its name. For example: **Algorithms/singhrahuldps.py**. It should have the following structure:

```python
# your imports
classNames = ['Algo1', 'Algo2']
classDescription = ['Algo1 Description', 'Algo2 Description']

class Algo1():
    def __init__(self, countryNames, countryCodes):
        #statements

    def fit(self, data):
        # statements

    def predict(self):
        # statements
        return predictions

class Algo2():
    def __init__(self, countryNames, countryCodes):
        #statements

    def fit(self, data):
        # statements

    def predict(self):
        # statements
        return predictions
```

View your changes on **index.html** by running the following command in terminal

```bash
python run.py
```

Ifyou want to only create output files for your own algorithm, use the following arguments

```bash
python run.py -u yourGithubUsername -a YourAlgorithm1, YourAlgorithm2, YourAlgorithm3
```

## Dependencies

```bash
pip install numpy scipy pandas requests pathlib bokeh
```

Mention additional dependencies for your class in the pull request.
