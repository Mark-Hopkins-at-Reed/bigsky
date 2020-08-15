import unittest
from bigsky.forecast2json import ForecastLoader, Classify, jsonify_hour, weather_times
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
        
  
if __name__ == "__main__":
	unittest.main()
