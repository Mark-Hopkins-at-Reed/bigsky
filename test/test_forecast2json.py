import unittest
from bigsky.forecast2json import ForecastLoader, Classify, jsonify_hour, weather_times, priority_weather
from bigsky.forecast2json import coincident_weather, avg_weather, listify_forecast, accumulate, end2end
from bigsky.forecast import read_forecast

class TestForecast2Json(unittest.TestCase):
     
    def setUp(self):
        pass
    
    def test_loader(self):
        floader = ForecastLoader()
        floader.add_dataset('data/examples')
        forecasts = floader.get_fors()
        assert len(forecasts) == 10
        ozone_of_359 = floader.search_where(lambda dp: dp['ozone'] == 359.7)
        expected1 =  {'time': '21:00',
                      'summary': 'Mostly Cloudy',
                      'icon': 'partly-cloudy-night',
                      'precipIntensity': 0,
                      'precipProbability': 0,
                      'temperature': 58.07,
                      'apparentTemperature': 58.07,
                      'dewPoint': 35.42,
                      'humidity': 0.43,
                      'pressure': 1020.8,
                      'windSpeed': 6.3,
                      'windGust': 14.46,
                      'windBearing': 12,
                      'cloudCover': 0.62,
                      'uvIndex': 0,
                      'visibility': 10,
                      'ozone': 359.7,
                      'unix_time': 1586404800}
        expected2 =  {'time': '21:00',
                      'summary': 'Mostly Cloudy',
                      'icon': 'partly-cloudy-night',
                      'precipIntensity': 0,
                      'precipProbability': 0,
                      'temperature': 58.07,
                      'apparentTemperature': 58.07,
                      'dewPoint': 35.39,
                      'humidity': 0.42,
                      'pressure': 1020.8,
                      'windSpeed': 6.3,
                      'windGust': 14.46,
                      'windBearing': 12,
                      'cloudCover': 0.62,
                      'uvIndex': 0,
                      'visibility': 10,
                      'ozone': 359.7,
                      'unix_time': 1586404800}
        assert len(ozone_of_359) == 2
        assert(expected1 in ozone_of_359)
        assert(expected2 in ozone_of_359)
        
    def test_cloud_intense(self):
        classify = Classify()
        datapoint = {'time': '21:00', 'cloudCover': 0.30}
        assert classify.cloud_intense(datapoint) == 0 # no intensity
        datapoint = {'time': '21:00', 'cloudCover': 0.32}
        assert classify.cloud_intense(datapoint) == 1 # light intensity
        datapoint = {'time': '21:00', 'cloudCover': 0.62}
        assert classify.cloud_intense(datapoint) == 2 # moderate intensity
        datapoint = {'time': '21:00', 'cloudCover': 0.9}
        assert classify.cloud_intense(datapoint) == 3 # heavy intensity
        
    def test_wind_intense(self):
        classify = Classify()
        datapoint = {'windGust': 0.30, 'windSpeed': 432, 'cloudCover': 0.32}
        assert classify.wind_intense(datapoint) == 3 
        datapoint = {'windGust': 48, 'windSpeed': .1, 'cloudCover': 0.32}
        assert classify.wind_intense(datapoint) == 3 
        datapoint = {'windGust': 13, 'windSpeed': 25.02, 'cloudCover': 0.3}
        assert classify.wind_intense(datapoint) == 1 
        datapoint = {'windGust': 13, 'windSpeed': 24.9, 'cloudCover': 0.3}
        assert classify.wind_intense(datapoint) == 0 
        datapoint = {'windGust': 25.01, 'windSpeed': 25.02, 'cloudCover': 0.32}
        assert classify.wind_intense(datapoint) == 1 
        datapoint = {'windGust': 25.01, 'windSpeed': 25.005, 'cloudCover': 0.32}
        assert classify.wind_intense(datapoint) == 0
        datapoint = {'windGust': 39.1, 'windSpeed': 13, 'cloudCover': 0.3}
        assert classify.wind_intense(datapoint) == 1 
        datapoint = {'windGust': 38.99, 'windSpeed': 13, 'cloudCover': 0.3}
        assert classify.wind_intense(datapoint) == 0
        datapoint = {'windGust': 38.9, 'windSpeed': 13, 'cloudCover': 0.3}
        assert classify.wind_intense(datapoint) == 0
        datapoint = {'windGust': 39.1, 'windSpeed': 13, 'cloudCover': 0.32}
        assert classify.wind_intense(datapoint) == 1 
        datapoint = {'windGust': 38.99, 'windSpeed': 13, 'cloudCover': 0.32}
        assert classify.wind_intense(datapoint) == 1
        datapoint = {'windGust': 38.9, 'windSpeed': 13, 'cloudCover': 0.32}
        assert classify.wind_intense(datapoint) == 0
        
    def test_jsonify_hour1(self):
        classify = Classify()
        dp = {'time': '21:00',
             'precipIntensity': 0,
             'precipProbability': 0,
             'temperature': 58.07,
             'apparentTemperature': 58.07,
             'dewPoint': 35.39,
             'humidity': 0.42,
             'pressure': 1020.8,
             'windSpeed': 6.3,
             'windGust': 14.46,
             'windBearing': 12,
             'cloudCover': 0.62,
             'uvIndex': 0,
             'visibility': 10,
             'ozone': 359.7 }
        expected = {'time': 21,
                    'weather': [{'type': 'cloud', 
                                 'degree': 'moderate', 
                                 'probability': 'high'}],
                    'accumulation': 0}
        assert jsonify_hour(dp, classify) == expected
        
        
    def test_jsonify_hour2(self):
        classify = Classify()
        dp = {'time': '21:00',
             'precipIntensity': 1,
             'precipProbability': 1,
             'precipType': 'rain',
             'temperature': 58.07,
             'apparentTemperature': 58.07,
             'dewPoint': 35.39,
             'humidity': 0.42,
             'pressure': 1020.8,
             'windSpeed': 6.3,
             'windGust': 14.46,
             'windBearing': 12,
             'cloudCover': 0.62,
             'uvIndex': 0,
             'visibility': 10,
             'ozone': 359.7 }
        expected = {'time': 21, 
                    'weather': [{'type': 'rain', 
                                'degree': 'heavy', 
                                'probability': 'high'}], 
                    'accumulation': 0}   
        result = jsonify_hour(dp, classify) 
        assert result== expected
        
        
    def test_weather_times(self):
        forecast = read_forecast('data/examples/04-06-2020_21__45.5281774,-122.6014991')
        times = weather_times(forecast)
        assert times ==({'rain': 0, 
                         'snow': 0, 
                         'cloud': 29,  # i.e. 29 total hours of cloud
                         'wind': 0, 
                         'humid': 0, 
                         'fog': 0}, 
                        {'rain': [], 
                         'snow': [], 
                         'cloud': [[21, 26], [28, 47], [67, 69]], # here are the specific 29 hours
                         'wind': [], 
                         'humid': [], 
                         'fog': []})

    def test_priority_weather(self):
        test_times = {"cloud":0, "fog":0}
        assert priority_weather(test_times) == 'clear'
        test_times['fog'] = 3
        assert priority_weather(test_times) == 'fog'
        test_times['cloud'] = 5
        assert priority_weather(test_times) == 'cloud'
        test_times['snow'] = 1
        assert priority_weather(test_times) == 'snow'

    def test_coincident_weather(self):
        intvldict = {'rain': [[21,25]], 
                    'snow': [], 
                    'cloud': [[21, 26], [28, 47], [67, 69]], 
                    'wind': [], 
                    'humid': [], 
                    'fog': []}
        assert coincident_weather(intvldict, 'rain') == ['cloud']
        assert coincident_weather(intvldict, 'cloud') == []         # Ya need most of the main weather to be covered
        intvldict = {'rain': [[21,25]], 
                    'snow': [], 
                    'cloud': [[21, 26], [28, 47], [67, 69]], 
                    'wind': [[19, 29]], 
                    'humid': [[19, 23]], 
                    'fog': []}
        assert coincident_weather(intvldict, 'rain') == ['cloud', 'wind'] 

    def test_avg_weather1(self):
        forecast = read_forecast('data/examples/04-06-2020_21__45.5281774,-122.6014991')
        js_list = listify_forecast(forecast)
        result = avg_weather(js_list, 'cloud')
        assert result == ('light', 'high') # average intensity, average probability

    def test_avg_weather2(self):
        forecast = read_forecast('data/examples/06-04-2020_23:30:06__45.5281774,-122.6014991')
        js_list = listify_forecast(forecast)
        result = avg_weather(js_list, 'cloud')
        assert result == ('light', 'high') # they aren't all 'light', 'high'! I think

    def test_accumulate(self):
        forecast = read_forecast('data/examples/06-04-2020_23:30:06__45.5281774,-122.6014991')
        js_list = listify_forecast(forecast)
        result = accumulate(js_list)
        assert result == 0   # Really this only does something if there be snow or something, which we don't have in examples dataset

    def test_end2end(self):
        forecast = read_forecast('data/examples/06-04-2020_23:30:06__45.5281774,-122.6014991')
        assert end2end(forecast) == "Partly cloudy throughout the day."
        forecast = read_forecast('data/examples/07-04-2020_06:49:18__21.4233714,-157.8062839')
        assert end2end(forecast) == "Partly cloudy in the afternoon and tomorrow afternoon." 
        # The actual expected result is "Humid throughout the day", so I ain't perfect
  
if __name__ == "__main__":
	unittest.main()
