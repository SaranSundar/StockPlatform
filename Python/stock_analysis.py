# import pandas as pd


def get_percent_change(stock, start_date, end_date, field='close'):
    df = stock[2]
    time_period = df[start_date:end_date]
    start_price = float(time_period.head(1)[field])
    end_price = float(time_period.tail(1)[field])
    diff = end_price - start_price
    change = (diff / start_price) * 100.0
    # print("Starting:", start_price)
    # print("Ending:", end_price)
    # print("% Change:", change)
    return change


def get_stocks_percent(data_stocks, percent, up=True, start_date='2019-03-11', end_date='2019-03-15',
                       field='close'):
    result = []
    for key, value in data_stocks.items():
        percent_change = get_percent_change(value, start_date, end_date, field)
        info = (key, percent_change)
        if up and percent_change >= percent:
            result.append(info)
        elif not up and percent_change <= percent:
            result.append(info)
    result.sort(key=lambda x: x[1], reverse=up)  # sorts in place
    print(result)
    return result
