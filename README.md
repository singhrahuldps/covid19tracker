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

## Dependencies

```bash
pip install numpy scipy pandas requests bokeh
```
