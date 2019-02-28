import os

import pandas as pd
from flask import Flask, session
from flask_cors import CORS
from flask_session import Session

from graph_util import draw_graph
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

"""
Uses Plotly to generate html file and opens it showing the interactive time slider graph
with EMA SMA and Stock Price. Will be fully customizable later for whatever kind of lines want
to be shown.
"""


@app.route("/api/graph/<symbol>")
def show_graph(symbol):
    app.logger.info('Graphing symbol ' + symbol)
    data_stocks = session['data_stocks']
    # data stocks is a json dict, need to convert to data frame
    data_stock = data_stocks[symbol]
    # df = pd.read_csv('finance-charts-apple.csv')
    df = pd.read_msgpack(data_stock[2])
    draw_graph(df)


@app.route("/index")
@app.route("/")
def main():
    # app.logger.info('Scraping Data, Please Wait...')
    file_name = "scraped_stocks.bin"
    (data_stocks, filters) = start_scraping(should_download=True, file_name=file_name)
    for data_stock in data_stocks.items():
        data_stock[2] = data_stock[2].to_msgpack()
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
