import pandas as pd
import pyupbit
import numpy as np

t = ["KRW-BTC", "KRW-ETH", "KRW-SOL", "KRW-SAND", "KRW-XRP", "KRW-BORA", "KRW-ATOM", "KRW-MATIC", "KRW-DOGE", "KRW-FLOW"]
k = 0.5
ma = 5
range = 1000
fee = 0.999

def back_test(ticker):
    df = pyupbit.get_ohlcv(ticker, period=1, interval="day", count=range)
    df['ma'] = df['close'].rolling(ma).mean()
    df['target'] = df['open'] + (df['high'].shift(1) - df['low'].shift(1)) * k
    df = df.iloc[(ma-1):]
    df['buy_price'] = np.where(df['ma']>df['target'],df['ma'],df['target'])
    df['fnl_ratio_fee'] = np.where(df['high'] > df['buy_price'], df['close']*fee/df['buy_price'], 1)    
    df['hpr_fee'] = df['fnl_ratio_fee'].cumprod()
    df['dd'] = (df['hpr_fee'].cummax() - df['hpr_fee']) / df['hpr_fee'].cummax() * 100
    df['trade_count'] = np.where(df['high'] > df['buy_price'],1,0)
    df['win_count'] = np.where(df['fnl_ratio_fee']>1,1,0)
    df['loss_count'] = np.where(df['fnl_ratio_fee']<1,1,0)
    df['f_amt'] = np.where(df['win_count'] ==1, df['close']-df['buy_price'],0)
    df['l_amt'] = np.where(df['loss_count'] ==1, df['close']-df['buy_price'],0)
    df['buy_and_hold'] = df['close']/df['open']
    df['bnh_hpr'] = df['buy_and_hold'].cumprod()

    bnh_return = (df['bnh_hpr'].iloc[-1]-1)*100
    total_return_fee = (df['hpr_fee'].iloc[-1]-1)*100
    cagr_fee = ((df['hpr_fee'].iloc[-1]/df['hpr_fee'].iloc[0])**(1/(len(df)/365))-1)*100
    mdd = df['dd'].max()

    trade_count = df['trade_count'].value_counts()[1] if 1 in df['trade_count'].value_counts() else 0
    win_count = df['win_count'].value_counts()[1] if 1 in df['win_count'].value_counts() else 0
    win_ratio = win_count/trade_count*100 if trade_count != 0 else 0

    avr_f = df['f_amt'].sum()/win_count if df['f_amt'].sum() != 0 else 0
    avr_l = -df['l_amt'].sum()/(trade_count-win_count) if df['l_amt'].sum() != 0 else 0
    fnl_ratio = avr_f/avr_l if avr_l != 0 else 0

    days = str(df.index[-1] - df.index[0])[:-8]
    test_result = [total_return_fee, bnh_return, cagr_fee, mdd, win_ratio, trade_count, fnl_ratio, days]

    return test_result

# print("Back Test Range : "+ str(df.index[0])[:10] + " ~ " + str(df.index[-1])[:10] + ",  " + str(df.index[-1] - df.index[0])[:-8])
# print("Total Return : {:0,.2f}%".format(total_return))
# print("CAGR : {:0,.2f}%".format(cagr))
# print("MDD: {:0,.2f}%".format(df['dd'].max()))
# print("Win Ratio : {:0,.2f}%".format(win_ratio) + "(" + str(win_count) + '/' + str(trade_count) + ')')
# print("FnL Ratio : {:0,.2f}".format(fnl_ratio))

col_name = ['Return with fee', 'Buy and Hold', 'CAGR_fee', 'MDD', 'Win Ratio', 'Trade Count', 'FnL Ratio', 'Test Range']
DF_test_result = pd.DataFrame(columns = col_name)

for t in t:
    DF_test_result.loc[t] = back_test(t)
#pd.set_option('display.max_columns', None)
print(DF_test_result)
