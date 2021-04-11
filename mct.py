import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
#from PyQt5.QtWidgets import * 
#from PyQt5.QtCore import *
from PyQt5.QtWidgets import QDesktopWidget
import numpy as np
import ccxt
import datetime as dt
import pprint as pp
from math import log10, floor
import random

#import threading #used only to id the active thread
#import code



debug = False
exchange = ccxt.binance()
markets = exchange.fetch_markets()



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
        
    def add_item(self, x, y, h):
        self.x.append(x) # + self.offset)
        self.y.append(y)
        self.h.append(h)


def get_exponent(n) -> int:
    base10 = log10(abs(n))
    return floor(base10)


def run(form, graph_length=200):
    random_test(form, graph_length)

def random_test(form, graph_length=200):
    graph_length = min(graph_length, 499)
    ts = random.choice(timescale)
    ticker = random.choice(markets)['symbol']

    if random.choice([True, False]):
        gd = real_test(graph_length, ticker, ts)
    else:
        gd = fake_test(graph_length, ticker, ts)    

    show_data(form, gd, ticker)

def real_test(graph_length=200, ticker='BTC/USDT', ts='4h'):
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

def fake_test(graph_length=200, ticker='BTC/USDT', ts='4h'):
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
        wick_data.add_item(i, candles[i].wick_value, candles[i].wick_height)
        if candles[i].uptrend == True:
            up_data.add_item(i, candles[i].candle_value, candles[i].candle_height)
        else:
            dn_data.add_item(i, candles[i].candle_value, candles[i].candle_height)

    return [up_data, dn_data, wick_data]

def show_data(form, gd, ticker=''):
    if debug:
        form.plot.setWindowTitle(ticker)

    data = []
    data.extend([init_bar_graph(gd[0]), init_bar_graph(gd[1]), init_bar_graph(gd[2])])
    form.delete_bgi()
    form.apply_bgi(data)
    form.win_show()

def init_bar_graph(d):
    return pg.BarGraphItem(x=d.x, y=d.y, height=d.h, width=d.width, brush=d.brush)


# class Worker(QThread): #Subclass QThread and re-define run() 
#     signal = pyqtSignal()

#     def __init__(self):
#         super().__init__()

#     def raise_sys_exit(self): #more gracefully exit the console
#         print('(Deactivated Console)')
#         raise SystemExit

#     def setup_console(self,global_dict):
#         console_exit = {'exit': self.raise_sys_exit}
#         self.console = code.InteractiveConsole(locals=dict(global_dict,**console_exit))

#     def run(self):
#         try:
#             print('worker', threading.get_ident())
#             self.console.interact()
#         except SystemExit:
#             self.signal.emit()


#class Form(QMainWindow):
class Form():
    def __init__(self, *args, **kwargs):
        # super(Form, self).__init__(*args, **kwargs)
        self.win = pg.GraphicsLayoutWidget(show=True, title='market chart tools')

        self.win.resize(1600, 900)
        self.win.setWindowTitle('Market Chart Tools')

        ag = QDesktopWidget().availableGeometry()
        sg = QDesktopWidget().screenGeometry()
        x = ag.width() - self.win.width()
        y = 2 * ag.height() - sg.height() - self.win.height()
        self.win.move(int(x/2), int(y/2))

        pg.setConfigOptions(antialias=True)

        #plot object
        self.plot = pg.PlotWidget()

        #button objects
        self.btn_go = QtGui.QPushButton('Go!')
        self.btn_go.clicked.connect(self.btn_go_event)
        self.btn_real = QtGui.QPushButton('Real')
        self.btn_real.clicked.connect(self.btn_real_event)
        self.btn_next = QtGui.QPushButton('Next')
        self.btn_next.clicked.connect(self.btn_next_event)
        self.btn_show = QtGui.QPushButton('Show')
        self.btn_show.clicked.connect(self.btn_show_event)
        self.btn_reset = QtGui.QPushButton('Reset')
        self.btn_reset.clicked.connect(self.btn_reset_event)

        self.buttons = []
        self.buttons.extend([self.btn_go, self.btn_real, self.btn_next, self.btn_show, self.btn_reset])

        #grid layout
        self.layout = QtGui.QGridLayout()
        self.win.setLayout(self.layout)

        #register objects
        self.layout.addWidget(self.btn_go, 0, 0)
        self.layout.addWidget(self.btn_real, 1, 0)
        self.layout.addWidget(self.btn_next, 2, 0)
        self.layout.addWidget(self.btn_show, 3, 0)
        self.layout.addWidget(self.btn_reset, 4, 0)
        self.layout.addWidget(self.plot, 0, 1, 9, 1)

        # console
        #self.console = pg.dbg(*args, **kwargs)

    def win_show(self):
        self.win.show()

    def delete_bgi(self):
        self.layout.removeWidget(self.plot)

    def apply_bgi(self, data):
        self.bg_up = data[0]
        self.bg_dn = data[1]
        self.bg_wick = data[2]

        self.plot = pg.PlotWidget()
        self.plot.addItem(self.bg_wick)
        self.plot.addItem(self.bg_up)
        self.plot.addItem(self.bg_dn)
        
        self.layout.addWidget(self.plot, 0, 1, 9, 1)

    def btn_go_event(self):
        run(self)

    def btn_real_event(self):
        pass

    def btn_next_event(self):
        pass

    def btn_show_event(self):
        pass

    def btn_reset_event(self):
        pass



def main():
    app = QtGui.QApplication([])
    gui = Form()
    sys.exit(app.exec_())


if __name__ == '__main__':
   main()
