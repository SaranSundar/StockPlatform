import os

import pandas as pd
import plotly
import plotly.graph_objs as go
import plotly.offline as py
from flask import Flask, session, jsonify
from flask_cors import CORS
from flask_session import Session

from stock_scraper import start_scraping

app = Flask(__name__)
app.secret_key = "qfeqv9839rnIBHVU9832"
CORS(app, supports_credentials=True)
app.config.update(
    DEBUG=True,
    JSON_SORT_KEYS=False,
    JSONIFY_PRETTYPRINT_REGULAR=False
)

# Configure sessions
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Used for Plotly API, can see graphs on there website but I use offline mode.
plotly.tools.set_credentials_file(
    username='SS_Zeklord', api_key='Z1JPugSh0SQav7gFwBRk')

"""
Uses Plotly to generate html file and opens it showing the interactive time slider graph
with EMA SMA and Stock Price. Will be fully customizable later for whatever kind of lines want
to be shown.
"""


@app.route("/api/graph/<symbol>")
def draw_graph(symbol):
    app.logger.info('Graphing symbol ' + symbol)
    data_stocks = session['data_stocks']
    # data stocks is a json dict, need to convert to data frame
    data_stock = data_stocks[symbol]
    # df = pd.read_csv('finance-charts-apple.csv')
    df = pd.read_msgpack(data_stock[2])
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
    return jsonify("Graph Being Drawn...")


@app.route("/index")
@app.route("/")
def main():
    # app.logger.info('Scraping Data, Please Wait...')
    file_name = "scraped_stocks2.bin"
    (data_stocks, filters) = start_scraping(should_download=True, file_name=file_name)
    session['data_stocks'] = data_stocks
    session['filters'] = filters
    # app.logger.info('Scraping Complete.')
    return '''
        <html>
            <head>
                <title>Flask Server</title>
            </head>
            <body>
                <h1>Home Page</h1>
            </body>
        </html>
        '''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8000), debug=True)
