# ccxt wrapper for Market Chart Tools
import ccxt

debug = False
exchange = ccxt.binance()


def set_exchange(ex):
    exchange = ex

def get_ohlcv(ticker='BTC/USDT', ts='4h'):
    return exchange.fetch_ohlcv(symbol=ticker, timeframe=ts)

def get_trades(ticker='BTC/USDT'):
    return exchange.fetch_trades(ticker)

def get_markets():
    return exchange.fetch_markets()

def main():
    pass

if '__name__' == '__main__':
    main()