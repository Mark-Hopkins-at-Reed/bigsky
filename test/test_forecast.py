import unittest
import torch
from torch import tensor
from bigsky.forecast import read_forecast_dir, harvest, ForecastData
from bigsky.forecast import minutely_summary, hourly_summary, daily_summary

class TestForecast(unittest.TestCase):
    
    def setUp(self):
        self.forecasts = read_forecast_dir('data/examples', randomize=False)
    
    def test_harvest(self):
        result = sorted(harvest(self.forecasts, minutely_summary))
        expected =  ['Clear for the hour.',
                     'Partly cloudy for the hour.',
                     'Partly cloudy for the hour.',
                     'Partly cloudy for the hour.',
                     'Partly cloudy for the hour.',
                     'Partly cloudy for the hour.',
                     'Partly cloudy for the hour.',
                     'Partly cloudy for the hour.',
                     'Partly cloudy for the hour.',
                     'Rain for the hour.']
        assert result == expected
        result = sorted(harvest(self.forecasts, hourly_summary))
        expected =  ['Humid throughout the day.',
                     'Light rain tonight and tomorrow morning.',
                     'Mostly cloudy throughout the day.',
                     'Partly cloudy throughout the day.',
                     'Partly cloudy throughout the day.',
                     'Partly cloudy throughout the day.',
                     'Partly cloudy throughout the day.',
                     'Partly cloudy throughout the day.',                     
                     'Partly cloudy throughout the day.',
                     'Rain this morning and later this morning.']
        assert result == expected
        result = sorted(harvest(self.forecasts, daily_summary))
        expected =  ['Possible light rain on Saturday.',
                     'Possible light rain on Saturday.',
                     'Possible light rain on Saturday.',
                     'Possible light rain on Saturday.',
                     'Possible light rain on Saturday.',
                     'Possible light rain on Saturday.',
                     'Possible light rain on Saturday.',
                     'Rain today through Monday.',
                     'Rain today through Monday.',
                     'Rain today through Thursday.']
        assert result == expected
        
    def test_forecast_data(self):
        fdata = ForecastData.from_hourly_data(self.forecasts)
        fdata = fdata.remap_response('rain')
        response_vec, domain_size = fdata.select_response('response')
        expected = tensor([0, 0, 0, 1, 1, 0, 0, 0, 0, 0])                    
        assert torch.all(torch.eq(expected, response_vec))
        assert domain_size == 2        
        evidence_vec = fdata.select(['ozone__0', 'ozone__1'])
        evidence_vec = torch.round(10000 * evidence_vec) / 10000
        expected = tensor([ [0.2641, 0.2647],
                            [0.3223, 0.3227],
                            [0.3241, 0.3222],
                            [0.3042, 0.3026],
                            [0.3296, 0.3300],
                            [0.3223, 0.3227],
                            [0.3223, 0.3227],
                            [0.3223, 0.3227],
                            [0.3237, 0.3241],
                            [0.3223, 0.3227]])
        assert torch.all(torch.eq(expected, evidence_vec))
        

        
       
if __name__ == "__main__":
	unittest.main()
