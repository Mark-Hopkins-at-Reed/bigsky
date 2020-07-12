import json
import random
from os import listdir
from os.path import isfile, join
import pandas as pd
import numpy as np
from bigsky.cky import cky_parse
from bigsky.datamanager import DataManager

class ForecastData:
    
    def __init__(self, df, normalizer_mode='normalize'):
        self.domain = dict()
        self.dtype = dict()
        if "OFFSET" not in df.keys():
            df.insert(0, "OFFSET", 1.0)
        self.df = df
        vartypes = dict()
        for var in self.df.keys():
            vartypes[var] = ForecastData.vartype(var)            
        self.mgr = DataManager(self.df, vartypes)
        self.mgr.set_column_normalizer(normalizer_mode)

        
    def select_response(self, column):
        return self.mgr.select_response(column)
        
    def select(self, columns):
        return self.mgr.select(columns)

    def remap_response(self, keyword):
        df = self.df.copy()
        count = 0
        for row in range(len(df)):
            if keyword in df.at[row, 'response'].lower():
                df.at[row, 'response'] = 1
                count += 1
            else:
                df.at[row, 'response'] = 0
        print('Mapped {}/{} to 1.'.format(count, len(df)))
        return ForecastData(df)
            
    def __len__(self):
        return len(self.df)

    @staticmethod
    def vartype(var):
        if var == 'response' or var == 'time' or var.startswith('precipType'): 
            result = 'categorical'
        else:
            result = 'numeric'
        return result

    @staticmethod
    def from_hourly_data(forecasts, ignore_fields = ['time', 'summary', 'icon',
                                                     'unix_time'],
                         normalizer_mode = 'normalize'):
        def safe_lookup(dictionary, key):
            if key in dictionary:
                return dictionary[key]
            else:
                return 0
        
        datas = harvest(forecasts, hourly_data_and_summary)
        results = []
        assert(len(datas) > 0)
        for (summary, data) in datas:
            result = {'response': summary}
            for feature in data[0]:
                result[feature] = [safe_lookup(datum, feature) for datum in data]
            results.append(result)            
        headings = ['response']
        for key in results[0]:
            if key not in headings and key not in ignore_fields:
                num_entries = len(results[0][key])
                for i in range(num_entries):
                    headings.append('{}__{}'.format(key, i))
        rows = []
        for result in results:
            row = []
            for heading in headings:
                if '__' in heading:
                    (feature, index) = heading.split('__')
                    try: 
                        row.append(result[feature][int(index)])
                    except KeyError:
                        row.append(0)
                else:
                    row.append(result[heading])
            rows.append(row)
        df = pd.DataFrame(np.array(rows), columns = headings)
        #remap_response(df, 'rain')
        df = df.astype({key: 'float64' for key in df.keys() 
                        if ForecastData.vartype(key) == 'numeric'}) 
        return ForecastData(df, normalizer_mode)

 
def read_forecast(filename):
    """Reads the forecast JSON into a dictionary."""
    with open(filename) as reader:
        forecast = json.load(reader)
    return forecast

def read_forecast_dir(directory, randomize=True):
    """
    Finds all files in the specified directory that correspond to
    well-formed JSON, and then makes a list of dictionaries corresponding
    to each JSON file.
    
    """
    onlyfiles = [f for f in listdir(directory) if isfile(join(directory, f))]
    if randomize:
        random.shuffle(onlyfiles)
    forecasts = []
    for file in onlyfiles:
        try:
            forecast = read_forecast(join(directory, file))
            forecasts.append(forecast)
        except Exception:
            print('WARNING(Not valid JSON): {}'.format(file))
    return forecasts
            
def hourly_data_and_summary(forecast):
    if 'hourly' in forecast and 'data' in forecast['hourly'] and 'summary' in forecast['hourly']:
        return (forecast['hourly']['summary'], forecast['hourly']['data'])
    else:
        return None

def minutely_summary(forecast):
    """Extracts the 'minutely' summary from a forecast dictionary."""
    if 'minutely' in forecast:
        return forecast['minutely']['summary']
    else:
        return None

def hourly_summary(forecast):
    """Extracts the 'hourly' summary from a forecast dictionary."""
    if 'hourly' in forecast and 'summary' in forecast['hourly']:
        return forecast['hourly']['summary']
    else:
        return None
    
def daily_summary(forecast):
    """Extracts the 'daily' summary from a forecast dictionary."""
    if 'daily' in forecast:
        return forecast['daily']['summary']
    else:
        return None

def harvest(forecasts, harvester):
    """
    Applies the provided function `harvester` to each forecast dictionary
    in a list of forecast dictionaries.
    
    """
    return [harvester(forecast) for forecast in forecasts]


def completeness(summaries, grammar):
    """
    from forecast import *
    from cfg import Cfg
    forecasts = read_forecast_dir('data/tmp')
    bgrammar = Cfg.from_file('weather.cfg').binarize()
    summaries = harvest(forecasts, hourly_summary)
    completeness(summaries, bgrammar)

    """
    parsed = 0
    nonempty = [s for s in summaries if s is not None]
    for summary in nonempty:
        summary = summary.lower()
        if cky_parse(summary, grammar):            
            parsed += 1
        else:
            print(summary)
    return parsed, len(nonempty)
    
