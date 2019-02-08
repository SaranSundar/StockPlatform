import os
import pickle
import random
import threading
import time
from timeit import default_timer as timer

import plotly
import plotly.graph_objs as go
import plotly.offline as py
from flask import Flask, jsonify
from flask_cors import CORS
from iexfinance import get_available_symbols
from iexfinance.stocks import Stock, get_historical_data

app = Flask(__name__)
CORS(app, supports_credentials=True, resources=r'/api/*')
app.config.update(
    DEBUG=True,
    JSON_SORT_KEYS=False,
    JSONIFY_PRETTYPRINT_REGULAR=False
)


@app.route("/api/v1/name/")
def get_name():
    return jsonify(random.choice(["Saran", "Xavier", "John", "Alton"]))


# Used for Plotly API, can see graphs on there website but I use offline mode.
plotly.tools.set_credentials_file(username='SS_Zeklord', api_key='Z1JPugSh0SQav7gFwBRk')
# Search amount should always be divisible by max threads
filters = {'symbol_types': ['cs', 'etf'], 'cost_options': {'min': 11, 'max': 40}, 'search_amount': 10,
           'min_per_thread': 4,
           'file_name': 'data_stocks.bin', 'max_threads': 25, 'search_criteria': ['+', '5%', '3days'], 'output': 'json'}

"""
Input is what kind of symbols you want, cs is common stock, etf is exchange traded funds.
There are more options that we dont need for now
"""


def get_filtered_symbols(symbol_types: list = None) -> dict:
    if symbol_types is None:
        symbol_types = ['cs', 'etf']
    supported_symbols: list = get_available_symbols(output_format=filters['output'])
    filtered_symbols: dict = {}
    for symbol in supported_symbols:
        if symbol['type'] in symbol_types:
            ticker = symbol['symbol']
            filtered_symbols[ticker] = symbol
    return filtered_symbols


"""
Input is a list of symbols to scrape, how many to scrape from list, and filters such as min max price,
and an list of stocks to append results to which happens to be a tuple made of the symbol, the stock, and
its historical data from 2015
"""


# THIS METHOD CANNOT WORK BECAUSE FIRST WE NEED A LIST OF STOCKS SORTED BY PRICE
def generate_tuple_dict(keys: list, index, filtered_symbols: dict, filter_list: dict, stocks: dict):
    # Not guarenteed to get search amount size becase of checking filter price
    for i in range(index[0], index[1]):
        key = keys[i]
        time.sleep(0.001)
        try:
            stock = Stock(key)
            if stock is not None:
                stock_price = stock.get_price()
                if stock_price is not None:
                    if filter_list['min'] <= stock.get_price() <= filter_list['max']:
                        historical_data = get_historical_data(key, output_format=filters['output'])
                        value = filtered_symbols[key]
                        stock_data = {'price': stock_price, 'sector': stock.get_sector()}
                        stocks[key] = (value, stock_data, historical_data)
                        print(key)
        except Exception as e:
            print("Symbol " + key + " has error")
            print(e)


"""
Input is list of filtered symbols like common stock and exchange traded funds.
Uses threads to make api calls and quickly scrape all stock info for each symbol given under the
search amount.
"""


def multi_threaded_stock_search(filtered_symbols: dict) -> dict:
    stocks = {}
    threads = []
    keys = list(filtered_symbols.keys())
    random.shuffle(keys)
    # Minimum per thread
    size = filters['min_per_thread']
    if filters['search_amount'] >= filters['max_threads'] * filters['min_per_thread']:
        size = int(filters['search_amount'] / filters['max_threads'])
    stocks_left = filters['search_amount']
    i = 0
    active_threads = 0
    while stocks_left > 0:
        if active_threads == filters['max_threads'] - 1 or stocks_left < size * 2:
            size = stocks_left
        if i + size < len(keys):
            index = (i, i + size)
        else:
            index = (i, len(keys))
        thread = threading.Thread(target=generate_tuple_dict, args=(keys, index, filtered_symbols,
                                                                    filters['cost_options'],
                                                                    stocks))
        threads.append(thread)
        thread.start()
        stocks_left -= size
        i += size
        active_threads += 1

    for thread in threads:
        thread.join()
    return stocks


def print_symbols(symbols: list):
    for symbol in symbols:
        print(symbol['name'])


# DataStock = (Symbol, Stock, HistoricalData
def print_tuples(data_stocks: dict):
    for k, data_stock in data_stocks.items():
        symbol = data_stock[0]
        stock = data_stock[1]
        historical_data = data_stock[2]
        abbreviated_name = symbol['name']
        if len(abbreviated_name) > 40:
            abbreviated_name = abbreviated_name[0:37] + "..."
        output = (symbol['symbol'], abbreviated_name, stock['sector'])
        print("{0:<10} {1:<45} {2:<38}".format(*output))
        print(historical_data)


"""
Uses pickle to dump list of tuples to file and allows it to be read back later should user
set the should_download parameter to false in the main method
"""


def write_data_stocks_to_file(data_stocks: dict, file_name: str):
    with open(file_name, 'wb') as f:
        pickle.dump(data_stocks, f)
        print("Successfully dumped list to file", file_name)


def read_data_stocks_from_file(file_name: str) -> dict:
    with open(file_name, 'rb') as f:
        data_stocks = pickle.load(f)
        print("Successfully read list from file", file_name)
    return data_stocks


def get_data_stocks(should_download: bool) -> dict:
    if should_download:
        filtered_symbols: dict = (get_filtered_symbols(filters['symbol_types']))
        data_stocks: dict = multi_threaded_stock_search(filtered_symbols)
        write_data_stocks_to_file(data_stocks, filters['file_name'])
    else:
        data_stocks: dict = read_data_stocks_from_file(
            filters['file_name'])
    return data_stocks


"""
Uses Plotly to generate html file and opens it showing the interactive time slider graph
with EMA SMA and Stock Price. Will be fully customizable later for whatever kind of lines want
to be shown.
"""


def draw_graph(data_stock):
    # df = pd.read_csv('finance-charts-apple.csv')
    df = data_stock[2]
    trace_open = go.Scatter(
        x=df.index,
        y=df['open'],
        name="Open Price",
        line=dict(color='#17BECF'),
        opacity=0.8)

    # This is a data frame
    short_rolling = df.rolling(window=20).mean()
    short_rolling = go.Scatter(
        x=short_rolling.index,
        y=short_rolling['open'],
        name="20 SMA",
        line=dict(color='#7F7F7F'),
        opacity=0.8)

    # This is a data frame
    long_rolling = df.rolling(window=100).mean()

    long_rolling = go.Scatter(
        x=long_rolling.index,
        y=long_rolling['open'],
        name="100 SMA",
        line=dict(color='#FF5733'),
        opacity=0.8)

    # This is a data frame
    ema_short = df.ewm(span=20, adjust=False).mean()
    ema_short = go.Scatter(
        x=ema_short.index,
        y=ema_short['open'],
        name="20 EMA",
        line=dict(color='#FF5733'),
        opacity=0.8)

    # data = [trace_high, trace_low]
    data = [trace_open, short_rolling, long_rolling, ema_short]
    layout = dict(
        title=data_stock[0]['symbol'],
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label='1m',
                         step='month',
                         stepmode='backward'),
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(count=28,
                         label='3w',
                         step='day',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date'
        )
    )

    fig = dict(data=data, layout=layout)
    py.plot(fig, filename='stock_chart.html')


"""Criteria: Total Area %, Number of days up or down."""
"""
Ascending or descending overall and head
"""


def apply_search_criteria(data_stocks: list, time_period, search_criteria: dict, output: list):
    return output


@app.route("/api/v1/get-stocks/<state>")
def get_route_stocks(state):
    data_stocks = None
    if state == "new":
        data_stocks = get_data_stocks(True)
    elif state == "old":
        data_stocks = get_data_stocks(False)
    return jsonify(**data_stocks)


def main():
    start = timer()
    data_stocks: dict = get_data_stocks(should_download=True)
    #print_tuples(data_stocks)
    # draw_graph(random.choice(data_stocks))
    end = timer()
    print("Total time taken :", end - start, "seconds")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8000), debug=True)
    main()
