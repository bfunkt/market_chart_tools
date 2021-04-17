# mct_chart.py
# chart data for Market Chart Tools
import numpy as np


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


# Candle args = [timestamp, o, h, l, c, v]
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


def get_candles_from_ohlcv(data):
    candles = [Candle(c) for c in data]
    return candles


def get_ohlcv_from_price(data):
    return ['', data[0], max(data), min(data), data[-1], 0]


def get_fake_market_data(ohlcv, graph_length):
    avg_p, min_p, max_p, range_p = get_ohlcv_price_range(ohlcv)
    
    # create random data, weight towards smaller sizes, scale to match prices arg
    fd = np.random.random_sample(graph_length*200)
    fd *= 2
    fd -= 1
    # weight samples towards being smaller values (use an odd factor here to maintain the negative range
    fd **= 3

    #insert zeros into data to emulate time variance between price changes
    fd_temp = []
    for d in fd:
        n = 0.0
        if np.random.random_sample() > 0.999:
            print('in the thing')
            n = ((np.random.random_sample() * 2) - 1.0)
            fd_temp.append(d+n)
            fd_temp.append(-(d+n))
        
        else:
            fd_temp.append(d)
        while np.random.random_sample() > 0.35:
            fd_temp.append(0)

    # take the cumulative
    fd = np.cumsum(fd_temp)
    # set the full range to positive values only
    min_fd = min(fd)
    fd -= min_fd
    # scale up to the expected range
    max_fd = max(fd)
    fd *= range_p
    fd /= max_fd
    # shift
    fd += avg_p
    fd2 = fd
    # fd2 = []
    # for d in fd:
    #     n = 0.0
    #     if np.random.random_sample() > 0.999:
    #         print('in the thing')
    #         n = (np.random.random_sample() - 0.5) * range_p 
    #     fd2.append(d+n)


    
    #make ohlcv_data to match the return format of ccxt.fetch_ohlcv()
    ohlcv_data = []
    chunk = int(len(fd2) / graph_length)
    for i in range(graph_length):
        temp = fd2[(i*chunk) : ((i+1)*chunk)]
        ohlcv_data.append(get_ohlcv_from_price(temp))

    return ohlcv_data


def get_trades_price_range(trades):
    avg_p = 0.0
    min_p = trades[0]['price']
    max_p = trades[0]['price']
    for trade in trades:
        avg_p += trade['price']
        min_p = min(min_p, trade['price'])
        max_p = max(max_p, trade['price'])
    avg_p /= len(trades)
    return avg_p, min_p, max_p, (max_p-min_p)


def get_ohlcv_price_range(ohlcv):
    avg_p = 0.0
    min_p = ohlcv[0][3]
    max_p = ohlcv[0][2]
    for candle in ohlcv:
        avg_p += ((candle[2] + candle[3]) / 2)
        min_p = min(min_p, candle[3])
        max_p = max(max_p, candle[2])
    avg_p /= len(ohlcv)
    return avg_p, min_p, max_p, (max_p-min_p)


def expand_ohlcv(ohlcv, exp):
    n = 10**exp
    l = [[v*n for v in candle] for candle in ohlcv]
    return l


def get_time_spread(trades):
    return abs(trades[0]['timestamp'] - trades[-1]['timestamp'])


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


timescale = ['1w', '1d', '4h', '2h', '1h', '30m', '15m', '5m', '1m']

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

def main():
    pass


if __name__ == '__main__':
    main()
