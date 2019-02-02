import pickle
import threading
import time
from random import shuffle
from timeit import default_timer as timer

import plotly
import plotly.graph_objs as go
import plotly.offline as py
from iexfinance import get_available_symbols
from iexfinance.stocks import Stock, get_historical_data

plotly.tools.set_credentials_file(username='SS_Zeklord', api_key='Z1JPugSh0SQav7gFwBRk')
# Search amount should always be divisible by max threads
filters = {'symbol_types': ['cs', 'etf'], 'cost_options': {'min': 11, 'max': 40}, 'search_amount': 100,
           'file_name': 'data_stocks.bin', 'max_threads': 25}


def get_filtered_symbols(symbol_types: list = None) -> dict:
    if symbol_types is None:
        symbol_types = ['cs', 'etf']
    supported_symbols: list = get_available_symbols(output_format='pandas')
    filtered_symbols: dict = {}
    for symbol in supported_symbols:
        if symbol['type'] in symbol_types:
            ticker = symbol['symbol']
            filtered_symbols[ticker] = symbol
    return filtered_symbols


def generate_tuple_dict(keys: list, filtered_symbols: dict, input_size: int, filter_list: dict, stocks: list):
    count = 0
    for key in keys:
        time.sleep(0.001)
        try:
            stock = Stock(key)
            if stock is not None:
                stock_price = stock.get_price()
                if stock_price is not None:
                    historical_data = get_historical_data(key, output_format='pandas')
                    if filter_list['min'] <= stock.get_price() <= filter_list['max']:
                        value = filtered_symbols[key]
                        stocks.append((value, stock, historical_data))
                        count += 1
                        print(key)
                    if count >= input_size:
                        break
        except:
            print("Symbol " + key + " has error")


def multi_threaded_stock_search(filtered_symbols: dict) -> list:
    stocks = []
    thread_count = filters['max_threads']
    threads = {}
    keys = list(filtered_symbols.keys())
    shuffle(keys)
    thread_search_amount = int(min(filters['search_amount'], len(keys)) / thread_count)
    for i in range(thread_count):
        threads[i] = threading.Thread(target=generate_tuple_dict,
                                      args=(keys[
                                            i * thread_search_amount: (i * thread_search_amount) +
                                                                      thread_search_amount],
                                            filtered_symbols, thread_search_amount,
                                            filters['cost_options'],
                                            stocks))
        threads[i].start()

    for i in range(thread_count):
        threads[i].join()
    return stocks


def print_symbols(symbols: list):
    for symbol in symbols:
        print(symbol['name'])


# DataStock = (Symbol, Stock, HistoricalData
def print_tuples(data_stocks: list):
    for data_stock in data_stocks:
        symbol = data_stock[0]
        stock = data_stock[1]
        historical_data = data_stock[2]
        abbreviated_name = symbol['name']
        if len(abbreviated_name) > 40:
            abbreviated_name = abbreviated_name[0:37] + "..."
        output = (symbol['symbol'], abbreviated_name, stock.get_sector())
        print("{0:<10} {1:<45} {2:<38}".format(*output))
        print(historical_data)


def write_data_stocks_to_file(data_stocks: list, file_name: str):
    with open(file_name, 'wb') as f:
        pickle.dump(data_stocks, f)
        print("Successfully dumped list to file", file_name)


def read_data_stocks_from_file(file_name: str) -> list:
    with open(file_name, 'rb') as f:
        data_stocks = pickle.load(f)
        print("Successfully read list from file", file_name)
    return data_stocks


def get_data_stocks(should_download: bool) -> list:
    if should_download:
        filtered_symbols: dict = (get_filtered_symbols(filters['symbol_types']))
        data_stocks: list = multi_threaded_stock_search(filtered_symbols)
        write_data_stocks_to_file(data_stocks, filters['file_name'])
    else:
        data_stocks: list = read_data_stocks_from_file(
            filters['file_name'])
    return data_stocks


def draw_graph(data_stock):
    # df = pd.read_csv('finance-charts-apple.csv')
    df = data_stock[2]
    trace_open = go.Scatter(
        x=df.index,
        y=df['open'],
        name="Open Price",
        line=dict(color='#17BECF'),
        opacity=0.8)
    # trace_high = go.Scatter(
    #     x=df.Date,
    #     y=df['AAPL.High'],
    #     name="AAPL High",
    #     line=dict(color='#17BECF'),
    #     opacity=0.8)
    # trace_low = go.Scatter(
    #     x=df.Date,
    #     y=df['AAPL.Low'],
    #     name="AAPL Low",
    #     line=dict(color='#7F7F7F'),
    #     opacity=0.8)

    # data = [trace_high, trace_low]
    data = [trace_open]
    layout = dict(
        title=data_stock[0]['name'],
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
    py.plot(fig, filename="Time Series with Rangeslider")


def main():
    start = timer()
    data_stocks: list = get_data_stocks(should_download=False)
    # print_tuples(data_stocks)
    draw_graph(data_stocks[0])
    end = timer()
    print("Total time taken :", end - start, "seconds")


if __name__ == '__main__':
    main()
