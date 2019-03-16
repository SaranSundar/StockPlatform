import json

import pandas as pd
import plotly
import plotly.graph_objs as go
import plotly.offline as py

"""
Uses Plotly to generate html file and opens it showing the interactive time slider graph
with EMA SMA and Stock Price. Will be fully customizable later for whatever kind of lines want
to be shown.
"""


def draw_graph(df):
    # Used for Plotly API, can see graphs on there website but I use offline mode.
    plotly.tools.set_credentials_file(
        username='SS_Zeklord', api_key='Z1JPugSh0SQav7gFwBRk')

    trace_open = go.Scatter(
        x=df.index,
        y=df['close'],
        name="Close Price",
        line=dict(color='#17BECF'),
        opacity=0.8)

    # This is a data frame
    short_rolling = df.rolling(window=20).mean()
    short_rolling = go.Scatter(
        x=short_rolling.index,
        y=short_rolling['close'],
        name="20 SMA",
        line=dict(color='#7F7F7F'),
        opacity=0.8)

    # This is a data frame
    long_rolling = df.rolling(window=100).mean()

    long_rolling = go.Scatter(
        x=long_rolling.index,
        y=long_rolling['close'],
        name="100 SMA",
        line=dict(color='#FF5733'),
        opacity=0.8)

    # This is a data frame
    ema_short = df.ewm(span=20, adjust=False).mean()
    ema_short = go.Scatter(
        x=ema_short.index,
        y=ema_short['close'],
        name="20 EMA",
        line=dict(color='#FF5733'),
        opacity=0.8)

    # data = [trace_high, trace_low]
    data = [trace_open, short_rolling, long_rolling, ema_short]
    layout = dict(
        title='Stock Graph',
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


def json_to_df(data_stocks1, data_stocks2):
    json_str_data_frame = data_stocks1['WTM'][2]
    # CODE GOES BELOW TO CONVERT JSON STRING TO DATAFRAME
    json_str_data_frame = json.loads(json_str_data_frame)

    date_list = []
    open_list = []
    high_list = []
    low_list = []
    close_list = []
    vol_list = []
    for date in json_str_data_frame:
        date_list.append(date)
        day = json_str_data_frame[date]
        open_list.append(day['open'])
        high_list.append(day['high'])
        low_list.append(day['low'])
        close_list.append(day['close'])
        vol_list.append(day['volume'])

    converted_data_frame = pd.DataFrame({'date': date_list,
                                         'open': open_list,
                                         'high': high_list,
                                         'low': low_list,
                                         'close': close_list,
                                         'volume': vol_list}).set_index('date')
    # pandas_data_frame = data_stocks2['WTM'][2]

    draw_graph(converted_data_frame)
