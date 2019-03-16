# import pandas as pd


def get_percent_change(time_period, field='close'):
    start_price = float(time_period.head(1)[field])
    end_price = float(time_period.tail(1)[field])
    diff = end_price - start_price
    change = (diff / start_price) * 100.0
    # print("Starting:", start_price)
    # print("Ending:", end_price)
    # print("% Change:", change)
    return change


def get_moving_averages(time_period, field):
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
    short_mavg = time_period.rolling(window=50).mean()
    long_mavg = time_period.rolling(window=100).mean()
    emavg = time_period.ewm(span=20, adjust=False).mean()


def get_stocks_percent(data_stocks, percent, up=True, start_date='2019-03-11', end_date='2019-03-15',
                       field='close'):
    result = []
    for stock_name, data_stock in data_stocks.items():
        data_frame = data_stock[2]
        time_period = data_frame[start_date:end_date]
        percent_change = get_percent_change(time_period, field)
        info = (stock_name, percent_change)
        if up and percent_change >= percent:
            result.append(info)
        elif not up and percent_change <= percent:
            result.append(info)
    result.sort(key=lambda x: x[1], reverse=up)  # sorts in place
    print(result)
    return result
