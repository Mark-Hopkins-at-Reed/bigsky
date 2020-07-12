# Bigsky: Natural Language Generation for Weather Forecasts

## To locally install the package:

    pip install -e .

## To run all unit tests:

    python -m unittest

## To run a particular unit test module (e.g. test/test_bpe.py)

    python -m unittest test.test_bpe

## To train a model that distinguishes "rain" forecasts from "non-rain"

    python bigsky/train.py

Then in a Python interpreter:

    from bigsky.train import graph_results
    graph_results('data/results/rain.exp.json')
    
## To visualize the hour-by-hour data

In a Python interpreter:

    from bigsky.explore import *
    time_plot([humid, partly_cloudy], "cloudCover")


## To evaluate the completeness of a context-free grammar against a set of hourly summaries

In a Python interpreter:

    from bigsky.forecast import *
    from bigsky.cfg import Cfg
    forecasts = read_forecast_dir('data/1k')
    bgrammar = Cfg.from_file('data/cfgs/weather.cfg').binarize()
    summaries = harvest(forecasts, hourly_summary)
    completeness(summaries, bgrammar)
