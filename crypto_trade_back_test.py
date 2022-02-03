import pandas as pd
import pyupbit
import numpy as np

t = ["KRW-BTC", "KRW-ETH"]
k = 0.5
ma = 5
range = 1000

def back_test(ticker):
    df = pyupbit.get_ohlcv(ticker, period=1, interval="day", count=range)
    df['ma'] = df['close'].rolling(ma).mean()
    df['target'] = df['open'] + (df['high'].shift(1) - df['low'].shift(1)) * k
    df = df.iloc[(ma-1):]
    df['buy_price'] = np.where(df['ma']>df['target'],df['ma'],df['target'])
    df['fnl_ratio'] = np.where(df['high'] > df['buy_price'], df['close']/df['buy_price'], 1)
    df['hpr'] = df['fnl_ratio'].cumprod()
    df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100
    df['trade_count'] = np.where(df['high'] > df['buy_price'],1,0)
    df['win_count'] = np.where(df['fnl_ratio']>1,1,0)
    df['loss_count'] = np.where(df['fnl_ratio']<1,1,0)
    df['f_amt'] = np.where(df['win_count'] ==1, df['close']-df['buy_price'],0)
    df['l_amt'] = np.where(df['loss_count'] ==1, df['close']-df['buy_price'],0)

    total_return = (df['hpr'].iloc[-1]-1)*100
    cagr = ((df['hpr'].iloc[-1]/df['hpr'].iloc[0])**(1/(len(df)/365))-1)*100
    mdd = df['dd'].max()
    try:
        trade_count = df['trade_count'].value_counts()[1]
    except Exception:
        trade_count = 0
    try:   
        win_count = df['win_count'].value_counts()[1]
    except Exception:
        win_count = 0
    try:   
        loss_count = df['loss_count'].value_counts()[1]
    except Exception:
        loss_count = 0
    
    win_ratio = win_count/trade_count*100

    if df['f_amt'].sum() != 0:
        avr_f = df['f_amt'].sum()/win_count
    else:
        avr_f = 0
    if df['l_amt'].sum() != 0:
        avr_l = -df['l_amt'].sum()/(trade_count-win_count)
    else:
        avr_l = 0
    try:
        fnl_ratio = avr_f/avr_l
    except Exception:
        fnl_ratio = 0

    test_result = [total_return, cagr, mdd, win_ratio, trade_count, win_count, loss_count, fnl_ratio]

    print("Back Test Range : "+ str(df.index[0])[:10] + " ~ " + str(df.index[-1])[:10] + ",  " + str(df.index[-1] - df.index[0])[:-8])

    return test_result

#print("Back Test Range : "+ str(df.index[0])[:10] + " ~ " + str(df.index[-1])[:10] + ",  " + str(df.index[-1] - df.index[0])[:-8])
# print("Total Return : {:0,.2f}%".format(total_return))
# print("CAGR : {:0,.2f}%".format(cagr))
# print("MDD: {:0,.2f}%".format(df['dd'].max()))
# print("Win Ratio : {:0,.2f}%".format(win_ratio) + "(" + str(win_count) + '/' + str(trade_count) + ')')
# print("FnL Ratio : {:0,.2f}".format(fnl_ratio))

col_name = ['Total Return', 'CAGR', 'MDD', 'Win Ratio', 'Trade Count', 'Win Count', 'Loss Count', 'FnL Ratio']
#DF_test_result = pd.DataFrame([back_test(t)], index = [t], columns = col_name)
DF_test_result = pd.DataFrame(columns = col_name)

for t in t:
    DF_test_result.loc[t] = back_test(t)

print(DF_test_result)
