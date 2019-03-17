# import pandas as pd
import sys


def get_percent_change(time_period, field='close'):
    start_price = float(time_period.head(1)[field])
    end_price = float(time_period.tail(1)[field])
    diff = end_price - start_price
    change = (diff / start_price) * 100.0
    # print("Starting:", start_price)
    # print("Ending:", end_price)
    # print("% Change:", change)
    return change


def calculate_graph_diffs(graph1, mavgs, field):
    def calculate_graph_diff(graph2):
        diff = 0.0
        totalY1 = 0.0
        for index1, row1 in graph1.iterrows():
            index1 = str(index1).split(" ")[0]
            row2 = graph2.loc[index1]
            y1 = float(row1[field])
            y2 = float(row2[field])
            totalY1 += y1
            diff += (y2 - y1)
            # print("Date:", index1, "Close", row1[field], "Short SMA", row2[field])
        diff = (diff / totalY1) * 100.0
        # print("Total %diff:", diff)
        return diff

    diffs = []
    for mavg in mavgs:
        diff = calculate_graph_diff(mavg)
        diffs.append(diff)
    return diffs


def get_moving_averages(history):
    """
        Growth Investors => Like to see moving averages trending up,
        and stock price continuously close above the moving avg.

        Value Investors => Might pick stock trading below moving avg,
        picks stock at discount hoping it goes back up to avg price.

        Volume => Above avg volume means price move, below means stopping.
        You want stock price to rise on heavy volume, fall on lighter volume.

        High Daily Volume => If stock price rises on higher then average volume,
        it's good. If it falls on higher that's really bad.

        Low Daily Volume => If stock price rises on lower then average volume,
        that's bad. Stock will definitely fall down. If price falls on lower volume,
        that's opportunity to buy because once it stops falling it will go up.
    """
    # 50 Used for both closing stock price and volume
    short_mavg = history.rolling(window=50).mean()
    long_mavg = history.rolling(window=100).mean()
    emavg = history.ewm(span=20, adjust=False).mean()
    return short_mavg, long_mavg, emavg


def get_stocks_percent(analysed_stocks, percent, up=True):
    # (data_stock, percent_change, graph_diffs)
    result = []
    for stock in analysed_stocks:
        percent_change = stock[1]
        if up and percent_change >= percent or not up and percent_change <= percent:
            result.append((stock[0][0]['symbol'], stock[1]))

    result.sort(key=lambda x: x[1], reverse=up)  # sorts in place
    print(result)


def print_progress(action='Downloading', progress=0.0, length=0.0):
    display = progress / length
    display = round(display, 4) * 100
    output = action + " " + str(display) + "%..."
    sys.stdout.write('\r' + output)


def analyse_stocks(data_stocks, start_date='2019-03-11', end_date='2019-03-15',
                   field='close'):
    result = []
    count = 0
    length = len(data_stocks)
    for stock_name, data_stock in data_stocks.items():
        try:
            data_frame = data_stock[2]
            time_period = data_frame[start_date:end_date]
            percent_change = get_percent_change(time_period, field)
            mavgs = get_moving_averages(data_frame)
            graph_diffs: list = calculate_graph_diffs(time_period, mavgs, field)  # Size of 3
            info = (data_stock, percent_change, graph_diffs)
            result.append(info)
            count += 1
            print_progress("Calculating", count, length)
        except Exception as e:
            # print("Error with stock:", stock_name)
            # print(e)
            # Ignore these stocks, only a small amount give
            # error due to not having all data points.
            pass
    return result
