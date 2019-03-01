import pickle
import random
import sys
import threading
import time
from timeit import default_timer as timer

import simplejson
from iexfinance.refdata import get_symbols
from iexfinance.stocks import Stock, get_historical_data

from apply_search_criteria import apply_search_criteria
from graph_util import draw_graph

progress = 0.0

"""
Input is what kind of symbols you want, cs is common stock, etf is exchange traded funds.
There are more options that we dont need for now
"""


def get_filtered_symbols(symbol_types: list) -> dict:
    format_type: str = "json"
    filtered_symbols = {}
    if symbol_types is None:
        symbol_types = ['cs', 'etf']
    supported_symbols = get_symbols(output_format=format_type)
    for symbol in supported_symbols:
        if symbol['type'] in symbol_types:
            ticker = symbol['symbol']
            filtered_symbols[ticker] = symbol
    return filtered_symbols


def print_symbols(symbols: list):
    for symbol in symbols:
        print(symbol['name'])


# DataStock = (Symbol, Stock, HistoricalData)
def print_tuples(stocks: dict):
    for k, data_stock in stocks.items():
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


def write_obj_to_file(obj, file_name: str):
    with open(file_name, 'wb') as f:
        pickle.dump(obj, f)
        print("Successfully dumped list to file", file_name)


def read_obj_from_file(file_name: str):
    with open(file_name, 'rb') as f:
        obj = pickle.load(f)
        print("Successfully read list from file", file_name)
    return obj


"""
Input is a list of symbols to scrape, how many to scrape from list, and filters such as min max price,
and an list of stocks to append results to which happens to be a tuple made of the symbol, the stock, and
its historical data from 2015
"""


def generate_tuple_dict(keys: list, index, stocks: dict, filtered_symbols: dict, format_type: str, search_amount: int):
    global progress
    for i in range(index[0], index[1]):
        key = keys[i]
        time.sleep(0.001)
        try:
            stock = Stock(key)
            if stock is not None:
                stock_price = stock.get_price()
                if stock_price is not None:
                    # if cost_options['min'] <= stock.get_price() <= cost_options['max']:
                    historical_data = get_historical_data(
                        key, output_format=format_type)
                    if format_type is "pandas":
                        # Removes all rows with NaN
                        historical_data = historical_data.dropna(how='any')
                    elif format_type is "json":
                        historical_data = simplejson.dumps({**historical_data}, ignore_nan=True)
                    symbol = filtered_symbols[key]
                    stock_data = {'price': stock_price,
                                  'sector': stock.get_sector()}
                    stocks[key] = (symbol, stock_data, historical_data)
                    progress += 1.0
                    p_display = progress / search_amount
                    p_display = round(p_display, 4) * 100
                    # p_display = str(p_display)
                    # p_display_arr = p_display.split(".")
                    # p_display = p_display_arr[0] + "."
                    # if len(p_display_arr[1]) <= 2:
                    #     p_display += p_display[1]
                    # else:
                    #     p_display += p_display[1][:2]
                    output = "Downloading " + str(p_display) + "%..."
                    sys.stdout.write('\r' + output)

        except Exception as e:
            # print("Symbol " + key + " has error")
            print(e)


"""
Input is list of filtered symbols like common stock and exchange traded funds.
Uses threads to make api calls and quickly scrape all stock info for each symbol given under the
search amount.
"""


def multi_threaded_stock_search(filtered_symbols: dict, search_amount: int,
                                format_type: str) -> dict:
    global progress
    stocks = {}
    threads = []
    keys = list(filtered_symbols.keys())
    random.shuffle(keys)
    # 4 in one Thread Min, 25 Threads max
    min_per_threads = 4
    max_threads = 100
    size = min_per_threads
    if search_amount > len(keys):
        search_amount = len(keys)
    if search_amount >= max_threads * min_per_threads:
        size = int(search_amount / max_threads)
    stocks_left = search_amount
    i = 0
    active_threads = 0
    while stocks_left > 0:
        if active_threads == max_threads - 1 or stocks_left < size * 2:
            size = stocks_left
        if i + size < len(keys):
            index = (i, i + size)
        else:
            index = (i, len(keys))
        thread = threading.Thread(target=generate_tuple_dict, args=(keys, index,
                                                                    stocks, filtered_symbols, format_type,
                                                                    search_amount))
        threads.append(thread)
        thread.start()
        stocks_left -= size
        i += size
        active_threads += 1
    progress = 0.0
    for thread in threads:
        thread.join()
    print("")
    return stocks


def get_data_stocks(should_download: bool, file_name: str, search_amount: int = 100, format_type='pandas'):
    if should_download:
        print("Scraping Data, Please Wait...")
        symbol_types = ['cs', 'etf']
        filtered_symbols = get_filtered_symbols(symbol_types)
        data_stocks = multi_threaded_stock_search(filtered_symbols, search_amount,
                                                  format_type)
        write_obj_to_file(data_stocks, file_name)
    else:
        print("Reading Data, Please Wait...")
        data_stocks = read_obj_from_file(file_name)
    return data_stocks


def get_all_sectors(data_stocks: dict):
    sectors = set()
    for d_stock in data_stocks.items():
        sectors.add(d_stock[1][1]['sector'])
    sectors = list(sectors)
    # Removes the empty item in the set
    sectors.__delitem__(0)
    return sectors


def apply_filters(data_stocks: dict, filters: dict):
    filtered_stocks = {}
    sorted_d_stocks = sorted(data_stocks.items(), key=lambda x: x[1][1]['price'], reverse=filters['price_descending'])
    # for symbol, d_stock in data_stocks.items():
    #     print(symbol, "$" + str(d_stock[1]['price']), d_stock[1]['sector'])
    for stock_tuple in sorted_d_stocks:
        # DataStock = (Symbol, Stock, HistoricalData)
        key = stock_tuple[0]
        d_stock = stock_tuple[1]
        if not (filters['min_price'] <= d_stock[1]['price'] <= filters['max_price']):
            continue
        if len(filters['sectors']) != 0 and not d_stock[1]['sector'] in filters['sectors']:
            continue
        filtered_stocks[key] = d_stock
        print(key, "---", d_stock[1]['price'], "---", d_stock[0]['name'], "---", d_stock[1]['sector'])
    return filtered_stocks


def print_help_menu():
    print("--------MENU-----------")
    print("1. Display Stocks Ascending")
    print("2. Display Stocks Descending")
    print("3. Set Min and Max Price")
    print("4. Display All Sectors")
    print("5. Download All Stocks")
    print("6. Help Menu")
    print("7. Filter by String")
    print("8. Exit Program")


# IMPORTANT, ANY USAGE OF THE PANDAS DATAFRAME IN THE DATASTOCK NOW REQUIRES IT TO BE DECODED WITH
# pd.read_msgpack(data_stock[2])
def console_app(data_stocks: dict, filters: dict):
    print("Welcome to Exodius v1.0")
    print_help_menu()
    while True:
        try:
            op = input(">")
            if op == "1":
                filters['price_descending'] = False
                filtered_stocks = apply_filters(data_stocks, filters)
            elif op == "2":
                filters['price_descending'] = True
                filtered_stocks = apply_filters(data_stocks, filters)
            elif op == "3":
                filters['min'] = float(input("Enter Min Price:"))
                filters['max'] = float(input("Enter Max Price:"))
                filtered_stocks = apply_filters(data_stocks, filters)
            elif op == "4":
                print("------SECTORS------")
                sectors = filters['sectors']
                for i in range(len(sectors)):
                    print(sectors[i], end=", ")
                    if i + 1 < len(sectors):
                        print(sectors[i + 1])
                    else:
                        print("")
            elif op == "5":
                # data_stocks = get_data_stocks(should_download=True, file_name=filters['file_name'],
                #                               search_amount=filters['search_amount'])
                print("This option is currently too dangerous to use, so it is disabled")
            elif op == "6" or op == "help":
                print_help_menu()
            elif op == "7":
                print("Known Terminals: window() getTrend()")
                search_string = input(">>")
                # I return filtered stocks in a dict because data_stocks is a dict. That way I can chain searches in
                # the future.
                filtered_dict_stocks = apply_search_criteria(data_stocks, search_string)
                for k in filtered_dict_stocks.keys():
                    print(filtered_dict_stocks[k][0]['symbol'])
                    print(filtered_dict_stocks[k][1]['sector'])
            elif op == "8" or op == "exit":
                print("Exiting Program")
                break
            else:
                print("Please Enter A Valid Option")
        except Exception as e:
            print(e)
        print("")


def start_scraping(should_download, file_name, search_amount=10, format_type='json'):
    filters = {'min_price': 0, 'max_price': float('inf'), 'price_descending': False,
               'sectors': set(), 'should_download': should_download,
               'search_amount': search_amount, 'file_name': file_name}
    start = timer()
    data_stocks = get_data_stocks(should_download, file_name, search_amount, format_type=format_type)
    # Get all filters
    sectors = get_all_sectors(data_stocks)
    # Ex. Sectors - "Financial Services", "Industrials", "Energy"
    filters['sectors'] = sectors
    apply_filters(data_stocks, filters)
    # print(len(data_stocks))
    # print_tuples(data_stocks)
    end = timer()
    print("Total time taken :", end - start, "seconds")
    return data_stocks, filters


"""Two test cases, more commonly will use 1 for running main data and 2 for trying new code"""


def set1():
    file_name = "scraped_stocks.bin"
    search_amount = 10000  # Arbitrarily large value to scrape all available stocks
    format_type = 'json'  # Can also be pandas
    (data_stocks, filters) = start_scraping(should_download=False, file_name=file_name, search_amount=search_amount)
    return data_stocks, filters


def set2():
    file_name = "scraped_stocks2.bin"
    search_amount = 10  # Arbitrarily large value to scrape all available stocks
    format_type = 'pandas'  # Can also be pandas
    (data_stocks, filters) = start_scraping(should_download=False, file_name=file_name, search_amount=search_amount,
                                            format_type=format_type)
    return data_stocks, filters


def main():
    (data_stocks1, filters1) = set1()
    (data_stocks2, filters2) = set2()
    # console_app(data_stocks, filters)
    json_to_df(data_stocks1, data_stocks2)
    print("-------EXODIUS v1.0-------")


def json_to_df(data_stocks1, data_stocks2):
    json_str_data_frame = data_stocks1['NTAP'][2]
    # CODE GOES BELOW TO CONVERT JSON STRING TO DATAFRAME

    pandas_data_frame = data_stocks2['NTAP'][2]

    draw_graph(pandas_data_frame)


if __name__ == '__main__':
    main()
