import unittest
from forecast import read_forecast_dir, harvest
from forecast import minutely_summary, hourly_summary, daily_summary


class TestWordnet(unittest.TestCase):
    
    def setUp(self):
        self.forecasts = read_forecast_dir('data/examples')
    
    def test_harvest(self):
        result = harvest(self.forecasts, minutely_summary)
        expected =  ['Clear for the hour.',
                     'Partly cloudy for the hour.',
                     'Partly cloudy for the hour.',
                     'Rain for the hour.',
                     'Partly cloudy for the hour.',
                     'Partly cloudy for the hour.',
                     'Partly cloudy for the hour.',
                     'Partly cloudy for the hour.',
                     'Partly cloudy for the hour.',
                     'Partly cloudy for the hour.']
        assert result == expected
        result = harvest(self.forecasts, hourly_summary)
        expected =  ['Humid throughout the day.',
                     'Partly cloudy throughout the day.',
                     'Partly cloudy throughout the day.',
                     'Rain this morning and later this morning.',
                     'Light rain tonight and tomorrow morning.',
                     'Partly cloudy throughout the day.',
                     'Partly cloudy throughout the day.',
                     'Partly cloudy throughout the day.',
                     'Mostly cloudy throughout the day.',
                     'Partly cloudy throughout the day.']
        assert result == expected
        result = harvest(self.forecasts, daily_summary)
        expected =  ['Rain today through Thursday.',
                     'Possible light rain on Saturday.',
                     'Possible light rain on Saturday.',
                     'Rain today through Monday.',
                     'Rain today through Monday.',
                     'Possible light rain on Saturday.',
                     'Possible light rain on Saturday.',
                     'Possible light rain on Saturday.',
                     'Possible light rain on Saturday.',
                     'Possible light rain on Saturday.']
        assert result == expected
        

        
       
if __name__ == "__main__":
	unittest.main()
