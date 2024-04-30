import yfinance as yf
import os
import warnings
from mplchart.chart import Chart
from mplchart.primitives import Candlesticks, Volume
from mplchart.indicators import ROC, SMA, EMA, RSI, MACD

TEMP_IMAGE_DIR = "temp_images"

os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)
warnings.simplefilter(action='ignore', category=FutureWarning)


def graph(ticker):

    msft = yf.Ticker(ticker)
    hist = msft.history(period="5y")
    image_path = os.path.join(TEMP_IMAGE_DIR, f'{ticker}_stock_price.png')
    max_bars = 250

    indicators = [
        Candlesticks(), SMA(10),SMA(60), SMA(200), EMA(10), EMA(60), EMA(200), Volume(),
        RSI(),
        MACD(),
    ]

    chart = Chart(title=ticker, max_bars=max_bars)
    chart.plot(hist, indicators)
    chart.figure.savefig(image_path)
    return image_path
