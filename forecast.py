import json
from os import listdir
from os.path import isfile, join
from cky import cky_parse
import pandas as pd
import numpy as np

class ForecastData:
    
    def __init__(self, df, buckets = bucket_forest_types):
        self.domain = dict()
        self.dtype = dict()
        df.insert(0, "OFFSET", 1.0)
        df["FORTYPCD"] = [buckets(x) for x in df["FORTYPCD"]]
        df = df.loc[df['FORTYPCD'] >= 0]
        self.df = df
        
        categorical_vars = ["FORTYPCD", "forgrp"]
        numeric_vars = ['OFFSET', 'ASPECT', 'SLOPE', 'LAT_PUBLIC', 
                        'LON_PUBLIC', 'ELEV_PUBLIC', "demLF","nlcd11",
                        "forprob", "evtLF","forbio"]
        vartypes = {v: 'categorical' for v in categorical_vars}
        vartypes.update({v: 'numeric' for v in numeric_vars})
        self.mgr = DataManager(self.df, vartypes)
        

    def select_response(self, column):
        return self.mgr.select_response(column)
        
    def select(self, columns):
        return self.mgr.select(columns)
            
    def __len__(self):
        return len(self.df)

    def latitude_buckets(self, interval):
        buckets = defaultdict(list)
        for row_index in range(len(self.df)):
            row = self.df.iloc[row_index]
            latitude = row['LAT_PUBLIC']
            buckets[int(latitude // interval)].append(row_index)
            buckets[int(latitude // interval + interval)].append(row_index)
        return dict(buckets)

    def lat_long_buckets(self, interval):
        lat_buckets = self.latitude_buckets(interval)
        buckets = defaultdict(list)
        for bucket in lat_buckets:
            for row_index in lat_buckets[bucket]:
                row = self.df.iloc[row_index]
                longitude = row['LON_PUBLIC']
                buckets[(bucket, int(longitude // interval))].append(row_index)
                buckets[(bucket, int(longitude // interval + interval))].append(row_index)
        return dict(buckets)

    def all_pairwise_distances(self):
        dists = dict()
        for row1 in range(len(self.df)):
            for row2 in range(row1 + 1, len(self.df)):
                dists[(row1, row2)] = self.distance(self.df.iloc[row1], self.df.iloc[row2])
        return dists
           
    def distance(self, row1, row2):
        squared_long_diff = (row1['LON_PUBLIC'] - row2['LON_PUBLIC']) ** 2
        squared_lat_diff = (row1['LAT_PUBLIC'] - row2['LAT_PUBLIC']) ** 2
        return (squared_long_diff + squared_lat_diff) ** 0.5
        

def read_forecast(filename):
    """Reads the forecast JSON into a dictionary."""
    with open(filename) as reader:
        forecast = json.load(reader)
    return forecast

def read_forecast_dir(directory):
    """
    Finds all files in the specified directory that correspond to
    well-formed JSON, and then makes a list of dictionaries corresponding
    to each JSON file.
    
    """
    onlyfiles = [f for f in listdir(directory) if isfile(join(directory, f))]
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

def compile_hourly_data(forecasts, ignore_fields = ['time', 'summary', 'icon',
                                                    'unix_time']):
    def safe_lookup(dictionary, key):
        if key in dictionary:
            return dictionary[key]
        else:
            return None
    
    datas = harvest(forecasts, hourly_data_and_summary)
    results = []
    assert(len(datas) > 0)
    for (summary, data) in datas:
        result = {'response': summary}
        for feature in data[0]:
            result[feature] = [safe_lookup(datum, feature) for datum in data]
        results.append(result)            
    headings = ['response', 'time']
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
                    row.append(None)
            else:
                row.append(result[heading])
        rows.append(row)
    df = pd.DataFrame(np.array(rows), columns = headings)
    return df

def remap_response(df, keyword):
    for row in range(len(df)):
        if keyword in df.at[row, 'response'].lower():
            df.at[row, 'response'] = 1
        else:
            df.at[row, 'response'] = 0


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
    
