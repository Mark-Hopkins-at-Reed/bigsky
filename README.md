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


## To translate a forecast into natural language with rules

In a Python interpreter:

    from bigsky.forecast import read_forecast
    from bigsky.forecast2json import end2end
    forecast = read_forecast('data/examples/04-06-2020_23:28:41__45.5281774,-122.6014991') # For example
    sentence = end2end(forecast)


## To compare a forecast's given summary with the one predicted

In a Python interpreter:

    from bigsky.forecast import read_forecast
    from bigsky.forecast2json import compare_end2end
    forecast = read_forecast('data/examples/04-06-2020_23:28:41__45.5281774,-122.6014991') # For example
    are_equal, prediction, gold = compare_end2end(forecast)


## To evaluate BLEU score of rule-based system

    python bleu.py

Configure the directories to test in data/datapaths.py