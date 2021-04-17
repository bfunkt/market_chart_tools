import sys

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import QDesktopWidget, QLabel

import numpy as np
import pprint as pp
import random
import datetime as dt
from math import log10, floor

import mct_ui
import mct_ccxt as ex
import mct_chart as chart


debug = False


def get_exponent(n) -> int:
    base10 = log10(abs(n))
    return floor(base10)


def random_test(gui, graph_length):
    ts = random.choice(chart.timescale)
    ticker = random.choice(ex.get_markets())['symbol']
    ohlcv = ex.get_ohlcv(ticker, ts)

    gui.last_ticker = ticker
    gui.last_timescale = ts

    ohlcv = ohlcv[:np.random.randint(100,500)]
    if random.choice([True, False]):
        gui.last_real = 'Real'
    else:
        gui.last_real = 'Fake'
        # real ohlcv data is passed to fake_data as a means to set a general expectation for scale and range of the fake data
        ohlcv = fake_data(ohlcv, len(ohlcv))    

    ##################################################################################
    #temporary fix to the pg auto-resize issue
    price_range = chart.get_ohlcv_price_range(ohlcv)
    l = price_range[1] - (price_range[3]*0.2)
    h = price_range[2] + (price_range[3]*0.2)
    ##################################################################################

    candles = chart.get_candles_from_ohlcv(ohlcv)
    gd = chart.graphify_data(candles)

    show_data(gui, gd, l, h, ticker)


def fake_data(ohlcv=None, graph_length=200):
    if ohlcv is None:
        ohlcv = ex.get_ohlcv()
    return chart.get_fake_market_data(ohlcv, graph_length)


def show_data(gui, gd, l, h, ticker=''):
    data = []
    data.extend([init_bar_graph(gd[0]), init_bar_graph(gd[1]), init_bar_graph(gd[2])])
    gui.delete_bgi()
    gui.apply_bgi(data, l, h)
    print(f'{l}, {h}')
    gui.win_show()


def init_bar_graph(d):
    return pg.BarGraphItem(x=d.x, y=d.y, height=d.h, width=d.width, brush=d.brush)





class GUI():
    def __init__(self):
        self.ui = mct_ui.UI(pg, self)

    def run(self, child, graph_length=200):
        random_test(child, graph_length)




def main():
    app = QtGui.QApplication([])
    g = GUI()
    g.ui.win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
   main()
