"""Criteria: Total Area %, Number of days up or down."""
"""
Ascending or descending overall and head
"""
import pandas as pd

def apply_search_criteria(data_stocks: list, criteria: str):
    print(criteria)
    output = dict()
    keys = list(data_stocks.keys())
    for k in keys:
        metrics = calculate_metrics(data_stocks[k])
        if(eval_criteria(criteria, metrics)):
            output[k] = data_stocks[k]
            print(metrics)
    return output

def eval_criteria(criteria: str, metrics: dict):
    tok = criteria.split()
    final = str()
    for t in tok:
        if(t in metrics):
            val = metrics[t]
            if(type(val) is str):
                final+= '\"' + val + '\"'
            else:
                final += str(val)
        else:
            final += t
        final += ' '
    return eval(final)

def calculate_metrics(data):
    #dictionary of metrics. These are what we decide stocks based on.
    m = dict()
    m['symbol'] = data[0]['symbol']
    m['sector'] = data[1]['sector']
    m['avgVolume'] = get_average(data[2]['volume'])
    m['avgVolumeDelta'] = get_average(get_delta(data[2]['volume']))
    return m

def get_average(data):
    count = data.size
    total = 0
    for val in data:
        total += val
    total /= count
    return total

def get_delta(data):
    deltas = list()
    prev = 0
    for val in data:
        deltas.append(val-prev)
        prev = val
    deltas.pop(0)
    return pd.Series(deltas)
