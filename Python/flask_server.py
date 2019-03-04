import os
import subprocess

from flask import Flask, Response

from graph_util import draw_graph
from stock_scraper import start_scraping
from store import redis_set, redis_get

app = Flask(__name__)
app.config.update(
    DEBUG=True, JSON_SORT_KEYS=False, JSONIFY_PRETTYPRINT_REGULAR=False)

"""
Uses Plotly to generate html file and opens it showing the interactive time slider graph
with EMA SMA and Stock Price. Will be fully customizable later for whatever kind of lines want
to be shown.
"""


# The ONLY method allowed for this route will be POST
@app.route("/api/graph/<symbol>")
def show_graph(symbol):
    app.logger.info('Graphing symbol ' + symbol)
    data_stocks = redis_get("data_stocks")
    # data stocks is a json dict, need to convert to data frame
    data_stock = data_stocks[symbol][2]
    # df = pd.read_csv('finance-charts-apple.csv')
    # df = pd.read_msgpack(data_stock[2])
    draw_graph(data_stock)

    # Status code 204 represents NO CONTENT for
    # POST requests that don't return anything
    return Response(None, 204)


@app.route("/index")
@app.route("/")
def main():
    # app.logger.info('Scraping Data, Please Wait...')
    file_name = "scraped_stocks2.bin"
    format_type = 'pandas'
    search_amount = 10000
    (data_stocks, filters) = start_scraping(
        should_download=False, file_name=file_name, format_type=format_type, search_amount=search_amount)
    # for key, value in data_stocks.items():
    #     data_stock = data_stocks[key]
    #     data_stock = (data_stock[0], data_stock[1], data_stock[2].to_msgpack())
    #     data_stocks[key] = data_stock
    redis_set("data_stocks", data_stocks)
    redis_set("filters", filters)
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
    subprocess.call(["brew", "services", "stop", "redis"])
    subprocess.call(["brew", "services", "start", "redis"])
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8000), debug=True)
