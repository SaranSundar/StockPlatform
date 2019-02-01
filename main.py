from iexfinance import get_available_symbols
from iexfinance.stocks import Stock, get_historical_data

from DataStock import DataStock


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
    for (key, value) in filtered_symbols:
        stock = Stock(key)
        if filter_list['min'] <= stock.get_price() <= filter_list['max']:
            stocks[key] = (value, stock, get_historical_data(key, output_format='pandas'))
            count += 1
        if count >= input_size:
            break
    return stocks


def print_symbols(symbols: list):
    for symbol in symbols:
        print(symbol['name'])


def main():
    filtered_symbols: dict = {}
    filtered_symbols = (get_filtered_symbols(['cs', 'etf']))
    test(filtered_symbols, 2)


if __name__ == '__main__':
    main()
