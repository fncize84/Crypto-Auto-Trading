import pyupbit
import time
import datetime
import requests
from slacker import Slacker

access = "access"
secret = "secret"

myToken = "xoxb-2918010100544-2894323027731-UuwsGPLiFR3NA5x5O8L5m6o6"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_daily_ohlcv_from_base(ticker, base=12)
    target_price = df.iloc[-2]['close'] + (df.iloc[-2]['high'] - df.iloc[-2]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_daily_ohlcv_from_base(ticker, base=12)
    start_time = df.index[-1]
    return start_time

def get_ma5(ticker):
    """5일 이동 평균선 조회"""
    df = pyupbit.get_daily_ohlcv_from_base(ticker, base=12)
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    return ma5

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]


upbit = pyupbit.Upbit(access, secret)

ticker = ["KRW-BTC", "KRW-ETH", "KRW-XRP", "KRW-SAND", "KRW-WEMIX"]
k = 0.5

buy_amount = get_balance("KRW")/len(ticker)

print("autotrade start")
# 시작 메세지 슬랙 전송
post_message(myToken,"#stock-trading", "autotrade start")

자동매매 시작

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        buy_amount = get_balance("KRW")/len(ticker)

        if start_time < now < end_time - datetime.timedelta(seconds=30):
            for t in ticker:
                target_price = get_target_price(t, k)
                ma5 = get_ma5(t)
                current_price = get_current_price(t)
                balance = get_balance(t)

                print(balance)

                if balance == 0 and target_price < current_price and ma5 < current_price:
                    buy_result = upbit.buy_market_order(t, buy_amount*0.9995)
                    post_message(myToken,"#stock-trading", t + " buy : " +str(buy_result))

        else:
            for t in ticker:
                balance = get_balance(t)
                if balance > 0:
                    sell_result = upbit.sell_market_order(t, balance)
                    post_message(myToken,"#stock-trading", t + " sell : " +str(sell_result))
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#stock-trading", e)
        time.sleep(1)
