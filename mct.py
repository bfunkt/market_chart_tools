import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import QDesktopWidget
import numpy as np
import ccxt
import datetime as dt
import pprint as pp
from math import log10, floor
import random


debug = False
exchange = ccxt.binance()
markets = exchange.fetch_markets()

win = None

#number of ms per candle timescale
# timescale = {   
#                 '1w': 604_800_000,
#                 '1d':  86_400_000,
#                 '4h':  14_400_000,
#                 '2h':   7_200_000,
#                 '1h':   3_600_000, 
#                 '30m':  1_800_000,
#                 '15m':    900_000,
#                 '5m':     300_000,
#                 '1m':      60_000
#             }

timescale = ['1w', '1d', '4h', '2h', '1h', '30m', '15m', '5m', '1m']


# args = [timestamp, o, h, l, c, v]
class Candle():
    def __init__(self, args):
        self.timestamp = args[0]
        self.data_o = args[1]
        self.data_h = args[2]
        self.data_l = args[3]
        self.data_c = args[4]
        self.data_v = args[5]

        self.candle_height = abs(self.data_o - self.data_c)
        self.candle_value = (self.data_o + self.data_c) / 2.0
        self.wick_height = abs(self.data_h - self.data_l)
        self.wick_value = (self.data_h + self.data_l) / 2.0

        self.trend = 0
        if self.data_o > self.data_c:
            self.trend = -1
        elif self.data_o < self.data_c:
            self.trend = 1

        self.uptrend = False
        if self.trend >= 0:
            self.uptrend = True 


class BarGraphData():
    def __init__(self, width=1.0, offset=0.0, brush=None):
        self.width = width
        self.offset = offset
        self.brush = brush
        self.x = []
        self.y = []
        self.h = []
        
    def addItem(self, x, y, h):
        self.x.append(x) # + self.offset)
        self.y.append(y)
        self.h.append(h)


def get_exponent(n) -> int:
    base10 = log10(abs(n))
    return floor(base10)


def run(graph_length=100):
    random_test(graph_length)

def random_test(graph_length=100):
    graph_length = min(graph_length, 499)
    ts = random.choice(timescale)
    ticker = random.choice(markets)['symbol']

    if random.choice([True, False]):
        gd = real_test(graph_length, ticker, ts)
    else:
        gd = fake_test(graph_length, ticker, ts)    

    show_data(gd, ticker)

def real_test(graph_length=100, ticker='BTC/USDT', ts='4h'):
    graph_length = min(graph_length, 499)
    #get real ohlcv data
    data = get_ohlcv(ticker, ts)
    #make an array of Candle objects
    candles = candleify_data(data)
    graph_length = min(graph_length, len(candles))
    #get graph-ready data
    gd = graphify_data(candles[:graph_length])

    if debug:
        print(f'+++ Fetching real market data: {ts} candles, {ticker}\n')
        print(f'+++ {len(candles)} candles parsed\n')

    return gd

def fake_test(graph_length=100, ticker='BTC/USDT', ts='4h'):
    graph_length = min(graph_length, 499)
    if debug:
        print(f'+++ Creating fake market data based on: {ts} candles, {ticker}\n')
    #get real trades
    trades = get_trades(ticker)
    avg_p, max_p, min_p = get_prices(trades)
    if debug:
        print(f'+++ avg_p={avg_p}, max_p={max_p}, min_p={min_p}\n')
    #create data
    fd = np.random.random_sample(100000)
    # if debug:
    #     print(f'+++ random_sample[:20]=\n{fd[:20]}\n')
    fd -= 0.5
    fd *= max_p
    fd /= min_p
    # if debug:
    #     print(f'+++ *= max_p, /= min_p=\n{fd[:20]}\n')
    fake_data = []
    #insert zeros into data to emulate time variance between trades
    for d in fd:
        fake_data.append(d)
        while np.random.random_sample() > 0.3:
            fake_data.append(0)
    # if debug:
    #     print(f'+++ After inserting zeros:\n{fake_data[:20]}\n')
    fake_data = np.cumsum(fake_data)
    # if debug:
    #     print(f'+++ cumsum:\n{fake_data[:20]}\n')

    candles = candles_from_fake_data(fake_data, graph_length)
    if debug:
        print(f'+++ Generated {len(candles)} candles from fake data\n')
    
    gd = graphify_data(candles[:graph_length])
    return gd

def candles_from_fake_data(data, graph_length):
    chunk = int(len(data) / graph_length)
    candles = []
    for i in range(graph_length):
        temp = data[(i*chunk):((i+1)*chunk)]
        # if debug:
        #     print(f'+++ Chunk length={len(temp)}\n{temp[:20]}\n')
        candles.append(Candle(['', temp[0], max(temp), min(temp), temp[-1], 0]))
    return candles

def get_prices(trades):
    avg_p = 0
    min_p = trades[0]['price']
    max_p = trades[0]['price']
    for trade in trades:
        avg_p += trade['price']
        min_p = min(min_p, trade['price'])
        max_p = max(max_p, trade['price'])
    avg_p /= len(trades)
    return avg_p, min_p, max_p

def get_time_spread(trades):
    return abs(trades[0]['timestamp'] - trades[-1]['timestamp'])

def get_ohlcv(ticker='BTC/USDT', ts='4h'):
    return exchange.fetch_ohlcv(symbol=ticker, timeframe=ts)

def get_trades(ticker='BTC/USDT'):
    return exchange.fetch_trades(ticker)

def candleify_data(data):
    candles = [Candle(c) for c in data]
    return candles

def graphify_data(candles):
    up_data = BarGraphData(0.9, brush='g')
    dn_data = BarGraphData(0.9, brush='r')
    wick_data = BarGraphData(0.1, 0.5, brush='w')

    for i in np.arange(len(candles)):
        wick_data.addItem(i, candles[i].wick_value, candles[i].wick_height)
        if candles[i].uptrend == True:
            up_data.addItem(i, candles[i].candle_value, candles[i].candle_height)
        else:
            dn_data.addItem(i, candles[i].candle_value, candles[i].candle_height)

    return [up_data, dn_data, wick_data]

def show_data(gd, ticker=''):
    plot1 = win.addPlot(title='Market Data')

    if debug:
        win.setWindowTitle(ticker)

    bg_up = init_bar_graph(gd[0])
    bg_dn = init_bar_graph(gd[1])
    bg_wick = init_bar_graph(gd[2])

    win.addItem(bg_wick)
    win.addItem(bg_up)
    win.addItem(bg_dn)

    win.show()

def init_bar_graph(d):
    return pg.BarGraphItem(x=d.x, y=d.y, height=d.h, width=d.width, brush=d.brush)


def init_window():
    app = QtGui.QApplication([])
    win = pg.GraphicsLayoutWidget(show=True, title='market chart tools')

    win.resize(1600, 900)
    win.setWindowTitle('Market Chart Tools')

    ag = QDesktopWidget().availableGeometry()
    sg = QDesktopWidget().screenGeometry()
    x = ag.width() - win.width()
    y = 2 * ag.height() - sg.height() - win.height()
    win.move(int(x/2), int(y/2))

    pg.setConfigOptions(antialias=True)

    #plot object
    plot = pg.PlotWidget()

    #button objects
    btn_go = QtGui.QPushButton('Go!')
    btn_real = QtGui.QPushButton('Real')
    btn_next = QtGui.QPushButton('Next')
    btn_show = QtGui.QPushButton('Show')
    btn_reset = QtGui.QPushButton('Reset')

    #grid layout
    layout = QtGui.QGridLayout()
    win.setLayout(layout)

    #register objects
    layout.addWidget(btn_go, 0, 0)
    layout.addWidget(btn_real, 1, 0)
    layout.addWidget(btn_next, 2, 0)
    layout.addWidget(btn_show, 3, 0)
    layout.addWidget(btn_reset, 4, 0)
    layout.addWidget(plot, 0, 1, 9, 1)

    #display as a new window
    win.show()

    #start the Qt event loop
    app.exec_()


if __name__ == '__main__':
   init_window()
