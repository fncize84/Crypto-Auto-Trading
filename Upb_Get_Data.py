import pyupbit
import requests
import pandas as pd

def get_target_price(ticker, k):
    df = pyupbit.get_ohlcv(ticker, count=2)
    target_price = df.iloc[-1]['open'] + (df.iloc[-2]['high'] - df.iloc[-2]['low']) * k
    return target_price

def get_high_price(ticker):
    df = pyupbit.get_ohlcv(ticker, count=2)
    high_price = df['high'].iloc[-1]
    return high_price


def get_start_time():
    df = pyupbit.get_ohlcv("KRW-BTC")
    start_time = df.index[-1]
    return start_time

def get_ma5(ticker):
    df = pyupbit.get_ohlcv(ticker, count=5)
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    return ma5

def get_current_price(ticker):
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def return_coin_name(ticker):
    url = "https://api.upbit.com/v1/market/all"
    coinname = requests.get(url)
    coinname = coinname.json()
    coinname_df = pd.DataFrame(coinname).set_index("market")
    coin_name = coinname_df.loc[ticker, "english_name"]
    return coin_name