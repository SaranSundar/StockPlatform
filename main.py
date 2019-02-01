import time
from random import shuffle
from timeit import default_timer as timer

from iexfinance import get_available_symbols
from iexfinance.stocks import Stock, get_historical_data

filters = {'symbol_types': ['cs', 'etf'], 'cost_options': {'min': 11, 'max': 40}, 'search_amount': 10}


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


def generate_tuple_dict(filtered_symbols: dict, input_size: int, filter_list: dict):
    stocks = {}
    count = 0
    keys = list(filtered_symbols.keys())
    shuffle(keys)
    for key in keys:
        time.sleep(0.001)
        stock = Stock(key)
        if filter_list['min'] <= stock.get_price() <= filter_list['max']:
            value = filtered_symbols[key]
            stocks[key] = (value, stock, get_historical_data(key, output_format='pandas'))
            count += 1
            print(key)
        if count >= input_size:
            break
    return stocks


def print_symbols(symbols: list):
    for symbol in symbols:
        print(symbol['name'])


def print_tuples(data_stocks: dict):
    for (key, value) in data_stocks.items():
        print(key)
        print(value[0]['name'])
        print(value[1].get_sector())
        # print("Symbol: " + key + ", Company Name: " + value[0]['name'] + ", Sector: " + value[1].get_sector())
        print()
        # print(value[2])


def main():
    start = timer()
    filtered_symbols: dict = (get_filtered_symbols(filters['symbol_types']))
    data_stocks: dict = generate_tuple_dict(filtered_symbols, filters['search_amount'], filters['cost_options'])
    # print_tuples(data_stocks)
    end = timer()
    print("Total time taken :", end - start, "seconds")


if __name__ == '__main__':
    main()
