import pyupbit
import numpy as np

df = pyupbit.get_ohlcv("KRW-BTC", count=1000)

df['pclose'] = df['close'].shift(1)
df['diff1'] = abs(df['high'] - df['low'])
df['diff2'] = abs(df['pclose'] - df['high'])
df['diff3'] = abs(df['pclose'] - df['low'])
df['TR'] = df[['diff1', 'diff2', 'diff3']].max(axis=1)
df['ATR20'] = df['TR'].rolling(20).mean()
df = df.dropna()
data = np.array(df['ATR20'])    # no previous day's N 
for i in range(1, len(df)):
    data[i] = (19 * data[i-1] + df['TR'].iloc[i]) / 20
df['N'] = data

init_amt = 1000000
unit = init_amt*0.01/df['N'].iloc[-1]
buy_amt = unit * df['open'][-1]
stop_loss_price = df['open'][-1] - 2*df['N'].iloc[-1]
loss = 2*df['N'].iloc[-1] * unit
print("N : ", df['N'].iloc[-1])
print("unit : ", unit)
print("buy_amt : ",buy_amt)
print("stop loss : ", stop_loss_price)
print("loss : ", loss)

'''
1. N, Unit cal;
2. target price cal;
    if no balance
sys1 진입
1/2N 상승시 1unit 추가 매수 (최대 4unit)

'''

ticker = 'KRW-BTC'
def target_price_sys1(ticker):
    df = pyupbit.get_ohlcv(ticker, count=21)
    df = df.iloc[:-1]
    target_price = df['high'].max()
    return target_price

def target_price_sys2(ticker):
    df = pyupbit.get_ohlcv(ticker, count=56)
    df = df.iloc[:-1]
    target_price = df['high'].max()
    return target_price

def sell_price_sys1(ticker):
    df = pyupbit.get_ohlcv(ticker, count=11)
    df = df.iloc[:-1]
    sell_price = df['low'].min()
    return sell_price

def sell_price_sys2(ticker):
    df = pyupbit.get_ohlcv(ticker, count=21)
    df = df.iloc[:-1]
    sell_price = df['low'].min()
    return sell_price
