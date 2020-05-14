import json
from os import listdir
from os.path import isfile, join

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
            

def minutely_summary(forecast):
    """Extracts the 'minutely' summary from a forecast dictionary."""
    if 'minutely' in forecast:
        return forecast['minutely']['summary']
    else:
        return None

def hourly_summary(forecast):
    """Extracts the 'hourly' summary from a forecast dictionary."""
    if 'hourly' in forecast:
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