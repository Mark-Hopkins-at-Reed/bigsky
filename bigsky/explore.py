from bigsky.forecast import read_forecast_dir
import numpy as np
import pandas as pd
import seaborn as sns

forecasts = read_forecast_dir('data/examples')

humid = forecasts[0]['hourly']
partly_cloudy = forecasts[2]['hourly']
rain = forecasts[3]['hourly']
mostly_cloudy = forecasts[8]['hourly']

def find_weathers(forecasts):
    for forecast in forecasts:
        print(forecast['hourly']['summary'])

def time_plot(forecasts, field):
    sns.set(style="whitegrid")
    forecast_datas = [forecast['data'] for forecast in forecasts]
    x_axis = list(range(len(forecast_datas[0])))
    headings = []
    field_values = []
    for forecast in forecasts:
        field_values.append([forecast['data'][i][field] for i in range(len(forecast['data']))])
        headings.append(forecast['summary'])
    field_values = np.array(field_values).transpose()
    data = pd.DataFrame(field_values, x_axis, columns=headings)
    sns.lineplot(data=data, palette="tab10", linewidth=2.5)