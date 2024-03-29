# import pandas as pd
import sys


def get_percent_change(time_period, field):
    start_price = float(time_period.head(1)[field])
    end_price = float(time_period.tail(1)[field])
    diff = end_price - start_price
    change = (diff / start_price) * 100.0
    # print("Starting:", start_price)
    # print("Ending:", end_price)
    # print("% Change:", change)
    return change


def calculate_graph_diffs(graph2, mavgs, field):
    def calculate_graph_diff(graph1):
        diff = 0.0
        totalY1 = 0.0
        for index, row2 in graph2.iterrows():
            index = str(index).split(" ")[0]
            row1 = graph1.loc[index]
            # Y2 needs to be top graph which is usually stock price,
            # Then Y1 is bottom graph which is moving average.
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


def always_above_or_below(graph1, graph2, field, percent=0.7, is_above=True):
    total = 0
    above = 0
    for index, row2 in graph2.iterrows():
        index = str(index).split(" ")[0]
        row1 = graph1.loc[index]
        # Graph 2 should be stock, graph 1 should be moving average
        y1 = float(row1[field])
        y2 = float(row2[field])
        total += 1
        if is_above and y2 > y1:
            above += 1
        elif not is_above and y2 < y1:
            above += 1
    ans = above / total
    return ans >= percent


def is_volume_behavior_good(history, average, field, percent=0.7):
    prev_price = 0.0
    total = 0.0
    passes = 0.0
    for index, volume_current in history.iterrows():
        index = str(index).split(" ")[0]
        volume_average = average.loc[index]
        y1 = float(volume_current['volume'])
        y2 = float(volume_average['volume'])
        p1 = float(volume_current[field])
        if y1 > y2:
            if p1 > prev_price:
                passes += 1
        elif y1 < y2:
            if p1 < prev_price:
                passes += 1
        total += 1
        prev_price = p1
    return passes / total >= percent


def is_stock_good(history, strategies, mavgs):
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
    trend = get_percent_change(history, 'close')
    if trend > 0 and always_above_or_below(mavgs[0], history, 'close') and is_volume_behavior_good(history, mavgs[0],
                                                                                                   'close'):
        return True


def get_moving_averages(history, short=50, long=100, ema=20):
    # 50 Used for both closing stock price and volume
    short_mavg = history.rolling(window=short).mean()
    long_mavg = history.rolling(window=long).mean()
    emavg = history.ewm(span=ema, adjust=False).mean()
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


def analyse_stocks(data_stocks, start_date, end_date,
                   field='close'):
    result = []
    count = 0
    length = len(data_stocks)
    for stock_name, data_stock in data_stocks.items():
        try:
            data_frame = data_stock[2]
            time_period = data_frame[start_date:end_date]
            percent_change = get_percent_change(time_period, field)
            mavgs = get_moving_averages(data_frame)  # Short, Long, Ema
            graph_diffs: list = calculate_graph_diffs(time_period, mavgs, field)  # Size of 3
            graph_diffs.append(calculate_graph_diffs(time_period, [mavgs[0]], field='volume'))
            info = (data_stock, percent_change, graph_diffs)
            if is_stock_good(time_period, None, mavgs):
                result.append(info)

            count += 1
            print_progress("Calculating", count, length)
        except Exception as e:
            print("Error with stock:", stock_name)
            print(e)
            # Ignore these stocks, only a small amount give
            # error due to not having all data points.
            # pass
    return result
